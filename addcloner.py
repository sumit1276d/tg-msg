import asyncio
import os
import threading
from telethon import TelegramClient
from telethon.errors import FloodWaitError
from telethon.tl.functions.channels import CreateChannelRequest
from telegram.ext import Updater, CommandHandler
import telegram

# === CONFIG ===
api_id = 25494810
api_hash = '19c0e1aec617479077971013f88cc63f'
bot_token = '7579631970:AAEChY5HC9RHoTK4rRRLxgHfvh-exac-3b8'
session_file = "main_clone.session"

bot = telegram.Bot(token=bot_token)
clone_semaphore = asyncio.Semaphore(1)

# === BOT COMMANDS ===
def start(update, context):
    update.message.reply_text("✅ Use:\n/clone <source> <target>\n/multi_clone <source> <target1> <target2> ...\n/multi_clone <source> <count>\n/clone_addlist <ignored_link_but_clones_3_recent_channels>")

def clone(update, context):
    if len(context.args) != 2:
        return update.message.reply_text("❌ Usage:\n/clone <source_link> <target_link>")
    source, target = context.args
    chat_id = update.effective_chat.id
    update.message.reply_text("🔁 Forwarding started...")
    threading.Thread(target=lambda: asyncio.run(forward_clone(source, target, chat_id))).start()

def multi_clone(update, context):
    if len(context.args) < 2:
        return update.message.reply_text("❌ Usage:\n/multi_clone <source> <target1> <target2> ...\nOr: /multi_clone <source> <count>")
    source = context.args[0]
    second_arg = context.args[1]
    chat_id = update.effective_chat.id
    if second_arg.isdigit():
        count = int(second_arg)
        update.message.reply_text(f"🚀 Cloning `{source}` into {count} new channels...")
        threading.Thread(target=lambda: asyncio.run(auto_multi_clone(source, count, chat_id))).start()
    else:
        targets = context.args[1:]
        update.message.reply_text("🔁 Multi-clone started...")
        threading.Thread(target=lambda: asyncio.run(multi_forward_clone(source, targets, chat_id))).start()

def clone_addlist(update, context):
    update.message.reply_text("🔁 Cloning last 3 joined channels...")
    chat_id = update.effective_chat.id
    threading.Thread(target=lambda: asyncio.run(clone_last_joined_channels(chat_id))).start()

# === CLONE LAST JOINED CHANNELS ===
async def clone_last_joined_channels(chat_id):
    async with clone_semaphore:
        client = TelegramClient(session_file, api_id, api_hash)
        await client.start()
        try:
            dialogs = [d async for d in client.iter_dialogs() if d.is_channel and not d.entity.broadcast]
            recent_channels = dialogs[:3]  # Last 3 joined
            for d in recent_channels:
                source = d.entity
                source_title = source.title or "Cloned Channel"
                result = await client(CreateChannelRequest(title=source_title, about="Cloned from recent join", megagroup=False))
                new_channel = result.chats[0]
                bot.send_message(chat_id, f"📦 Created new channel: {source_title}")
                await clone_messages(client, source, new_channel, chat_id)
        except Exception as e:
            bot.send_message(chat_id, f"❌ Fatal error: {e}")
        finally:
            await client.disconnect()

# === AUTO MULTI CLONE ===
async def auto_multi_clone(source_link, count, chat_id):
    async with clone_semaphore:
        client = TelegramClient(session_file, api_id, api_hash)
        await client.start()
        try:
            source = await client.get_entity(source_link)
            source_name = source.title or "ClonedChannel"
            targets = []
            for i in range(1, count + 1):
                try:
                    new_title = f"{source_name} #{i}"
                    result = await client(CreateChannelRequest(title=new_title, about="Cloned content", megagroup=False))
                    targets.append(result.chats[0])
                    await asyncio.sleep(1)
                except Exception as e:
                    bot.send_message(chat_id, f"❌ Failed to create channel #{i}: {e}")
            await multi_forward_clone(source_link, targets, chat_id)
        except Exception as e:
            bot.send_message(chat_id, f"❌ Error: {e}")
        finally:
            await client.disconnect()

# === MULTI FORWARD FUNCTION ===
async def multi_forward_clone(source_link, target_entities, chat_id):
    async with clone_semaphore:
        client = TelegramClient(session_file, api_id, api_hash)
        await client.start()
        try:
            if isinstance(target_entities[0], str):
                targets = [await client.get_entity(t) for t in target_entities]
            else:
                targets = target_entities
            source = await client.get_entity(source_link)
            await clone_messages(client, source, targets, chat_id)
        except Exception as e:
            bot.send_message(chat_id, f"❌ Fatal error: {e}")
        finally:
            await client.disconnect()

# === SINGLE FORWARD FUNCTION ===
async def forward_clone(source_link, target_link, chat_id):
    async with clone_semaphore:
        client = TelegramClient(session_file, api_id, api_hash)
        await client.start()
        try:
            source = await client.get_entity(source_link)
            target = await client.get_entity(target_link)
            await clone_messages(client, source, target, chat_id)
        except Exception as e:
            bot.send_message(chat_id, f"❌ Fatal error: {e}")
        finally:
            await client.disconnect()

# === CLONE LOGIC ===
async def clone_messages(client, source, targets, chat_id):
    if not isinstance(targets, list):
        targets = [targets]
    count = 0
    failed = 0
    skipped = 0
    async for message in client.iter_messages(source, reverse=True):
        for target in targets:
            try:
                await client.forward_messages(target, message.id, from_peer=source)
            except Exception as e:
                if "can't forward" in str(e).lower() or "forbidden" in str(e).lower():
                    try:
                        if message.media:
                            file_path = await message.download_media()
                            if file_path and os.path.exists(file_path):
                                await client.send_file(target, file_path, caption=message.text or "")
                                os.remove(file_path)
                            else:
                                skipped += 1
                        elif message.text:
                            await client.send_message(target, message.text)
                        else:
                            skipped += 1
                    except Exception:
                        failed += 1
                else:
                    failed += 1
            await asyncio.sleep(0.5)
        count += 1
        if count % 25 == 0:
            bot.send_message(chat_id, f"📤 {count} messages sent...")
    bot.send_message(chat_id, f"✅ Done!\n📤 Sent: {count}\n❌ Failed: {failed}\n⏭️ Skipped: {skipped}")

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
    dp.add_handler(CommandHandler("multi_clone", multi_clone))
    dp.add_handler(CommandHandler("clone_addlist", clone_addlist))
    print("🤖 Bot is running...")
    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()
