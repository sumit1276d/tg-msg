import asyncio
from telethon.sync import TelegramClient
from telethon.sessions import StringSession
from telethon.tl.functions.messages import GetHistoryRequest
from telethon.tl.functions.channels import CreateChannelRequest, InviteToChannelRequest
from telethon.tl.functions.messages import ImportChatInviteRequest
from telethon.tl.types import InputPeerChannel, InputChannel
from telethon.errors import ChatAdminRequiredError

# REPLACE THESE
API_ID = 23231941
API_HASH = '7da383341f3696f2933e660031b7a1ea'
STRING_SESSION = 'BQFifcUAcZvvJdCusbsuhtaKaHYfgIHTqedY1jfktaLBU1fneXYL9CveYWSaT8ngrEMCWObhVMaWdjVqIZgRiWzHJIRKuJMY5Aj32Sb__o2Sx-0b5QVE-N8fhDZDrMe4oV6vQa_IZbhtG5tnXUzXCYzx0hlq_4Jm9cZOu4DacHDTPApwEyTvos3pdXCluNxSJ0V4JXEzgsrDB5PFL841ZeziLKQ5JDjxk7NoPR0lV1nve-B3RaSGr6RsMFb2Pcn21VhseNrg2p2KMW0nE3oEyK80EYdseoS1xW-rrzzibsK87Mfk5vo2h1q65SPXLr0Hv7_cTjWVpV-CaKlMjqXzzpLXqQLf_wAAAAHB9U1nAA'

async def main():
    async with TelegramClient(StringSession(STRING_SESSION), API_ID, API_HASH) as client:
        print("✅ Logged in as:", (await client.get_me()).username)

        # Step 1: Find the first addlist link in saved messages
        saved = await client.get_messages('me', limit=20)
        addlist_link = None
        for msg in saved:
            if msg.message and ('t.me' in msg.message or 'telegram.me' in msg.message):
                addlist_link = msg.message.strip()
                break

        if not addlist_link:
            print("❌ No addlist link found in saved messages.")
            return

        print("📎 Found addlist link:", addlist_link)

        # Step 2: Join the source channel
        try:
            if '/+' in addlist_link:
                hash_part = addlist_link.split('/+')[-1]
                updates = await client(ImportChatInviteRequest(hash_part))
                source = updates.chats[0]
            else:
                source = await client.get_entity(addlist_link)
        except Exception as e:
            print("❌ Failed to join source channel:", e)
            return

        print("📥 Joined source channel:", source.title)

        # Step 3: Create a new channel
        result = await client(CreateChannelRequest(
            title=source.title + " Clone",
            about="Cloned by @YourBot",
            megagroup=False
        ))
        new_channel = result.chats[0]
        print("✅ Created new channel:", new_channel.title)

        # Step 4: Copy messages from source to destination
        print("📤 Forwarding messages...")
        offset_id = 0
        limit = 100
        total = 0

        while True:
            history = await client(GetHistoryRequest(
                peer=source,
                offset_id=offset_id,
                offset_date=None,
                add_offset=0,
                limit=limit,
                max_id=0,
                min_id=0,
                hash=0
            ))
            if not history.messages:
                break

            for msg in reversed(history.messages):
                try:
                    await client.send_message(new_channel.id, msg)
                    total += 1
                    await asyncio.sleep(0.5)  # Avoid flood wait
                except Exception as e:
                    print(f"⚠️ Error sending message: {e}")
                offset_id = msg.id

        print(f"✅ Finished cloning {total} messages to {new_channel.title}")

if __name__ == '__main__':
    asyncio.run(main())
