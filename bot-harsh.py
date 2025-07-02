import telebot
from telebot import types
import threading
import os
import re

# === Owner and Log Group ID ===
OWNER_ID = 7728339922  # Replace with your Telegram ID
LOG_GROUP_ID = -1002607860400  # Replace with your log group ID

# === List of Bot Tokens ===
BOT_TOKENS = [
   '8017395949:AAFNT9yiaJG1qP65MpYyUX_IFtqBGLUx6tA',
   '7716788867:AAGxhAQQe0krMD_bzMYLNnZKL36TZor2qXk',
   '7342709630:AAGYvXxRdho0LPjH8rbXpUAAKTaVvK-n5yA',
   '7345023240:AAGwIENQGR3i0jrZRO0OZL4SPciH85JJkeQ',
]

# === Main Menu Text ===
MAIN_MENU_TEXT = (
     "✅ 𝗣𝗿𝗲𝗺𝗶𝘂𝗺 𝗰𝗼𝗹𝗹𝗲𝗰𝘁𝗶𝗼𝗻 𝗳𝗼𝗿 𝗽𝗿𝗲𝗺𝗶𝘂𝗺 𝗰𝘂𝘀𝘁𝗼𝗺𝗲𝗿𝘀 ✅\n"
    "✅ 𝗔𝗹𝗹 𝗽𝗮𝗶𝗱, 𝗦𝗲𝗹𝗲𝗰𝘁 𝗮𝗻𝗱 𝗯𝘂𝘆 ✅\n\n"

    "✅𝟭. 𝗠𝗼𝗺 𝘀𝗼𝗻 ( 𝟰,𝟯𝟬𝟬+ 𝘃𝗶𝗱𝗲𝗼𝘀 ✅️)\n"
    "🍓𝟮. 𝗦𝗶𝘀 𝗯𝗿𝗼 ( 𝟰,𝟬𝟬𝟬+ 𝘃𝗶𝗱𝗲𝗼𝘀 ✅️ )\n"
    "🍆𝟯. 𝗖𝗽 𝗸!𝗱𝘀 ( 𝟱𝟬,𝟬𝟬𝟬+ 𝘃𝗶𝗱𝗲𝗼𝘀 ✅️)\n"
    "✅𝟰. 𝗗𝗮𝗱 𝗱𝗮𝘂𝗴𝗵𝘁𝗲𝗿 ( 𝟰,𝟬𝟬𝟬+  𝘃𝗶𝗱𝗲𝗼𝘀 ✅️)\n"
    "⭐️𝟱. 𝗥@𝗽𝗲 & 𝗳𝗼𝗿𝗰𝗲 ( 𝟱𝟬𝟬𝟬+ 𝘃𝗶𝗱𝗲𝗼𝘀 ✅️ )\n"
    "🍑𝟲. 𝗧𝗲𝗲𝗻 ( 𝟭𝟬,𝟬𝟬𝟬+ 𝘃𝗶𝗱𝗲𝗼𝘀 ✅️)\n"
    "✅𝟯. 𝗨𝘀𝗮 𝗖𝗣  ( 𝟭,𝟲𝟬𝟬+ 𝘃𝗶𝗱𝗲𝗼𝘀 ✅️)\n"
    "🍓𝟴. 𝗛𝗶𝗱𝗱𝗲𝗻 𝗰𝗮𝗺 ( 𝟰,𝟬𝟬𝟬+ 𝘃𝗶𝗱𝗲𝗼𝘀 ✅️)\n"
    "🍆𝟵. 𝗦𝗻𝗮𝗽 𝗶𝗻𝘀𝘁𝗮 𝗹𝗲𝗮𝗸 ( 𝟱𝟬𝟬𝟬+ 𝘃𝗶𝗱𝗲𝗼𝘀 ✅️)\n"
    "✅𝟭𝟬. 𝗝𝗮𝗽𝗮𝗻𝗲𝘀𝗲 ( 𝟱𝟬𝟬𝟬+ 𝘃𝗶𝗱𝗲𝗼𝘀 ✅️)\n"
    "⭐️𝟭𝟭. 𝗕𝗹𝗮𝗰𝗸 𝘁𝗲𝗲𝗻 𝘃𝗶𝗱𝗲𝗼𝘀 ( 𝟭𝟬𝟬𝟬+ 𝘃𝗶𝗱�_e𝗼𝘀 ✅️)\n"
    "🏃‍♂️𝟭𝟮. 𝗢𝗻𝗹𝘆 𝗳𝗮𝗻 ( 𝟭𝟬𝟬𝟬𝟬+ ✅️)\n"
    "🍑𝟭𝟯. 𝗟𝗲𝗮𝗸𝘀 ( 𝟭𝟬𝟬𝟬𝟬+ 𝘃𝗶𝗱𝗲𝗼𝘀 ✅️ )\n"
    "🍆 𝟭𝟰. 𝗔𝗻𝗶𝗺𝗮𝗹𝘀 𝘄𝗶𝘁𝗵 𝗴𝗶𝗿𝗹𝘀 ( 𝟮𝟱𝟬𝟬+ 𝘃𝗶𝗱𝗲𝗼𝘀 ✅️)\n"
    "🍓 𝟭𝟱. 𝗣𝘂𝗯𝗹𝗶𝗰 𝗮𝗴𝗲𝗻𝘁𝘀 ( 𝟭𝟰𝟬𝟬+ 𝘃𝗶𝗱𝗲𝗼𝘀 ✅️)\n"
    "🔥 𝟭𝟲. 𝗚𝗮𝘆 𝗖𝗣 ( 𝟭𝟬,𝟬𝟬𝟬+ 𝘃𝗶𝗱𝗲𝗼𝘀 ✅️) \n"
    "🥵 𝟭𝟳. 𝗧𝗮𝗺𝗶𝗹, 𝗠𝗮𝗹𝗹𝘂 ( 𝟭𝟬𝟬𝟬𝟬+ 𝘃𝗶𝗱𝗲𝗼𝘀 ✅)\n"
    "😍 𝟭𝟴. 𝗚𝗶𝗿𝗹𝘀 𝗻𝘂𝗱𝗲 𝗽𝗶𝗰𝘀 ( 𝟭𝟬𝟬𝗞 𝗣𝗵𝗼𝘁𝗼𝘀 ✅)\n"
    "🍑 𝟭𝟵. 𝗗𝗿𝘂𝗴𝗴𝗲𝗱  𝗴𝗶𝗿𝗹 𝗳#𝗰𝗸 ( 𝟲𝟱𝟬𝟬+ 𝘃𝗶𝗱𝗲𝗼𝘀 ✅ )\n"
    "🔥 𝟮𝟭. 𝗚𝗶𝗿𝗹𝘀 𝗕𝗹𝗮𝗰𝗸 𝗺𝗮𝗶𝗹 ( 𝟰𝟬𝟬𝟬+ 𝘃𝗶𝗱𝗲𝗼𝘀 ✅)\n"
    "🤤 𝟮𝟮. 𝗜𝗻𝗱𝗶𝗮𝗻 𝗗𝗲𝘀𝗶 ( 𝟯𝟬,𝟬𝟬𝟬+ 𝗩𝗶𝗱𝗲𝗼𝘀 ✅ )\n"
    "🤩 𝟮𝟯. 𝗢𝗹𝗱 𝗮𝗴𝗲 𝗚𝗿𝗮𝗻𝗻𝘆 𝗦#𝘅 ( 𝟰𝟬𝟬𝟬+ 𝗩𝗶𝗱𝗲𝗼𝘀 ✅ )\n"
    "🔞 𝟮𝟰. 𝗦𝗰𝗵𝗼𝗼𝗹 𝗚𝗶𝗿𝗹𝘀 ( 𝟮,𝟬𝟬𝟬+ 𝗩𝗶𝗱𝗲𝗼𝘀 ✅ )\n"
    "🥵 𝟮𝟱. 𝗖𝗵𝗶𝗻𝗲𝘀𝗲 𝗧𝗲𝗲𝗻 ( 𝟴,𝟬𝟬𝟬+ 𝗩𝗶𝗱𝗲𝗼𝘀 ✅ )\n"
    "🔥 𝟮𝟲. 𝗦𝗻𝗮𝗽𝗴𝗼𝗱 ( 𝟱𝟬,𝟬𝟬𝟬+ 𝗩𝗶𝗱𝗲𝗼𝘀 ✅ )\n"
    "🌟 𝟮𝟳. 𝗕𝗗𝗠𝗦 ( 𝟭,𝟬𝟬𝟬+ 𝗩𝗶𝗱𝗲𝗼𝘀 ✅ )\n"
    "😍 𝟮𝟴. 𝗣𝗲𝗲 & 𝗦𝗰𝗮𝘁 ( 𝟭,𝟬𝟬𝟬+ 𝗩𝗶𝗱𝗲𝗼𝘀 ✅ )\n"
    "🤤 𝟮𝟵. 𝗦𝗵𝗲𝗺𝗮𝗹𝗲 ( 𝟮,𝟬𝟬𝟬+ 𝗩𝗶𝗱𝗲𝗼𝘀 ✅ )\n"
    "❤️ 𝟮9. 𝗔𝗹𝗹 𝗩𝗜𝗗𝗘𝗢𝗦 𝗚𝗥𝗢𝗨𝗣𝗦 + �_M𝗘𝗚𝗔 𝗟𝗜𝗡𝗞𝗦 ( 𝟮,𝟬𝟬𝟬𝟬𝟬 + 𝗩𝗶𝗱𝗲𝗼𝘀 ✅ )\n\n"
    "📩 𝗗𝗺 𝗳𝗼𝗿 𝗯𝘂𝘆 𝗮𝗻𝗱 𝗳𝘂𝗹𝗹 𝗱𝗲𝘁𝗮𝗶𝗹𝘀 ✅\n"
    "@Lord_seller_x0\n"
    "@Lord_seller_x0\n"
    "@Lord_seller_x0\n"
    "@Lord_seller_x0\n"
    "@Lord_seller_x0\n"
    "@Lord_seller_x0\n"
   "https://t.me/Lord_seller_xx0"
)

