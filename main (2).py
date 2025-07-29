import json
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton
from telegram import ParseMode
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler
from keep_alive import keep_alive

TOKEN = "8317507530:AAHdsoVNN39H2pyfgW1zt3d-3L4MLgH5OU8"
CHANNEL_USERNAME = "@Lib_al"
GIFT_THRESHOLD = 3
GIFT_LINK = "https://t.me/laybry/14"
DATA_FILE = "data.json"

def load_data():
    try:
        with open(DATA_FILE, "r") as f:
            data = json.load(f)
            return data.get("referrals", {}), data.get("invited_by", {})
    except:
        return {}, {}

def save_data():
    with open(DATA_FILE, "w") as f:
        json.dump({"referrals": referrals, "invited_by": invited_by}, f)

referrals, invited_by = load_data()

def is_subscribed(bot, user_id):
    try:
        member = bot.get_chat_member(CHANNEL_USERNAME, user_id)
        return member.status in ['member', 'administrator', 'creator']
    except:
        return False

def start(update, context):
    user = update.message.from_user
    user_id = str(user.id)
    args = context.args

    if not is_subscribed(context.bot, int(user_id)):
        keyboard = InlineKeyboardMarkup([[InlineKeyboardButton("✅ Verify Subscription", callback_data="check_sub")]])
        update.message.reply_text(f"❌ You must join our channel first:\n{CHANNEL_USERNAME}", reply_markup=keyboard)
        return

    if args:
        referrer_id = str(args[0])
        if user_id != referrer_id and user_id not in invited_by:
            invited_by[user_id] = referrer_id
            referrals[referrer_id] = referrals.get(referrer_id, 0) + 1
            save_data()

            if referrals[referrer_id] == GIFT_THRESHOLD:
                context.bot.send_message(chat_id=int(referrer_id),
                    text=f"🎁 Congratulations! You earned a free book!\nHere it is: {GIFT_LINK}")

    welcome_text = f"👋 Welcome {user.first_name}!\nThanks for using the bot.\n\n📊 Referrals: {referrals.get(user_id, 0)}"
    inline_buttons = InlineKeyboardMarkup([
        [InlineKeyboardButton("🔗 MyLink", callback_data="mylink")],
        [InlineKeyboardButton("📊 Stats", callback_data="stats")],
        [InlineKeyboardButton("🆘 Help", callback_data="help")]
    ])

    reply_keyboard = ReplyKeyboardMarkup(
        [[KeyboardButton("🚀 Start")]], resize_keyboard=True
    )

    update.message.reply_text(welcome_text, reply_markup=reply_keyboard)
    update.message.reply_text("👇 Choose an option:", reply_markup=inline_buttons)

def button_handler(update, context):
    query = update.callback_query
    user_id = str(query.from_user.id)

    if query.data == "mylink":
        bot_username = context.bot.username
        link = f"https://t.me/{bot_username}?start={user_id}"
        query.edit_message_text(f"🔗 Your referral link:\n{link}")

    elif query.data == "stats":
        count = referrals.get(user_id, 0)
        query.edit_message_text(f"📈 You have referred {count} user(s).")

    elif query.data == "help":
        help_text = (
            "ℹ️ *Help Info*\n\n"
            "- Share your referral link.\n"
            "- Invite 3 friends.\n"
            "- Get a free book!\n"
            "- Make sure they join the channel."
        )
        query.edit_message_text(help_text, parse_mode=ParseMode.MARKDOWN)

    elif query.data == "check_sub":
        if is_subscribed(context.bot, int(user_id)):
            query.edit_message_text("✅ Subscription confirmed! Press /start again.")
        else:
            query.answer("❌ You're still not subscribed.", show_alert=True)

def main():
    updater = Updater(TOKEN, use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CallbackQueryHandler(button_handler))

    print("✅ Bot is running...")
    keep_alive()
    updater.start_polling()
    updater.idle()

main()