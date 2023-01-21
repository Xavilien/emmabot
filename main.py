from telegram.ext import Updater, CommandHandler, ConversationHandler, CallbackQueryHandler, MessageHandler, Filters
from telegram import ChatAction, InlineKeyboardMarkup, InlineKeyboardButton, Bot
from telegram import ParseMode
import os
from functools import wraps

TOKEN = os.environ.get('EMMA_BOT_TOKEN')
PORT = int(os.environ.get('PORT', 5000))
OWNER = os.environ.get('TELEGRAM_ID', None)

VERSION = 0.0
VERSION_INTRO = "First Draft"

chats = {}
logs = []


def typing(func):
    """Sends typing action while processing func command."""

    @wraps(func)
    def command_func(update, context, *args, **kwargs):
        context.bot.send_chat_action(chat_id=update.effective_message.chat_id, action=ChatAction.TYPING)
        return func(update, context, *args, **kwargs)

    return command_func


# /version
@typing
def version(update, _):
    update.message.reply_text(f"<b>Version {VERSION}</b>\n"
                              f"{VERSION_INTRO}", parse_mode=ParseMode.HTML)
    return -1


# Updates owner when someone runs a command. Stores the logs temporarily which can be accessed by /logs
def log(update, command):
    username = update.message.from_user.username
    userid = update.message.from_user.id

    message = f"@{username} ({userid}) ran {command}"
    logs.append(message + "\n")

    if OWNER == 0:
        bot = Bot(TOKEN)
        bot.send_message(OWNER, message)


# Bot replies "Hello World!" when the /start command is activated for the Bot
@typing
def start(update, _):
    log(update, "/start")
    text = update.message.text.split()
    if len(text) < 2:
        update.message.reply_text("Please enter a name.")
        return -1

    name = text[1]
    welcome_message = f"Hi {name} 😀 \n\n" \
                      "Before we embark on Phase 0 please fill up this Intellectual Property Agreement Google Form " \
                      "as our resources are private and confidential. 😀 https://forms.gle/3JXob9Qf9SEwPmQN6" \
                      "\n\nI will also require your gmail thank you!"
    update.message.reply_text(welcome_message)


@typing
def stage1(update, _):
    log(update, "/stage1")
    stage1_message = "While waiting for the Agreement, let's proceed to level 1! 😀 \n\n" \
                     "Here are the details for *Level 1*: " \
                     "Overview of advisory 1. Our Services & Sample Consultation Video -"
    update.message.reply_text(stage1_message)


@typing
def stage2(update, _):
    log(update, "/stage2")
    stage2_message = "Hey let's go to level 2!! 🥳 \n\n" \
                     "*Level 2*\n" \
                     "*Basics of Financial Planning*" \
                     "\nEnjoy watching all the videos to have a bird's eye view on what financial planning is all " \
                     "about, so that you understand the value advisors provide for our clients, and have an idea on " \
                     "how you can provide this value for your friends as well."
    update.message.reply_text(stage2_message, parse_mode=ParseMode.MARKDOWN)


@typing
def stage3(update, _):
    log(update, "/stage3")
    stage3_message = "Let's head to the final stage of your assessment! 🥳 \n\n" \
                     "*Level 3* \n\n" \
                     "*AMRE* \n\n" \
                     "Time to get out of " \
                     "your own comfort zone. This process is for you to reach out to people around you, " \
                     "get their opinions and thoughts on advisors and what their ideal advisor should be. This will " \
                     "also build your resistance against rejections (if you get any). \n\n" \
                     "Fill up your database first, " \
                     "from your contacts, listing them down does not mean you will be reaching out to them, " \
                     "this exercise simply gives you a more macro view of your battleground, which will come in " \
                     "handy for the other Levels ahead."
    update.message.reply_text(stage3_message)


@typing
# /cancel
def cancel(update, _):
    log(update, "/cancel")
    update.message.reply_text("Operation cancelled.")
    return -1


# def get_conversation_handler():
#     mgr_filter = Filters.regex(r"(\d+ \d+\n\d+ \d+)")
#
#     conversation_handler = ConversationHandler(
#         entry_points=[CommandHandler('distance', distance)],
#         states={
#             "distance": [MessageHandler(mgr_filter, distance)],
#         },
#         fallbacks=[CommandHandler('cancel', cancel),
#                    CommandHandler('distance', distance)],
#
#     )
#
#     return conversation_handler


def main():
    updater = Updater(TOKEN)
    dp = updater.dispatcher  # Registers handlers (commands etc)

    # dp.add_handler(get_conversation_handler())
    dp.add_handler(CommandHandler("version", version))  # To keep track of bot updates
    dp.add_handler(CommandHandler("start", start))  # Run start function when /start command is used
    dp.add_handler(CommandHandler("stage1", stage1))
    dp.add_handler(CommandHandler("stage2", stage2))
    dp.add_handler(CommandHandler("stage3", stage3))

    print("Starting bot...")
    updater.start_polling()  # Start the bot

    url = "https://pathprofile.herokuapp.com/" + TOKEN
    updater.start_webhook(listen="0.0.0.0", port=PORT, url_path=TOKEN, webhook_url=url)

    updater.idle()  # Not exactly sure why this has to be here to be honest


if __name__ == '__main__':
    main()
