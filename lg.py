import os
from pyrogram import Client, filters
from pyrogram.types import Message
import shutil

# BOT CONFIG
API_ID = 21011209
API_HASH = "7b8e5aeb45f1586354e0a486c2ff3aa1"
BOT_TOKEN = "7550922698:AAHkxNQzLOw6Brjiuids_kysMo1PICq13rY"

bot = Client("login_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

# Create a sessions folder if not exists
if not os.path.exists("sessions"):
    os.makedirs("sessions")

@bot.on_message(filters.private & filters.document)
async def handle_session_file(client, message: Message):
    doc = message.document
    if not doc.file_name.endswith(".session"):
        await message.reply("❌ Please upload a valid `.session` file.")
        return

    session_path = os.path.join("sessions", doc.file_name)
    await message.download(file_name=session_path)

    session_name = doc.file_name.replace(".session", "")
    try:
        user_client = Client(
            name=session_name,
            api_id=API_ID,
            api_hash=API_HASH,
            session_string=None,
            workdir="sessions"
        )

        await user_client.connect()
        me = await user_client.get_me()
        await user_client.send_message("me", "✅ This session is working and logged in from the bot.")
        await message.reply(f"✅ Logged in as @{me.username or 'No Username'}\n📱 Phone: +{me.phone_number}")
        await user_client.disconnect()

    except Exception as e:
        await message.reply(f"❌ Failed to login with session: {e}")
        # Optionally delete broken session
        os.remove(session_path)

bot.run()
