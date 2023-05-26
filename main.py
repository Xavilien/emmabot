import os
import re
from datetime import timedelta, date
from functools import wraps

from flask import Flask, request
from telegram import ChatAction, ParseMode, Bot, Update
from deta import Deta

VERSION = 2.3
VERSION_INTRO = "Fixed a super pesky bug that prevented the bot from working when added to groups"

TOKEN = os.environ.get('EMMA_BOT_TOKEN')
PORT = int(os.environ.get('PORT', 5000))
ADMINS = os.environ.get('ADMINS').split('_')
KEY = os.environ.get('DETA_PROJECT_KEY')
OWNER = ADMINS[0]

app = Flask(__name__)
bot = Bot(TOKEN)

deta = Deta(KEY)
users = deta.Base("users")


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
    chat_id = update.message.chat.id

    # Get the name of the person after the /start command
    text = update.message.text.split()
    if len(text) < 2:
        update.message.reply_text("Please enter a name.")
        return -1

    name = text[1]

    users.put({
        "key": str(chat_id),
        "name": name,
        "next_stage": "stage0"
    })

    welcome_message = f"Hi {name} 😀 \n\n" \
                      "Before we embark on Phase 0 please fill up this Intellectual Property Agreement Google Form " \
                      "as our resources are private and confidential. 😀 https://forms.gle/3JXob9Qf9SEwPmQN6" \
                      "\n\nAlso can I get your email?"

    bot.send_message(chat_id, welcome_message, parse_mode=ParseMode.MARKDOWN)


@typing
def stages(update, stage: str, deadline: int):
    """Choose the correct stage to run"""
    chat_id = update.message.chat.id

    try:
        # Check if user exists
        user = users.get(str(chat_id))
        if not user:
            bot.send_message(chat_id, "User does not exist. Please run /start first")
            return

        # Check if user is at the correct stage
        if user["next_stage"] != stage:
            bot.send_message(chat_id, f"Wrong stage. Next stage should be /{user['next_stage']}")
            return

        # Retrieve the relevant message
        with open(f"text/{stage}.md") as file:
            message = file.read()

        # Add in name by replacing the placeholder text
        message = re.sub("<name>", user["name"], message)

        # Add in the due date by replacing the placeholder text
        due_date = (date.today() + timedelta(deadline)).strftime("%d/%m/%Y")
        message = re.sub("<insert date>", str(due_date), message)

        # Update stage
        user["next_stage"] = f"stage{int(user['next_stage'][-1]) + 1}"
        users.put(user)

        bot.send_message(chat_id, message, parse_mode=ParseMode.MARKDOWN)

    except Exception as e:
        bot.send_message(chat_id, f"Error: {e}")


def stage0(update):
    stages(update, "stage0", 1)


def stage1(update):
    stages(update, "stage1", 3)


def stage2(update):
    stages(update, "stage2", 3)


def stage3(update):
    stages(update, "stage3", 10)


def next_stage(update):
    chat_id = update.message.chat.id

    try:
        command = users.get(str(chat_id))['next_stage']

        if command == "stage4":
            bot.send_message(chat_id, "No more stages left, congrats!")
            return

        eval(f"{command}(update)")

    except Exception as e:
        bot.send_message(chat_id, f"Error: {e}")


def back(update):
    chat_id = update.message.chat.id

    try:
        user = users.get(str(chat_id))
        previous = int(user['next_stage'][-1]) - 1

        if previous < 0:
            bot.send_message(chat_id, "Next stage already at /stage0")
            return

        user["next_stage"] = f"stage{previous}"
        users.put(user)

        bot.send_message(chat_id, f"Next stage is /stage{previous}")

    except Exception as e:
        bot.send_message(chat_id, f"Error: {e}")


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
        if command[0] == "next":
            next_stage(update)
            return "Success"

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
