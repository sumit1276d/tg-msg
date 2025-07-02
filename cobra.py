from telethon.sync import TelegramClient
from telethon.tl.functions.channels import (
    CreateChannelRequest, ExportChatInviteRequest, InviteToChannelRequest,
    EditBannedRequest
)
from telethon.tl.functions.messages import (
    SendMessageRequest, PinMessagesRequest
)
from telethon.tl.functions.contacts import ResolveUsernameRequest
from telethon.tl.types import ChatBannedRights
from telethon.errors import SessionPasswordNeededError

# ✅ HARD-CODED API ID + HASH
api_id = 22046466
api_hash = "e28a9150403458514e9469cdbb1d54d1"

print("📲 Telegram Group Auto Creator\n")
phone = input("📞 Enter your Telegram phone number (with +): ").strip()
session_name = f"session_{phone.replace('+', '')}"

client = TelegramClient(session_name, api_id, api_hash)
client.connect()

if not client.is_user_authorized():
    client.send_code_request(phone)
    code = input("📥 Enter the OTP you received: ").strip()
    try:
        client.sign_in(phone, code)
    except SessionPasswordNeededError:
        pw = input("🔐 Enter your 2FA password: ").strip()
        client.sign_in(password=pw)

# Ask for group name
group_name = input("🏷️ Enter the group name to create: ").strip()

# Create group (megagroup)
result = client(CreateChannelRequest(
    title=group_name,
    about="",
    megagroup=True
))
group = result.chats[0]
group_id = group.id
print(f"\n✅ Group created: {group.title} (ID: {group_id})")

# Don't hide history (default behavior shows it to new members)

# Revoke basic member permissions
ban_rights = ChatBannedRights(
    until_date=None,
    send_messages=True,
    send_media=True,
    send_stickers=True,
    send_gifs=True,
    send_games=True,
    send_inline=True,
    send_polls=True,
    change_info=True,
    invite_users=True,
    pin_messages=True
)
client(EditBannedRequest(group, "all", ban_rights))
print("🚫 Revoked all default member permissions")

# Add ghclonebot
bot_username = "ghclonebot"
bot = client(ResolveUsernameRequest(bot_username)).users[0]
client(InviteToChannelRequest(group, [bot]))
print(f"🤖 Bot @{bot_username} added")

# Generate group link
invite = client(ExportChatInviteRequest(group.id))
group_link = invite.link
print(f"\n🔗 Group invite link: {group_link}")

# Send welcome message and pin
welcome_text = f"👋 Welcome!\n\n📤 Share this group to unlock:\n🔗 {group_link}"
msg = client(SendMessageRequest(peer=group.id, message=welcome_text))
client(PinMessagesRequest(peer=group.id, id=[msg.id], silent=True))
print("📌 Welcome message sent and pinned.")

# Save to file
with open("created_groups.txt", "a") as f:
    f.write(f"{group.title} | {group_link}\n")

print("\n✅ Group is ready! Promote using the link above.")
client.disconnect()
