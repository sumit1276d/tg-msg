from pyrogram import Client, filters
from pyrogram.types import Message
import asyncio
from pyrogram import idle

API_ID = 20430204
API_HASH = "fef11a3be7bc24fdd1bccf0be8298580"

BOT_TOKENS = [
"7790690194:AAFaHlXhEB9Ix888_Rx2IyThVhSZx1y1G48",
"7755027583:AAEuBKfd4qLTwr3dPqwQD1mZOCDfgYt1mW4",
"8021021008:AAG-iBScwb7QKI9BYe3foPJIrSC39yYOroc",
    # ... add more tokens as needed
]

clients = []

def create_bot(token):
    bot = Client(f"bot_{token[:6]}", api_id=API_ID, api_hash=API_HASH, bot_token=token)

    @bot.on_message(filters.new_chat_members & filters.group)
    async def delete_join(client, message: Message):
        try:
            await client.delete_messages(message.chat.id, message.id)
        except Exception as e:
            print(f"[{token[:6]}] Join delete failed: {e}")

    @bot.on_message(filters.left_chat_member & filters.group)
    async def delete_leave(client, message: Message):
        try:
            await client.delete_messages(message.chat.id, message.id)
        except Exception as e:
            print(f"[{token[:6]}] Leave delete failed: {e}")

    @bot.on_message(filters.command("start") & filters.group)
    async def started(client, message: Message):
        if message.from_user and message.from_user.id:
            await message.reply("✅ Join Hider Bot Activated!\nAdd me as admin and I'll clean join/leave messages.")
    
    return bot

for token in BOT_TOKENS:
    client = create_bot(token)
    clients.append(client)

async def main():
    await asyncio.gather(*[c.start() for c in clients])
    print("🚀 All Join Hider Bots are running.")
    await idle()
    await asyncio.gather(*[c.stop() for c in clients])

asyncio.run(main())
