from telegram.constants import ParseMode
from constants import bot, commands_list
from study_buddy.courses import *
from study_buddy.notes import *


def help_request(message):
    request = message.text.split()
    if request[0].lower() not in "help":
        return False
    else:
        return True


@bot.message_handler(func=help_request)
@bot.message_handler(commands=['help'])
def bot_help(message):
    """Sends a greeting message and a list of commands to the user.
    Args:
        message (Message): The message object containing information about the user and chat.
    Returns:
        None
    """
    first_name = message.from_user.first_name  # Get the user's first name

    # Greeting message
    greeting_message = f"""
    *👋 Hello, {first_name}!*
    _Welcome to the Feluda Study Buddy Bot._ 
    """

    # Send the greeting and the command list
    bot.send_message(message.chat.id,
                     greeting_message + commands_list,
                     parse_mode=ParseMode.MARKDOWN)


@bot.message_handler(commands=['start'])
def start(message):
    first_name = message.from_user.first_name  # Get the user's first name

    # Greeting message
    greeting_message = f"""
    *👋 Hello, {first_name}!*
    _Welcome to the Feluda Study Buddy Bot._ 
    """

    # Send the greeting and the command list
    bot.send_message(message.chat.id,
                     greeting_message + commands_list,
                     parse_mode=ParseMode.MARKDOWN)

bot.polling()
