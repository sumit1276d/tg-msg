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
media_source = 'ttps://t.me/+15kZMlIeH7ZkY2Y1'  # <-- Replace with your media group/channel username or ID
text_message =  "✅ 𝗣𝗿𝗲𝗺𝗶𝘂𝗺 𝗰𝗼𝗹𝗹𝗲𝗰𝘁𝗶𝗼𝗻 𝗳𝗼𝗿 𝗽𝗿𝗲𝗺𝗶𝘂𝗺 𝗰𝘂𝘀𝘁𝗼𝗺𝗲𝗿𝘀 ✅\n"
    "✅ 𝗔𝗹𝗹 𝗽𝗮𝗶𝗱, 𝗦𝗲𝗹𝗲𝗰𝘁 𝗮𝗻𝗱 𝗯𝘂𝘆 ✅\n\n"

    "✅𝟭. 𝗠𝗼𝗺 𝘀𝗼𝗻 ( 𝟰,𝟯𝟬𝟬+ 𝘃𝗶𝗱𝗲𝗼𝘀 ✅️)\n"
    "🍓𝟮. 𝗦𝗶𝘀 𝗯𝗿𝗼 ( 𝟰,𝟬𝟬𝟬+ 𝘃𝗶𝗱𝗲𝗼𝘀 ✅️ )\n"
    "🍆𝟯. 𝗖𝗽 𝗸!𝗱𝘀 ( 𝟱𝟬,𝟬𝟬𝟬+ 𝘃𝗶𝗱𝗲𝗼𝘀 ✅️)\n"
    "✅𝟰. 𝗗𝗮𝗱 𝗱𝗮𝘂𝗴𝗵𝘁𝗲𝗿 ( 𝟰,𝟬𝟬𝟬+  𝘃𝗶𝗱𝗲𝗼𝘀 ✅️)\n"
    "⭐️𝟱. 𝗥@𝗽𝗲 & 𝗳𝗼𝗿𝗰𝗲 ( 𝟱𝟬𝟬𝟬+ 𝘃𝗶𝗱𝗲𝗼𝘀 ✅️ )\n"
    "🍑𝟲. 𝗧𝗲𝗲𝗻 ( 𝟭𝟬,𝟬𝟬𝟬+ 𝘃𝗶𝗱𝗲𝗼𝘀 ✅️)\n"
    "✅𝟯. 𝗨𝘀𝗮 𝗖𝗣  ( 𝟭,𝟲𝟬𝟬+ 𝘃𝗶𝗱𝗲𝗼𝘀 ✅️)\n"
    "🍓𝟴. 𝗛𝗶𝗱𝗱𝗲𝗻 𝗰𝗮𝗺 ( 𝟰,𝟬𝟬𝟬+ 𝘃𝗶𝗱𝗲𝗼𝘀 ✅️)\n"
    "🍆𝟵. 𝗦𝗻𝗮𝗽 𝗶𝗻𝘀𝘁𝗮 𝗹𝗲𝗮𝗸 ( 𝟱𝟬𝟬𝟬+ 𝘃𝗶𝗱𝗲𝗼𝘀 ✅️)\n"
    "✅𝟭𝟬. 𝗝𝗮𝗽𝗮𝗻𝗲𝘀𝗲 ( 𝟱𝟬𝟬𝟬+ 𝘃𝗶𝗱𝗲𝗼𝘀 ✅️)\n"
    "⭐️𝟭𝟭. 𝗕𝗹𝗮𝗰𝗸 𝘁𝗲𝗲𝗻 𝘃𝗶𝗱𝗲𝗼𝘀 ( 𝟭𝟬𝟬𝟬+ 𝘃𝗶𝗱�_e𝗼𝘀 ✅️)\n"
    "🏃‍♂️𝟭𝟮. 𝗢𝗻𝗹𝘆 𝗳𝗮𝗻 ( 𝟭𝟬𝟬𝟬𝟬+ ✅️)\n"
    "🍑𝟭𝟯. 𝗟𝗲𝗮𝗸𝘀 ( 𝟭𝟬𝟬𝟬𝟬+ 𝘃𝗶𝗱𝗲𝗼𝘀 ✅️ )\n"
    "🍆 𝟭𝟰. 𝗔𝗻𝗶𝗺𝗮𝗹𝘀 𝘄𝗶𝘁𝗵 𝗴𝗶𝗿𝗹𝘀 ( 𝟮𝟱𝟬𝟬+ 𝘃𝗶𝗱𝗲𝗼𝘀 ✅️)\n"
    "🍓 𝟭𝟱. 𝗣𝘂𝗯𝗹𝗶𝗰 𝗮𝗴𝗲𝗻𝘁𝘀 ( 𝟭𝟰𝟬𝟬+ 𝘃𝗶𝗱𝗲𝗼𝘀 ✅️)\n"
    "🔥 𝟭𝟲. 𝗚𝗮𝘆 𝗖𝗣 ( 𝟭𝟬,𝟬𝟬𝟬+ 𝘃𝗶𝗱𝗲𝗼𝘀 ✅️) \n"
    "🥵 𝟭𝟳. 𝗧𝗮𝗺𝗶𝗹, 𝗠𝗮𝗹𝗹𝘂 ( 𝟭𝟬𝟬𝟬𝟬+ 𝘃𝗶𝗱𝗲𝗼𝘀 ✅)\n"
    "😍 𝟭𝟴. 𝗚𝗶𝗿𝗹𝘀 𝗻𝘂𝗱𝗲 𝗽𝗶𝗰𝘀 ( 𝟭𝟬𝟬𝗞 𝗣𝗵𝗼𝘁𝗼𝘀 ✅)\n"
    "🍑 𝟭𝟵. 𝗗𝗿𝘂𝗴𝗴𝗲𝗱  𝗴𝗶𝗿𝗹 𝗳#𝗰𝗸 ( 𝟲𝟱𝟬𝟬+ 𝘃𝗶𝗱𝗲𝗼𝘀 ✅ )\n"
    "🔥 𝟮𝟭. 𝗚𝗶𝗿𝗹𝘀 𝗕𝗹𝗮𝗰𝗸 𝗺𝗮𝗶𝗹 ( 𝟰𝟬𝟬𝟬+ 𝘃𝗶𝗱𝗲𝗼𝘀 ✅)\n"
    "🤤 𝟮𝟮. 𝗜𝗻𝗱𝗶𝗮𝗻 𝗗𝗲𝘀𝗶 ( 𝟯𝟬,𝟬𝟬𝟬+ 𝗩𝗶𝗱𝗲𝗼𝘀 ✅ )\n"
    "🤩 𝟮𝟯. 𝗢𝗹𝗱 𝗮𝗴𝗲 𝗚𝗿𝗮𝗻𝗻𝘆 𝗦#𝘅 ( 𝟰𝟬𝟬𝟬+ 𝗩𝗶𝗱𝗲𝗼𝘀 ✅ )\n"
    "🔞 𝟮𝟰. 𝗦𝗰𝗵𝗼𝗼𝗹 𝗚𝗶𝗿𝗹𝘀 ( 𝟮,𝟬𝟬𝟬+ 𝗩𝗶𝗱𝗲𝗼𝘀 ✅ )\n"
    "🥵 𝟮𝟱. 𝗖𝗵𝗶𝗻𝗲𝘀𝗲 𝗧𝗲𝗲𝗻 ( 𝟴,𝟬𝟬𝟬+ 𝗩𝗶𝗱𝗲𝗼𝘀 ✅ )\n"
    "🔥 𝟮𝟲. 𝗦𝗻𝗮𝗽𝗴𝗼𝗱 ( 𝟱𝟬,𝟬𝟬𝟬+ 𝗩𝗶𝗱𝗲𝗼𝘀 ✅ )\n"
    "🌟 𝟮𝟳. 𝗕𝗗𝗠𝗦 ( 𝟭,𝟬𝟬𝟬+ 𝗩𝗶𝗱𝗲𝗼𝘀 ✅ )\n"
    "😍 𝟮𝟴. 𝗣𝗲𝗲 & 𝗦𝗰𝗮𝘁 ( 𝟭,𝟬𝟬𝟬+ 𝗩𝗶𝗱𝗲𝗼𝘀 ✅ )\n"
    "🤤 𝟮𝟵. 𝗦𝗵𝗲𝗺𝗮𝗹𝗲 ( 𝟮,𝟬𝟬𝟬+ 𝗩𝗶𝗱𝗲𝗼𝘀 ✅ )\n"
    "❤️ 𝟮9. 𝗔𝗹𝗹 𝗩𝗜𝗗𝗘𝗢𝗦 𝗚𝗥𝗢𝗨𝗣𝗦 + �_M𝗘𝗚𝗔 𝗟𝗜𝗡𝗞𝗦 ( 𝟮,𝟬𝟬𝟬𝟬𝟬 + 𝗩𝗶𝗱𝗲𝗼𝘀 ✅ )\n\n"
    "📩 𝗗𝗺 𝗳𝗼𝗿 𝗯𝘂𝘆 𝗮𝗻𝗱 𝗳𝘂𝗹𝗹 𝗱𝗲𝘁𝗮𝗶𝗹𝘀 ✅\n" # <-- Your message

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
