import os
import asyncio
import threading
from telethon import TelegramClient
from telethon.tl.functions.messages import CreateChatRequest, EditChatAboutRequest
from telethon.tl.functions.channels import EditAdminRequest, EditBannedRequest, InviteToChannelRequest
from telethon.tl.types import ChatAdminRights, ChatBannedRights
from telegram import Update, Bot
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

# === CONFIG ===
api_id = 25494810
api_hash = '19c0e1aec617479077971013f88cc63f'
bot_token = '7992906581:AAFYGogkq9j4B4cZY750JCmuBmk5xN8_80w'
session_folder = 'sessions'
admin_username = 'venroxhub'
joinhider = 'joinhiderrobot'
bio_text = "One-time payment, lifetime access"
media_source = 'https://t.me/YOUR_MEDIA_SOURCE'  # <-- Replace with your media group/channel username or ID
text_message = "🔥 Welcome to the Premium Vault!\n\nLifetime access granted. Enjoy the leaks!"  # <-- Your message

bot = Bot(token=bot_token)

# === BOT COMMANDS ===
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("✅ Use:\n/clone <count>")

async def clone_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if len(context.args) != 1 or not context.args[0].isdigit():
        await update.message.reply_text("❌ Usage:\n/clone <count>")
        return
    count = int(context.args[0])
    chat_id = update.effective_chat.id
    threading.Thread(target=lambda: asyncio.run(clone_groups(count, chat_id))).start()
    await update.message.reply_text(f"📡 Creating {count} groups...")

# === CLONE FUNCTION ===
async def clone_groups(count, chat_id):
    sessions = [f for f in os.listdir(session_folder) if f.endswith(".session")]
    if not sessions:
        bot.send_message(chat_id, "❌ No sessions found in 'sessions/' folder.")
        return

    for i in range(min(count, len(sessions))):
        session_path = os.path.join(session_folder, sessions[i])
        client = TelegramClient(session_path, api_id, api_hash)
        try:
            await client.start()
            group_name = f"Premium Vault #{i+1}"
            result = await client(CreateChatRequest(users=[], title=group_name))
            group = result.chats[0]

            # Make @venroxhub admin with full rights
            user = await client.get_entity(admin_username)
            rights = ChatAdminRights(
                post_messages=True, edit_messages=True, delete_messages=True,
                ban_users=True, invite_users=True, pin_messages=True,
                add_admins=True, manage_call=True, anonymous=False, manage_chat=True
            )
            await client(EditAdminRequest(channel=group, user_id=user, admin_rights=rights, rank="Admin"))

            # Restrict all members (read-only)
            banned_rights = ChatBannedRights(
                until_date=None, view_messages=False, send_messages=True,
                send_media=True, send_stickers=True, send_gifs=True,
                send_games=True, send_inline=True, embed_links=True
            )
            await client(EditBannedRequest(channel=group, participant="all", banned_rights=banned_rights))

            # Add @joinhiderrobot
            try:
                bot_user = await client.get_entity(joinhider)
                await client(InviteToChannelRequest(channel=group, users=[bot_user]))
            except Exception as e:
                print(f"⚠️ Could not add joinhider: {e}")

            # Set group description
            await client(EditChatAboutRequest(peer=group, about=bio_text))

            # Post text message
            await client.send_message(group.id, text_message)

            # Post media from media_source
            source = await client.get_entity(media_source)
            async for message in client.iter_messages(source, reverse=True):
                if message.media:
                    try:
                        await client.forward_messages(group.id, message.id, source)
                        await asyncio.sleep(0.5)
                    except:
                        pass

            bot.send_message(chat_id, f"✅ Group created: {group.title}")

        except Exception as e:
            bot.send_message(chat_id, f"❌ Error in session {sessions[i]}:\n{e}")
        finally:
            await client.disconnect()

# === LOGIN TOOL ===
async def login_account():
    phone = input("📱 Phone number (+countrycode): ").strip()
    session_path = os.path.join(session_folder, phone)
    client = TelegramClient(session_path, api_id, api_hash)
    await client.connect()
    if not await client.is_user_authorized():
        try:
            await client.send_code_request(phone)
            code = input("🔐 Enter OTP: ")
            await client.sign_in(phone, code)
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
    app.add_handler(CommandHandler("clone", clone_handler))
    print("🤖 Bot running...")
    app.run_polling()

if __name__ == "__main__":
    main()
