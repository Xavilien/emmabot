import os
import re
from datetime import timedelta, date
from functools import wraps

from flask import Flask, request
from telegram import ChatAction, ParseMode, Bot, Update

VERSION = 2.3
VERSION_INTRO = "Fixed a super pesky bug that prevented the bot from working when added to groups"

TOKEN = os.environ.get('EMMA_BOT_TOKEN')
PORT = int(os.environ.get('PORT', 5000))
ADMINS = os.environ.get('ADMINS').split('_')
OWNER = ADMINS[0]

app = Flask(__name__)
bot = Bot(TOKEN)


def typing(func):
    """Sends typing action while processing func command."""

    @wraps(func)
    def command_func(update, *args, **kwargs):
        bot.send_chat_action(chat_id=update.effective_message.chat_id, action=ChatAction.TYPING)
        return func(update, *args, **kwargs)

    return command_func


def log(update):
    """Updates owner when someone runs a command"""
    username = update.message.from_user.username
    userid = update.message.from_user.id
    command = update.message.text

    message = f"@{username} ({userid}) ran {command}"

    if OWNER:
        bot.send_message(OWNER, message)


@typing
def version(update):
    """Sends bot version to keep track of changes"""
    bot.send_message(update.message.chat.id, f"*Version {VERSION}*\n{VERSION_INTRO}", parse_mode=ParseMode.MARKDOWN)


@typing
def start(update):
    # Get the name of the person after the /start command
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
        # Retrieve the relevant message
        with open(f"text/{stage}.md") as file:
            message = file.read()

        # Add in the due date by replacing the placeholder text
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
    log(update)  # sends a message to my chat everytime someone interacts with the bot

    # check if the user running the command is an admin
    if str(update.message.from_user.id) not in ADMINS:
        bot.send_message(update.message.chat.id, "Sorry, not authorised.")
        return "Unauthorised"

    # Run the command if it exists
    command = re.findall("^/(\\w+)", str(update.message.text))
    if len(command) > 0:
        command = f"{command[0]}(update)"
        try:
            eval(command)
        except NameError:
            return "Command not found"

    return "Success"


@app.route('/', methods=['GET', 'POST'])
def set_webhook():
    url = "https://8xotrk.deta.dev/" + TOKEN
    bot.set_webhook(url)
    return "Success"


if __name__ == '__main__':
    app.run()
