import telebot

from telebot import types

import threading



# === List of Bot Tokens ===

BOT_TOKENS = [

    '7346893218:AAGg2hSy4c0OqSfKYGm2Ec30hj-Y0GohUR4',
    '7737238053:AAH2ct3AsBmA_dt_sToviQpbiku0WgdoPCA',

    

    # Add more tokens here if needed

]



# === Main Menu Text ===

MAIN_MENU_TEXT = (

    "✅ 𝗣𝗿𝗲𝗺𝗶𝘂𝗺 𝗰𝗼𝗹𝗹𝗲𝗰𝘁𝗶𝗼𝗻 𝗳𝗼𝗿 𝗽𝗿𝗲𝗺𝗶𝘂𝗺 𝗰𝘂𝘀𝘁𝗼𝗺𝗲𝗿𝘀 ✅\n"

    "✅ 𝗔𝗹𝗹 𝗽𝗮𝗶𝗱, 𝗦𝗲𝗹𝗲𝗰𝘁 𝗮𝗻𝗱 𝗯𝘂𝘆 ✅\n\n"

    "❌𝗣𝗿𝗲𝗺𝗶𝘂𝗺 𝗰𝗼𝗹𝗹𝗲𝗰𝘁𝗶𝗼𝗻 𝗳𝗼𝗿 𝗽𝗿𝗲𝗺𝗶𝘂𝗺 𝗰𝘂𝘀𝘁𝗼𝗺𝗲𝗿𝘀 ❌\n"

    "❌ 𝗔𝗹𝗹 𝗽𝗮𝗶𝗱, 𝗦𝗲𝗹𝗲𝗰𝘁 𝗮𝗻𝗱 𝗯𝘂𝘆 ❌\n\n"

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

    "@pepesellsss\n"

    "@pepesellsss\n"

    "@pepesellsss\n"

    "@pepesellsss\n"

    "@pepesellsss\n"

    "@pepesellsssr"

)



# === Set Up Each Bot ===

def setup_bot(api_token):

    bot = telebot.TeleBot(api_token)



    # === Show Main Menu ===

    def send_main_menu(message):

        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)

        markup.add("📋 Menu", "✉️ DM for Buying", "💳 Payment Method")

        bot.send_message(message.chat.id, MAIN_MENU_TEXT, reply_markup=markup)



    # === /start Command ===

    @bot.message_handler(commands=['start'])

    def handle_start(message):

        send_main_menu(message)



    # === 📋 Menu Button ===

    @bot.message_handler(func=lambda m: m.text == "📋 Menu")

    def handle_menu(message):

        send_main_menu(message)



    # === ✉️ DM for Buying Button ===

    @bot.message_handler(func=lambda m: m.text == "✉️ DM for Buying")

    def handle_dm_buy(message):

        bot.send_message(message.chat.id, "📩 𝗗𝗠 𝗳𝗼𝗿 𝗯𝘂𝘆𝗶𝗻𝗴:\n@pepesellsss\nhttps://t.me/pepesellsss")



   # === 💳 Payment Method Button ===

    @bot.message_handler(func=lambda m: m.text == "💳 Payment Method")

    def handle_payment(message):

        bot.send_message(

            message.chat.id,

            "💰 *We accept:*\n"

            "🎀 PayPal\n"

            "🎀 Bank Transfer (Remitly / Western Union / TapTap)\n"

            "🎀 Gift Cards\n"

            "🎀 Crypto via Binance\n"

            "🎀 CashApp\n"

            "🎀 Zelle",

            parse_mode="Markdown"

        )





    # === Start Polling ===

    bot.polling()



# === Launch Bots in Threads ===

def run_bots():

    for token in BOT_TOKENS:

        threading.Thread(target=setup_bot, args=(token,)).start()



run_bots()