# === Escape text for MarkdownV2 ===
def escape_markdown(text):
    escape_chars = r"_*[]()~`>#+-=|{}.!"
    return re.sub(f"([{re.escape(escape_chars)}])", r"\\\1", text)

# === Save user ID to file ===
def save_user(user_id):
    try:
        with open("users.txt", "a+") as f:
            f.seek(0)
            users = f.read().splitlines()
            if str(user_id) not in users:
                f.write(f"{user_id}\n")
    except Exception:
        pass

# === Load all user IDs from file ===
def load_users():
    if not os.path.exists("users.txt"):
        return []
    with open("users.txt", "r") as f:
        return list(set([line.strip() for line in f if line.strip().isdigit()]))

# === Set Up Each Bot ===
def setup_bot(api_token):
    bot = telebot.TeleBot(api_token)

    def send_main_menu(message):
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        markup.add("\ud83d\udccb Menu", "\u2709\ufe0f DM for Buying", "\ud83d\udcb3 Payment Method")
        try:
            bot.send_message(message.chat.id, MAIN_MENU_TEXT, reply_markup=markup, parse_mode="MarkdownV2")
        except Exception:
            pass

    @bot.message_handler(commands=['start'])
    def handle_start(message):
        save_user(message.from_user.id)
        send_main_menu(message)

        user = message.from_user
        name = f"{user.first_name or ''} {user.last_name or ''}".strip()
        username = f"@{user.username}" if user.username else "No username"

        name_md = escape_markdown(name)
        username_md = escape_markdown(username)

        log_text = (
            f"\ud83d\udfe2 New User Started Bot\n\n"
            f"\ud83d\udc64 Name: {name_md}\n"
            f"\ud83c\udd94 ID: `{user.id}`\n"
            f"\ud83d\udd17 Username: {username_md}"
        )

        try:
            bot.send_message(LOG_GROUP_ID, log_text, parse_mode="MarkdownV2")
        except Exception as e:
            print(f"[ERROR] Logging user failed: {e}")

    @bot.message_handler(commands=['broadcast'])
    def handle_broadcast(message):
        if message.from_user.id != OWNER_ID:
            return

        parts = message.text.split(maxsplit=1)
        if len(parts) < 2:
            bot.send_message(message.chat.id, "\u274c Usage: /broadcast Your message here")
            return

        broadcast_msg = parts[1]
        users = load_users()
        success = 0
        failed = 0

        for uid in users:
            try:
                bot.send_message(int(uid), broadcast_msg)
                success += 1
            except Exception as e:
                failed += 1
                print(f"[Broadcast Error] {uid}: {e}")
                continue

        summary = (
            f"\ud83d\udce2 Broadcast Summary:\n"
            f"\u2705 Sent: {success}\n"
            f"\u274c Failed: {failed}\n"
            f"\ud83d\udc65 Total: {len(users)}"
        )
        try:
            bot.send_message(message.chat.id, summary)
        except Exception as e:
            print(f"[ERROR] Failed to send summary to admin: {e}")

    @bot.message_handler(commands=['total'])
    def handle_total(message):
        if message.from_user.id != OWNER_ID:
            return
        users = load_users()
        try:
            bot.send_message(message.chat.id, f"\ud83d\udc65 Total users: {len(users)}")
        except Exception as e:
            print(f"[ERROR] Failed to send total users: {e}")

    @bot.message_handler(func=lambda m: m.text == "\ud83d\udccb Menu")
    def handle_menu(message):
        send_main_menu(message)

    @bot.message_handler(func=lambda m: m.text == "\u2709\ufe0f DM for Buying")
    def handle_dm_buy(message):
        bot.send_message(message.chat.id, "\ud83d\udce9 𝗗𝗠 𝗳𝗼𝗿 𝗯𝘂𝘆𝗶𝗻𝗴:\n@Lord_seller_xx0\nhttps://t.me/Lord_seller_xx0")

    @bot.message_handler(func=lambda m: m.text == "\ud83d\udcb3 Payment Method")
    def handle_payment(message):
        payment_text = (
            "\ud83d\udcb0 *We accept:*\n"
            "\ud83c\udf80 PayPal\n"
            "\ud83c\udf80 Bank Transfer (Remitly / Western Union / TapTap)\n"
            "\ud83c\udf80 Gift Cards\n"
            "\ud83c\udf80 Crypto via Binance\n"
            "\ud83c\udf80 CashApp\n"
            "\ud83c\udf80 Zelle"
        )
        bot.send_message(message.chat.id, payment_text, parse_mode="MarkdownV2")

    try:
        bot.polling(non_stop=True)
    except Exception as e:
        print(f"[ERROR] Polling crashed: {e}")

# === Launch Bots in Threads ===
def run_bots():
    for token in BOT_TOKENS:
        threading.Thread(target=setup_bot, args=(token,)).start()

run_bots()
