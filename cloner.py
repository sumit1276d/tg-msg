import asyncio
import os
import threading
from telethon import TelegramClient
from telethon.errors import FloodWaitError, ChannelPrivateError
from telethon.tl.functions.messages import ImportChatInviteRequest
from telegram import Update, Bot
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

# === CONFIG ===
api_id = 25494810
api_hash = '19c0e1aec617479077971013f88cc63f'
bot_token = '7992906581:AAFYGogkq9j4B4cZY750JCmuBmk5xN8_80w'
session_file = "main_clone.session"  # Single account for forwarding

bot = Bot(token=bot_token)
clone_semaphore = asyncio.Semaphore(1)  # One task at a time

# === BOT COMMANDS ===
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("✅ Use:\n/clone <source> <target>\nOnly public or joined groups/channels work.")

async def clone(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if len(context.args) != 2:
        await update.message.reply_text("❌ Usage:\n/clone <source_link> <target_link>")
        return

    source, target = context.args
    chat_id = update.effective_chat.id

    def run_clone():
        asyncio.run(forward_clone(source, target, chat_id))

    threading.Thread(target=run_clone).start()
    await update.message.reply_text("🔁 Forwarding started...")

# === FORWARD FUNCTION ===
async def forward_clone(source_link, target_link, chat_id):
    async with clone_semaphore:
        client = TelegramClient(session_file, api_id, api_hash)
        await client.start()

        try:
            for link in [source_link, target_link]:
                if "joinchat" in link or "+" in link:
                    try:
                        hash_code = link.split("+")[-1]
                        await client(ImportChatInviteRequest(hash_code))
                    except Exception as e:
                        await bot.send_message(chat_id, f"⚠️ Could not join: {link}\n{e}")

            source = await client.get_entity(source_link)
            target = await client.get_entity(target_link)

            count = 0
            failed = 0
            skipped = 0

            async for message in client.iter_messages(source, reverse=True):
                try:
                    await client.forward_messages(target, message.id, from_peer=source)
                    count += 1
                except Exception as e:
                    if "can't forward" in str(e).lower() or "forbidden" in str(e).lower():
                        try:
                            if message.media:
                                file_path = await message.download_media()
                                if file_path and os.path.exists(file_path):
                                    await client.send_file(target, file_path, caption=message.text or "")
                                    os.remove(file_path)
                                    count += 1
                                else:
                                    skipped += 1
                            elif message.text:
                                await client.send_message(target, message.text)
                                count += 1
                            else:
                                skipped += 1
                        except Exception as media_err:
                            print(f"⚠️ Manual upload failed: {media_err}")
                            failed += 1
                    else:
                        print(f"❌ Unknown error: {e}")
                        failed += 1

                if count % 25 == 0:
                    await bot.send_message(chat_id, f"📦 Sent {count} messages...")

                await asyncio.sleep(0.5)

            await bot.send_message(chat_id, f"✅ Done!\n📤 Total Sent: {count}\n❌ Failed: {failed}\n⏭️ Skipped Unsupported: {skipped}")

        except ChannelPrivateError:
            await bot.send_message(chat_id, "🚫 Error: One of the channels is private or not joined.")
        except Exception as e:
            await bot.send_message(chat_id, f"❌ Fatal error:\n{e}")
        finally:
            await client.disconnect()

# === MAIN ===
def main():
    print("🤖 Clone Bot Ready")
    print("Type `login` to authorize your account or press Enter to run the bot.")
    cmd = input("➤ ").strip().lower()

    if cmd == "login":
        with TelegramClient(session_file, api_id, api_hash) as client:
            client.loop.run_until_complete(client.get_me())
            print("✅ Logged in successfully!")
        return

    app = ApplicationBuilder().token(bot_token).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("clone", clone))
    print("🤖 Bot is running...")
    app.run_polling()

if __name__ == "__main__":
    main()
