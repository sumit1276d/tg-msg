import asyncio
import os
import threading
from telethon import TelegramClient
from telethon.errors import FloodWaitError, ChannelPrivateError
from telethon.tl.functions.messages import ImportChatInviteRequest
from telegram.ext import Updater, CommandHandler
import telegram

# === CONFIG ===
api_id = 25494810
api_hash = '19c0e1aec617479077971013f88cc63f'
bot_token = '7992906581:AAFYGogkq9j4B4cZY750JCmuBmk5xN8_80w'
session_file = "main_clone.session"  # Single account for forwarding

bot = telegram.Bot(token=bot_token)
clone_semaphore = asyncio.Semaphore(1)  # One task at a time

# === BOT COMMANDS ===
def start(update, context):
    update.message.reply_text("✅ Use:\n/clone <source> <target>\nOnly public or joined groups/channels work.")

def clone(update, context):
    if len(context.args) != 2:
        return update.message.reply_text("❌ Usage:\n/clone <source_link> <target_link>")

    source, target = context.args
    chat_id = update.effective_chat.id

    threading.Thread(target=lambda: asyncio.run(forward_clone(source, target, chat_id))).start()
    update.message.reply_text("🔁 Forwarding started...")

# === FORWARD FUNCTION ===
async def forward_clone(source_link, target_link, chat_id):
    async with clone_semaphore:
        client = TelegramClient(session_file, api_id, api_hash)
        await client.start()

        try:
            # Join groups if needed
            for link in [source_link, target_link]:
                if "joinchat" in link or "+" in link:
                    try:
                        hash_code = link.split("+")[-1]
                        await client(ImportChatInviteRequest(hash_code))
                    except Exception as e:
                        bot.send_message(chat_id, f"⚠️ Could not join: {link}\n{e}")

            source = await client.get_entity(source_link)
            target = await client.get_entity(target_link)

            count = 0
            failed = 0
            skipped = 0

            async for message in client.iter_messages(source, reverse=True):
                try:
                    # Try forwarding
                    await client.forward_messages(target, message.id, from_peer=source)
                    count += 1
                except Exception as e:
                    if "can't forward" in str(e).lower() or "forbidden" in str(e).lower():
                        # Try manual upload
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
                    bot.send_message(chat_id, f"📦 Sent {count} messages...")

                await asyncio.sleep(0.5)

            bot.send_message(chat_id, f"✅ Done!\n📤 Total Sent: {count}\n❌ Failed: {failed}\n⏭️ Skipped Unsupported: {skipped}")

        except ChannelPrivateError:
            bot.send_message(chat_id, "🚫 Error: One of the channels is private or not joined.")
        except Exception as e:
            bot.send_message(chat_id, f"❌ Fatal error:\n{e}")
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

    updater = Updater(bot_token, use_context=True)
    dp = updater.dispatcher
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("clone", clone))

    print("🤖 Bot is running...")
    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()
