from pyrogram import Client
from pyrogram.errors import FloodWait
import asyncio
import time

api_id = 20345960
api_hash = "dbffff8460006c1b4d46733c32885c91"
group_link = "https://t.me/+j00kD0kK4iQ3YzJl"  # Replace this!

app = Client("super_approver", api_id=api_id, api_hash=api_hash)

async def main():
    await app.start()
    approved = 0

    try:
        chat = await app.get_chat(group_link)
        group_id = chat.id
    except Exception as e:
        print(f"❌ Failed to get group ID: {e}")
        return

    while True:
        requests = []
        async for user in app.get_chat_join_requests(group_id):
            requests.append(user)

        if not requests:
            print("✅ No more join requests.")
            break

        for user in requests:
            try:
                await app.approve_chat_join_request(group_id, user.user.id)
                approved += 1
                print(f"✅ Approved {user.user.first_name} (ID: {user.user.id}) | Total: {approved}")
                await asyncio.sleep(3)
            except FloodWait as e:
                print(f"⏳ FloodWait: Sleeping for {e.value} seconds...")
                time.sleep(e.value)
            except Exception as e:
                print(f"❌ Error approving {user.user.id}: {e}")

    await app.stop()

asyncio.run(main())
