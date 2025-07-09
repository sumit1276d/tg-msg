import os
import asyncio
import threading
from telethon import TelegramClient
from telethon.errors import SessionPasswordNeededError
from telethon.tl.functions.channels import CreateChannelRequest, InviteToChannelRequest, EditAdminRequest
from telethon.tl.functions.messages import EditChatAboutRequest
from telethon.tl.types import ChatAdminRights
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from telegram import Update, Bot

# === CONFIG ===
api_id = 25494810
api_hash = '19c0e1aec617479077971013f88cc63f'
bot_token = '7992906581:AAFYGogkq9j4B4cZY750JCmuBmk5xN8_80w'
session_folder = "sessions"
admin_username = 'venroxhub'
bio_text = "One-time payment, lifetime access"
bot = Bot(token=bot_token)

# === BOT COMMANDS ===
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("✅ Use:\n/multi_clone <source_channel> <count>")

async def multi_clone(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if len(context.args) != 2:
        await update.message.reply_text("❌ Usage:\n/multi_clone <source_channel> <count>")
        return
    source = context.args[0]
    count = int(context.args[1])
    chat_id = update.effective_chat.id
    threading.Thread(target=lambda: asyncio.run(clone_all(source, count, chat_id))).start()
    await update.message.reply_text("📡 Cloning started...")

# === Make admin with full rights ===
async def make_admin(client, channel, username):
    try:
        user = await client.get_entity(username)
        rights = ChatAdminRights(
            post_messages=True,
            edit_messages=True,
            delete_messages=True,
            ban_users=True,
            invite_users=True,
            pin_messages=True,
            add_admins=True,
            manage_call=True,
            anonymous=False,
            manage_chat=True
        )
        await client(EditAdminRequest(channel=channel, user_id=user, admin_rights=rights, rank="Admin"))
        return True
    except Exception as e:
        print(f"❌ Failed to promote admin: {e}")
        return False

# === CLONING FLOW ===
async def clone_all(source_link, count, chat_id):
    sessions = [f for f in os.listdir(session_folder) if f.endswith(".session")]
    if not sessions:
        bot.send_message(chat_id, "❌ No sessions found in 'sessions/' folder.")
        return

    for i in range(min(count, len(sessions))):
        session_path = os.path.join(session_folder, sessions[i])
        client = TelegramClient(session_path, api_id, api_hash)
        try:
            await client.start()
            source = await client.get_entity(source_link)
            new_title = f"{source.title} #{i+1}"

            # 1. Create channel
            result = await client(CreateChannelRequest(title=new_title, about="Clone", megagroup=False))
            new_channel = result.chats[0]
            await client(EditChatAboutRequest(peer=new_channel, about=bio_text))
            bot.send_message(chat_id, f"✅ Created: {new_title}")

            # 2. Promote admin with full rights
            admin_added = await make_admin(client, new_channel, admin_username)
            if admin_added:
                bot.send_message(chat_id, f"👑 Admin @{admin_username} promoted")
            else:
                bot.send_message(chat_id, f"⚠️ Could not promote @{admin_username}")

            # 3. Clone media
            await clone_messages(client, source, new_channel, chat_id)

        except Exception as e:
            bot.send_message(chat_id, f"❌ Error with session {sessions[i]}:\n{e}")
        finally:
            await client.disconnect()

# === CLONE MEDIA ===
async def clone_messages(client, source, target, chat_id):
    count = 0
    failed = 0
    skipped = 0
    async for message in client.iter_messages(source, reverse=True):
        try:
            await client.forward_messages(target, message.id, from_peer=source)
            count += 1
        except Exception:
            try:
                if message.media:
                    path = await message.download_media()
                    if path:
                        await client.send_file(target, path, caption=message.text or "")
                        os.remove(path)
                        count += 1
                    else:
                        skipped += 1
                elif message.text:
                    await client.send_message(target, message.text)
                    count += 1
                else:
                    skipped += 1
            except:
                failed += 1
        await asyncio.sleep(0.5)
        if count % 25 == 0:
            bot.send_message(chat_id, f"📤 Sent {count} messages...")

    bot.send_message(chat_id, f"✅ Done!\n📤 Sent: {count}\n❌ Failed: {failed}\n⏭️ Skipped: {skipped}")

# === LOGIN FLOW ===
async def login_account():
    phone = input("📱 Phone number (+countrycode): ").strip()
    session_path = os.path.join(session_folder, phone)
    client = TelegramClient(session_path, api_id, api_hash)
    await client.connect()
    if not await client.is_user_authorized():
        try:
            await client.send_code_request(phone)
            code = input("🔐 Enter OTP: ")
            try:
                await client.sign_in(phone, code)
            except SessionPasswordNeededError:
                pwd = input("🔒 Enter 2FA password: ")
                await client.sign_in(password=pwd)
            print("✅ Login successful.")
        except Exception as e:
            print(f"❌ Failed: {e}")
    await client.disconnect()

# === MAIN ===
def main():
    if not os.path.exists(session_folder):
        os.makedirs(session_folder)

    print("🤖 Ready. Type `login` to add new session or press Enter to run bot.")
    cmd = input("➤ ").strip().lower()
    if cmd == "login":
        asyncio.run(login_account())
        return

    app = ApplicationBuilder().token(bot_token).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("multi_clone", multi_clone))
    print("🤖 Bot running...")
    app.run_polling()

if __name__ == "__main__":
    main()
