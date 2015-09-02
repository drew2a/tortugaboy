import os
import re
import json
import time
from random import randint

from slacker import Slacker
from flask import Flask, request

app = Flask(__name__)

curdir = os.path.dirname(os.path.abspath(__file__))
os.chdir(curdir)

slack = Slacker(os.getenv('TOKEN'))
username = os.getenv('USERNAME', 'tortugaboy')
icon_emoji = os.getenv('ICON_EMOJI', ':moyai:')
channel = os.getenv('CHANNEL', '#random')
delay = int(os.getenv('DELAY_IN_SEC', '3'))

commands = ['game', 'gamerules', 'help', 'g', 'gr', 'h']

magic = -12
started = False
in_delay = False


def post_message(text, attachments=None):
    if not attachments:
        attachments = []

    slack.chat.post_message(channel=channel,
                            text=text,
                            username=username,
                            parse='full',
                            link_names=1,
                            attachments=attachments,
                            icon_emoji=icon_emoji)


def get_user(id):
    user = slack.users.info(id).body
    return user['user']['name']


def help():
    post_message('Hello! My name is Tortuga Boy.\n'
                 'Wanna play with me?\n'
                 'My commands:\n\n'
                 '*!game* or *!g*\n '
                 '*!gamerules* or *!gr*\n')


def rules():
    post_message('I will write "Game started" and get you a magic number (for example 7-0-6-1-1-4-4-8).\n'
                 'Who will type it the first (without dashes, for example 70611448) , that won!')


def dashes(i):
    result = ''
    for ch in str(i):
        result = result + ch + '-'
    return result.strip('-')


def game(user):
    global started, magic, in_delay
    if started or in_delay:
        post_message('No-no-no, @' + user + ', no-no-no.')
        return
    magic = randint(100, 99999999)
    post_message('Game will start after ' + str(delay) + ' seconds. Magic number is.... *' + dashes(magic) + '*')
    in_delay = True
    for x in reversed(range(0, delay)):
        post_message(str(x) + '...')
        time.sleep(1)
    post_message('*Start!*')
    in_delay = False
    started = True


def game_over(user):
    global started
    started = False
    post_message('Winner is: *@' + user + '*')


def process(text, user):
    global started, magic
    if not started: return
    if text.strip().split(' ')[0] == str(magic): game_over(user)


@app.route("/", methods=['POST'])
def main():
    # ignore message we sent
    message_user = request.form.get("user_name", "").strip()
    if message_user == username or message_user.lower() == "slackbot":
        return

    text = request.form.get("text", "")

    # find !command, but ignore <!command
    match = re.findall(r"(?<!<)!(\S+)", text)
    if not match:
        process(text, message_user)
        return json.dumps({})

    command = match[0]
    command = command.lower()

    if command not in commands:
        help()
        return json.dumps({})

    if command == 'game' or command == 'g':
        game(message_user)
    elif command == 'help' or command == 'h':
        help()
    elif command == 'gamerules' or command == 'gr':
        rules()

    return json.dumps({})


if __name__ == "__main__":
    app.run(debug=True)
