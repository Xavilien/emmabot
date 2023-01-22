from flask import Flask, request
from telegram import ChatAction, ParseMode, Bot, Update
import os
from functools import wraps
import re

VERSION = 1.0
VERSION_INTRO = "Working MVP"

TOKEN = os.environ.get('EMMA_BOT_TOKEN')
PORT = int(os.environ.get('PORT', 5000))
OWNER = os.environ.get('TELEGRAM_ID', None)

app = Flask(__name__)
bot = Bot(TOKEN)


def typing(func):
    """Sends typing action while processing func command."""

    @wraps(func)
    def command_func(update, *args, **kwargs):
        bot.send_chat_action(chat_id=update.effective_message.chat_id, action=ChatAction.TYPING)
        return func(update, *args, **kwargs)

    return command_func


# Updates owner when someone runs a command
def log(update, command):
    username = update.message.from_user.username
    userid = update.message.from_user.id

    message = f"@{username} ({userid}) ran {command}"

    if OWNER:
        bot.send_message(OWNER, message)


@typing
def version(update):
    bot.send_message(update.message.chat.id, f"*Version {VERSION}*\n{VERSION_INTRO}", parse_mode=ParseMode.MARKDOWN)
    return -1


@typing
def start(update):
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

    bot.send_message(update.message.chat.id, welcome_message, parse_mode=ParseMode.MARKDOWN)


@typing
def stage1(update):
    log(update, "/stage1")
    stage1_message = "While waiting for the Agreement, let's proceed to level 1! 😀 \n\n" \
                     "Here are the details for *Level 1*: " \
                     "Overview of advisory 1. Our Services & Sample Consultation Video -"
    bot.send_message(update.message.chat.id, stage1_message, parse_mode=ParseMode.MARKDOWN)


@typing
def stage2(update):
    log(update, "/stage2")
    stage2_message = "Hey let's go to level 2!! 🥳 \n\n" \
                     "*Level 2*\n" \
                     "*Basics of Financial Planning*" \
                     "\nEnjoy watching all the videos to have a bird's eye view on what financial planning is all " \
                     "about, so that you understand the value advisors provide for our clients, and have an idea on " \
                     "how you can provide this value for your friends as well."
    bot.send_message(update.message.chat.id, stage2_message, parse_mode=ParseMode.MARKDOWN)


@typing
def stage3(update):
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
    bot.send_message(update.message.chat.id, stage3_message, parse_mode=ParseMode.MARKDOWN)


@app.route(f'/{TOKEN}', methods=['POST'])
def respond():
    update = Update.de_json(request.get_json(force=True), bot)
    text = update.message.text

    command = re.findall("^/(\\w+)", text)

    if len(command) > 0:
        command = f"{command[0]}(update)"
        try:
            eval(command)
        except NameError:
            pass

    return "Success"


@app.route('/', methods=['GET', 'POST'])
def set_webhook():
    url = "https://8xotrk.deta.dev/" + TOKEN
    bot.set_webhook(url)
    return "Webhook success"


if __name__ == '__main__':
    app.run()
