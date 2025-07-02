from pyrogram import Client, filters
from pyrogram.types import Message, ChatPermissions
import zipfile
import os
import shutil
import asyncio

# Your credentials
API_ID = 25494810
API_HASH = "19c0e1aec617479077971013f88cc63f"
STRING_SESSION = "BQE2vQcAJQp6n_g5_zW5SfLdQluO7pGbh1VPOpAlH80NBHGY6eu47tw1_2apfLp343JA_Kwq2qTrp61oKm3hmn-rYd2Dvikax51K4YET7GbHIuk-6gev-32KWhT26jCAmMtOXCsrpbU1ZlgRBmAvZEyEGvraQVlqN0NVdoMSs9rCjV6bVhRdgELkBwyMloqg06Hv6hF2XQ-hC-icq9K1s7t-Ciiubaib6_UHreg3L7oowNwDv9XXZ3_Hs7JyVTrgaJHL6gpYQMbUZ9mEK1DLxc_ev6Q-usiZWxGGrKEJb6tGWdTr1RR9jOUjLK3yCBx_4ZfBg061saS4kqPhnzQxXwSDRcACnAAAAAHgAbHpAA"  # Replace this with your generated string session

app = Client("user_session", api_id=API_ID, api_hash=API_HASH, session_string=STRING_SESSION)

user_data = {}

def make_progress_bar(current, total, length=20):
    percent = int((current / total) * 100)
    filled = int(length * current // total)
    bar = "█" * filled + "-" * (length - filled)
    return f"[{bar}] {percent}%"

@app.on_message(filters.private & filters.command("start"))
async def start_handler(client, message: Message):
    await message.reply_text("👋 Send me a group name first.\n\nExample:\n`My Cool Group`", quote=True)
    user_data[message.from_user.id] = {"step": "awaiting_group_name"}

@app.on_message(filters.private & filters.text)
async def get_group_name(client, message: Message):
    user_id = message.from_user.id
    if user_id in user_data and user_data[user_id]["step"] == "awaiting_group_name":
        user_data[user_id]["group_name"] = message.text.strip()
        user_data[user_id]["step"] = "awaiting_zip"
        await message.reply_text("✅ Group name saved.\nNow send me a ZIP file with your videos.")

@app.on_message(filters.private & filters.document)
async def get_zip_file(client, message: Message):
    user_id = message.from_user.id
    if user_id not in user_data or user_data[user_id].get("step") != "awaiting_zip":
        await message.reply_text("❗ Please start with /start and send the group name first.")
        return

    zip_path = f"downloads/{user_id}.zip"
    extract_dir = f"downloads/extracted_{user_id}"
    os.makedirs("downloads", exist_ok=True)

    msg = await message.reply_text("⬇️ Downloading ZIP file...")

    try:
        await message.download(zip_path)
        await msg.edit("📦 Extracting ZIP...")
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(extract_dir)

        group_name = user_data[user_id]["group_name"]
        await msg.edit(f"📁 Creating private group: `{group_name}`")

        # Create the private supergroup
        result = await client.create_supergroup(group_name)
        group_id = result.id
        await asyncio.sleep(2)

        # Set minimal permissions (silent)
        await client.set_chat_permissions(group_id, ChatPermissions())

        # Generate invite link
        invite_link = await client.export_chat_invite_link(group_id)

        # Find video files in extracted folder
        video_files = [
            f for f in os.listdir(extract_dir)
            if f.lower().endswith(('.mp4', '.mkv', '.mov', '.avi'))
        ]
        total_files = len(video_files)
        if total_files == 0:
            await msg.edit("❗ No video files found in the ZIP.")
            return

        await msg.edit(f"📤 Uploading {total_files} video(s) to the group...")

        for idx, file_name in enumerate(video_files, 1):
            file_path = os.path.join(extract_dir, file_name)
            try:
                await client.send_video(group_id, file_path)
            except Exception as e:
                await message.reply_text(f"❌ Failed to upload {file_name}: {e}")
                continue
            progress_bar = make_progress_bar(idx, total_files)
            await msg.edit(f"📤 Uploading videos...\n{progress_bar}\n\n{idx}/{total_files} sent")

        await msg.edit("✅ All videos uploaded successfully!")
        await message.reply_text(f"🎉 Done! Here is your group link:\n{invite_link}")

    except Exception as e:
        await msg.edit(f"❌ Error: {e}")

    finally:
        if os.path.exists(zip_path):
            os.remove(zip_path)
        if os.path.exists(extract_dir):
            shutil.rmtree(extract_dir)
        user_data.pop(user_id, None)

app.run()
