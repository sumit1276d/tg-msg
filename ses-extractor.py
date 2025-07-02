import os
import re
import zipfile
import asyncio
import uuid
from telethon import TelegramClient, events
from pyrogram import Client, filters
from pyrogram.types import Message

# Configuration
API_ID = 26220159
API_HASH = "8d30aa8f87a69e1531fd8a5974d7d2a0"
BOT_TOKEN = "YOUR_BOT_TOKEN"
SESSION_DIR = "sessions"
os.makedirs(SESSION_DIR, exist_ok=True)

# Pyrogram bot
bot = Client("otp_zip_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

@bot.on_message(filters.document & filters.private)
async def handle_zip_file(client: Client, message: Message):
    file = message.document

    if not file.file_name.endswith(".zip"):
        await message.reply("❌ Please send a valid `.zip` file containing `.session` files.")
        return

    # Unique directory for this user
    user_dir = os.path.join(SESSION_DIR, f"{message.from_user.id}_{uuid.uuid4().hex}")
    os.makedirs(user_dir, exist_ok=True)

    # Download and extract
    zip_path = os.path.join(user_dir, file.file_name)
    await message.download(file_name=zip_path)

    try:
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(user_dir)
    except Exception as e:
        await message.reply(f"❌ Failed to extract ZIP: {e}")
        return

    session_files = [f for f in os.listdir(user_dir) if f.endswith(".session")]
    if not session_files:
        await message.reply("❌ No valid `.session` files found in the ZIP.")
        return

    await message.reply(f"✅ Found {len(session_files)} session files. Listening for OTPs...")

    # Launch OTP extractors
    for sess in session_files:
        path = os.path.join(user_dir, sess)
        asyncio.create_task(start_otp_listener(path, message.from_user.id))

async def start_otp_listener(session_path, user_id):
    try:
        client = TelegramClient(session_path[:-8], API_ID, API_HASH)
        await client.start()

        @client.on(events.NewMessage)
        async def otp_handler(event):
            text = event.raw_text
            match = re.search(r"(?:Login code|Code):?\s?(\d{5})", text)
            if match:
                otp = match.group(1)
                await bot.send_message(
                    user_id,
                    f"🔐 OTP from <code>{os.path.basename(session_path)}</code>: <b>{otp}</b>",
                    parse_mode="html"
                )
                await client.disconnect()

        await client.run_until_disconnected()

    except Exception as e:
        await bot.send_message(user_id, f"❌ Error with {os.path.basename(session_path)}: {e}")
        if os.path.exists(session_path):
            os.remove(session_path)

if __name__ == "__main__":
    print("🤖 OTP Extractor Bot Running...")
    bot.run()
