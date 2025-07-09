from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from telethon.tl.functions.channels import EditAdminRequest
from telethon.tl.types import ChatAdminRights

# ... rest of your imports and existing code ...

# === BOT COMMANDS ===
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("✅ Use:\n/multi_clone <source_channel> <count>")

async def multi_clone(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if len(context.args) != 2:
        await update.message.reply_text("❌ Usage:\n/multi_clone <source_channel> <count>")
        return
    source = context.args[0]
    count = int(context.args[1])
    chat_id = update.effective_chat.id
    threading.Thread(target=lambda: asyncio.run(clone_all(source, count, chat_id))).start()
    await update.message.reply_text("📡 Cloning started...")

# === Make admin with full rights ===
async def make_admin(client, channel, username):
    try:
        user = await client.get_entity(username)
        rights = ChatAdminRights(
            post_messages=True,
            edit_messages=True,
            delete_messages=True,
            ban_users=True,
            invite_users=True,
            pin_messages=True,
            add_admins=True,
            manage_call=True,
            anonymous=False,
            manage_chat=True
        )
        await client(EditAdminRequest(channel=channel, user_id=user, admin_rights=rights, rank="Admin"))
        return True
    except Exception as e:
        print(f"❌ Failed to promote admin: {e}")
        return False

# === Updated CLONE FLOW (only admin logic updated part shown here) ===
# Inside clone_all() after creating the channel, replace:
# await client(InviteToChannelRequest(channel=new_channel, users=[user]))

# With:
admin_added = await make_admin(client, new_channel, admin_username)
if admin_added:
    bot.send_message(chat_id, f"👑 Admin @{admin_username} promoted")
else:
    bot.send_message(chat_id, f"⚠️ Could not promote @{admin_username}")

# === MAIN FUNCTION ===
def main():
    if not os.path.exists(session_folder):
        os.makedirs(session_folder)

    print("🤖 Ready. Type `login` to add new session or press Enter to run bot.")
    cmd = input("➤ ").strip().lower()
    if cmd == "login":
        asyncio.run(login_account())
        return

    app = ApplicationBuilder().token(bot_token).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("multi_clone", multi_clone))
    print("🤖 Bot running...")
    app.run_polling()
