from pyrogram import Client, filters
from pyrogram.types import Message
from pyrogram.enums import ChatMemberStatus
from pyrogram.errors import FloodWait
import asyncio

API_ID = 26922037
API_HASH = "e9e91ff6b1633fdf7d1de2a8d09ef492"
BOT_TOKEN = "7683046404:AAFAU99Z65IOLVcJvbLJj60QFpo9P1hN8E8"
OWNER_ID = 7679771797    # Replace with your Telegram user ID

bot = Client("join_hider_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

managed_groups = set()  # Stores managed group IDs

# Handle rate limits
async def safe_execute(coro):
    try:
        return await coro
    except FloodWait as e:
        print(f"FloodWait: Sleeping for {e.value} seconds")
        await asyncio.sleep(e.value + 1)
        return await coro
    except Exception as e:
        print(f"Error: {e}")
        await log_to_group(None, f"Error: {e}")
        return None

# Log to group chat anonymously
async def log_to_group(chat_id, message):
    if not chat_id:
        return
    try:
        msg = await safe_execute(bot.send_message(
            chat_id,
            f"[Log] {message}",
            disable_notification=True
        ))
        if msg:
            await asyncio.sleep(5)  # Brief visibility
            await safe_execute(bot.delete_messages(chat_id, msg.id))
    except Exception as e:
        print(f"Failed to log to group: {e}")

# Check if user is owner
async def is_owner(user_id):
    return user_id == OWNER_ID

# Check if bot is admin with delete permission
async def has_bot_permissions(chat_id):
    try:
        me = await bot.get_me()
        member = await bot.get_chat_member(chat_id, me.id)
        if member.status not in [ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER]:
            await log_to_group(chat_id, "Bot is not an admin")
            return False

        privileges = member.privileges
        if not privileges:
            await log_to_group(chat_id, "No privileges found for bot")
            return False

        if not privileges.can_delete_messages:
            await log_to_group(chat_id, "Missing permission: can_delete_messages")
            return False

        is_anonymous = hasattr(member, 'is_anonymous') and member.is_anonymous
        if not is_anonymous:
            await log_to_group(chat_id, "Warning: Bot is not anonymous admin")
        
        return True
    except Exception as e:
        print(f"Permission check failed: {e}")
        await log_to_group(chat_id, f"Permission check failed: {e}")
        return False

# /addgroup command (add group in private chat)
@bot.on_message(filters.command("addgroup") & filters.private)
async def add_group(client, message: Message):
    if not message.from_user or not await is_owner(message.from_user.id):
        return await message.reply("🚫 Only the bot owner can use this command.")
    if len(message.command) < 2:
        return await message.reply("❌ Usage:\n/addgroup <group_id>")
    
    try:
        group_id = int(message.command[1])
    except ValueError:
        return await message.reply("❌ Invalid group ID. Use the numeric ID (e.g., -100123456789).")
    
    if not await has_bot_permissions(group_id):
        return await message.reply("❌ Bot lacks required admin permissions (can_delete_messages).")
    
    managed_groups.add(group_id)
    await safe_execute(message.reply(f"✅ Added group {group_id}"))
    await log_to_group(group_id, f"Added group to join hider")
    await asyncio.sleep(1)

# /listgroups command (list managed groups)
@bot.on_message(filters.command("listgroups") & filters.private)
async def list_groups(client, message: Message):
    if not message.from_user or not await is_owner(message.from_user.id):
        return await message.reply("🚫 Only the bot owner can use this command.")
    
    if not managed_groups:
        return await message.reply("❌ No groups are being managed.")

    group_list = []
    for chat_id in managed_groups:
        try:
            chat = await client.get_chat(chat_id)
            group_list.append(f"- {chat.title} (ID: {chat_id})")
        except Exception:
            group_list.append(f"- Unknown (ID: {chat_id})")
    
    await message.reply("📋 **Managed Groups**\n" + "\n".join(group_list))
    await asyncio.sleep(1)

# Handle join message (delete immediately)
@bot.on_message(filters.new_chat_members & filters.group)
async def handle_join_message(client, message: Message):
    chat_id = message.chat.id
    if chat_id not in managed_groups:
        return
    try:
        await safe_execute(client.delete_messages(chat_id, message.id))
        await log_to_group(chat_id, f"Deleted join message {message.id}")
    except Exception as e:
        print(f"Failed to delete join message: {e}")
        await log_to_group(chat_id, f"Failed to delete join message: {e}")

# Handle leave message (delete immediately)
@bot.on_message(filters.left_chat_member & filters.group)
async def handle_leave_message(client, message: Message):
    chat_id = message.chat.id
    if chat_id not in managed_groups:
        return
    try:
        await safe_execute(client.delete_messages(chat_id, message.id))
        await log_to_group(chat_id, f"Deleted leave message {message.id}")
    except Exception as e:
        print(f"Failed to delete leave message: {e}")
        await log_to_group(chat_id, f"Failed to delete leave message: {e}")

bot.run()
