from pyrogram import Client
import asyncio

# Your credentials
api_id = 26418169
api_hash = "cf6bda80929e128329a837e20fbb52ed"
string_session = "1BZWaqwUAUDLP3rtMFD7YoJV7SVZ-AgMp8pumRV1DBC3I0n1Dqd62qkVzRCAE4RmcYuJ_p8EYCxXTnW2Wyd4aPYbf49EYX1vTKL2CjVff80B5dBN1BvwSd8GMTsVotLKL1dTWqdT1EgKBAJ-wTGFZz1rNVGGBpf2uqzquZZGEU83_HhvecDoWSAUoWUPeVMqkEP0FQSM0TmXgiIJFFiEZgAJiX-2nTAy26E--DYhFyH-kznjOOZ8pR3RkeTN6xRgQZ69cDOo8JweyHaBEHnCCNnjYkyCHK3RKfIVCuQUH9YvOkG3LYSgRXgF9H5649RDLjP5AjjIL0CFRXlgINOSnONGu61J90rM="

# Create the client
app = Client(
    name="proof_forwarder",  # required name param
    api_id=api_id,
    api_hash=api_hash,
    session_string=string_session
)

# Number of channels to create
NUM_CHANNELS = 30

# List to store new channel IDs
channel_ids = []

# Source channel username (without @)
SOURCE_CHANNEL = "genzsellervouches"

async def main():
    await app.start()
    print("✅ Logged in successfully.")

    # Step 1: Create 30 private channels
    for i in range(NUM_CHANNELS):
        title = f"Proof Channel {i+1}"
        try:
            result = await app.create_channel(
                title=title,
                description="Auto Proof Dump",
                is_megagroup=False  # False = channel
            )
            channel_ids.append(result.id)
            print(f"✅ Created: {title}")
        except Exception as e:
            print(f"❌ Failed to create channel {i+1}: {e}")
            continue
        await asyncio.sleep(1)

    # Step 2: Forward media messages from source to all created channels
    async for message in app.get_chat_history(SOURCE_CHANNEL, limit=100):
        if not message.media:
            continue  # Only forward media messages

        for chat_id in channel_ids:
            try:
                await app.forward_messages(chat_id, SOURCE_CHANNEL, message.id)
                await asyncio.sleep(0.5)  # Prevent rate limit
            except Exception as e:
                print(f"❌ Forward failed to {chat_id}: {e}")
                continue

    print("✅ Done. All media forwarded.")
    await app.stop()

# Run it
app.run(main())
