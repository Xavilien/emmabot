from flask import Flask, request
from telegram import ChatAction, ParseMode, Bot, Update
import os
from functools import wraps
import re
from datetime import timedelta, date

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
def stages(update, stage: str, deadline: int):
    try:
        log(update, f"/{stage}")
        with open(f"text/{stage}.md") as file:
            message = file.read()

        due_date = (date.today() + timedelta(deadline)).strftime("%d/%m/%Y")
        message = re.sub("<insert date>", str(due_date), message)
        bot.send_message(update.message.chat.id, message, parse_mode=ParseMode.MARKDOWN)
    except Exception as e:
        bot.send_message(update.message.chat.id, str(e))


def stage1(update):
    stages(update, "stage1", 3)


def stage2(update):
    stages(update, "stage2", 3)


def stage3(update):
    stages(update, "stage3", 10)


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
