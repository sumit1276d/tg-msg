from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, ChatMemberUpdated
from pyrogram.enums import ChatMemberStatus
import asyncio
import re
from time import time

API_ID = 22046466
API_HASH = "e28a9150403458514e9469cdbb1d54d1"
BOT_TOKEN = "7894616680:AAF40zOmeD2EPALHv1EtzvmLInkF4R3GpV0"

bot = Client("fomo_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

group_links = {}       # Stores group invite links
last_message = {}      # Stores last pinned FOMO message per group
processed_leaves = {}  # Tracks users who left recently
active_groups = set()  # Active groups with FOMO scheduler

# --- Permissions ---
async def is_admin(chat_id, user_id):
    try:
        member = await bot.get_chat_member(chat_id, user_id)
        return member.status in [ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER]
    except:
        return False

async def has_bot_permissions(chat_id):
    try:
        me = await bot.get_me()
        member = await bot.get_chat_member(chat_id, me.id)
        privs = member.privileges
        return all([privs.can_pin_messages, privs.can_delete_messages, privs.can_manage_chat]) if privs else False
    except:
        return False

# --- Send FOMO message every hour ---
async def send_fomo_message(chat_id):
    if chat_id not in group_links:
        return False
    link = group_links[chat_id]
    fomo_text = "👋 Share this 1 TIME TO Get Unlimited videos"
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("📤 Share [0/1]", url=link)],
        [InlineKeyboardButton("🔓 Open Group", callback_data="fomo_info")]
    ])
    try:
        if chat_id in last_message:
            await bot.unpin_chat_message(chat_id, last_message[chat_id])
            await bot.delete_messages(chat_id, last_message[chat_id])
        msg = await bot.send_message(chat_id, fomo_text, reply_markup=keyboard)
        await bot.pin_chat_message(chat_id, msg.id, disable_notification=True)
        last_message[chat_id] = msg.id
        return True
    except Exception as e:
        print(f"Send error: {e}")
        return False

# --- Scheduler (1 hour loop) ---
async def fomo_scheduler():
    while True:
        try:
            for chat_id in list(active_groups):
                await send_fomo_message(chat_id)
                await asyncio.sleep(1)
            await asyncio.sleep(3600)  # Wait 1 hour
        except Exception as e:
            print(f"Scheduler error: {e}")
            await asyncio.sleep(60)

# --- Admin Commands ---
@bot.on_message(filters.command("init") & filters.private)
async def init_scheduler(client, message):
    asyncio.create_task(fomo_scheduler())
    await message.reply("✅ FOMO scheduler started!")

@bot.on_message(filters.command("settings") & filters.group)
async def set_group_link(client, message: Message):
    if not message.from_user or not await is_admin(message.chat.id, message.from_user.id):
        return await message.reply("🚫 Only admins can use this.")
    if len(message.command) < 2:
        return await message.reply("❌ Usage:\n/settings https://t.me/+abc123")
    input_link = message.command[1]
    match = re.search(r"(?:\+|joinchat/)([a-zA-Z0-9_-]+)", input_link)
    if not match:
        return await message.reply("❌ Invalid link.")
    code = match.group(1)
    share_link = f"https://t.me/share/url?url=https://t.me/joinchat/{code}"
    group_links[message.chat.id] = share_link
    await message.reply(f"✅ Invite link saved:\n{share_link}")

@bot.on_message(filters.command("start") & filters.group)
async def start_fomo(client, message: Message):
    if not message.from_user or not await is_admin(message.chat.id, message.from_user.id):
        return await message.reply("🚫 Only admins can use this.")
    if message.chat.id not in group_links:
        return await message.reply("❗ Use /settings to set invite link first.")
    if not await has_bot_permissions(message.chat.id):
        return await message.reply("❌ Bot needs pin, delete, manage chat rights.")
    active_groups.add(message.chat.id)
    await send_fomo_message(message.chat.id)
    await message.reply("✅ FOMO will post every 1 hour.")

@bot.on_message(filters.command("stop") & filters.group)
async def stop_fomo(client, message: Message):
    if not message.from_user or not await is_admin(message.chat.id, message.from_user.id):
        return await message.reply("🚫 Only admins can use this.")
    chat_id = message.chat.id
    if chat_id in active_groups:
        active_groups.remove(chat_id)
        if chat_id in last_message:
            try:
                await bot.unpin_chat_message(chat_id, last_message[chat_id])
                await bot.delete_messages(chat_id, last_message[chat_id])
                del last_message[chat_id]
            except Exception as e:
                print(f"Cleanup error: {e}")
        await message.reply("✅ Stopped FOMO in this group.")
    else:
        await message.reply("❌ FOMO wasn’t active in this group.")

# --- Button Popup ---
@bot.on_callback_query(filters.regex("fomo_info"))
async def fomo_popup(client, callback_query):
    await callback_query.answer("Please forward this message to 3 groups to unlock!", show_alert=True)

# --- Welcome message (custom + clean) ---
@bot.on_message(filters.new_chat_members & filters.group)
async def handle_join(client, message: Message):
    try:
        chat_id = message.chat.id
        if chat_id not in group_links:
            return await client.delete_messages(chat_id, message.id)
        link = group_links[chat_id]
        welcome_text = "👋 Welcome! Share this 1 TIME TO Get Unlimited videos"
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("📤 Share [1/3]", url=link)],
            [InlineKeyboardButton("🔓 Open Group", callback_data="fomo_info")]
        ])
        if chat_id in last_message:
            try:
                await client.unpin_chat_message(chat_id, last_message[chat_id])
                await client.delete_messages(chat_id, last_message[chat_id])
            except:
                pass
        msg = await client.send_message(chat_id, welcome_text, reply_markup=keyboard)
        await client.pin_chat_message(chat_id, msg.id, disable_notification=True)
        last_message[chat_id] = msg.id
        await client.delete_messages(chat_id, message.id)
    except Exception as e:
        print(f"Join error: {e}")

# --- Leave cleanup + fake unlock msg ---
@bot.on_message(filters.left_chat_member & filters.group)
async def handle_leave(client, message: Message):
    try:
        await client.delete_messages(message.chat.id, message.id)
    except:
        pass

@bot.on_chat_member_updated()
async def user_left_handler(client, event: ChatMemberUpdated):
    try:
        new_status = event.new_chat_member.status if event.new_chat_member else None
        user = event.from_user
        if not user or new_status != ChatMemberStatus.LEFT:
            return
        event_key = f"{event.chat.id}:{user.id}"
        current_time = time()
        if event_key in processed_leaves and current_time - processed_leaves[event_key] < 300:
            return
        processed_leaves[event_key] = current_time
        await client.send_message(event.chat.id, f"✅ {user.first_name} unlocked the group!")
    except:
        pass

print("Starting bot...")
bot.run()
