from argparse import ArgumentParser
from json import load
from connections import User, Room, Message
from socket import socket
from sys import exit, platform
from os import system, abort
from time import sleep
from re import sub
from random import choice
from threading import Thread

"""
This section of the code handles the command line input and parsing all the arguments using the argparse module.
The argparse module provides -h and --help by defaults and provide the user of this program to get an elaborate
explanation for the usage of the program. Furthermore it also provides us an easier way to handle the arguments
passed in by the user than using the sys module.
"""
parser = ArgumentParser(description="A client that connects to a REST API implemented with Flask"
                                    "for chatting with other users, or bots if you are very lonely."
                                    "A solution for the 2nd obligatory assignment in DATA2410 taught at "
                                    "OsloMet during spring 2021")
parser.add_argument('username', type=str,
                    help='Desired username to connect as (Connected as a user by default, i.e. not as a bot)')
parser.add_argument('-r', '--room', type=str, metavar='', nargs='+',
                    help='The desired room(s) to join upon running the script')
parser.add_argument('-p', '--push', action='store_true', help='Enable push notifications')
group = parser.add_mutually_exclusive_group()
group.add_argument('-u', '--user', action='store_true', help='Explicitly connect as a user')
group.add_argument('-b', '--bot', action='store_true', help='Explicitly connect as a bot')
arguments = parser.parse_args()

# Defining the global variables:
active_user = arguments.username
active_room = None
push_enabled = arguments.push
user_is_bot = arguments.bot
bot_responses = {}

# We shall at this point check if the user has is a bot and handle it accordingly:
if user_is_bot:
    # First convert first letter to a capital letter:
    active_user = active_user.capitalize()
    # Then check if the bot is one of the bots we have implemented:
    f = open('bots.json')
    bots = load(f)
    if active_user not in bots:
        exit(f"Unable to summon the bot named \"{active_user}\"\n"
             f"The only bots available are:\n{list(bots.keys())}")
    # If a bot has successfully been summoned then store their responses and close the opened file:
    bot_responses = bots[active_user]
    f.close()


# If the user is a bot we have to decide how the bot should respond to the message:
def bot_respond_to_message(user: str, message: str):
    # Check first if the user is itself do nothing if it is:
    if user == active_user:
        return

    # Parse the message:
    # Remove all special characters and make every characters to lowercase:
    message = sub('[^A-Za-z ]+', '', message).lower()
    word_list = message.split()  # This list should contain one word from the message on each index
    for word in word_list:
        # Check each word and if it matches one of the keyword from the bot then respond accordingly
        if word in bot_responses:
            the_response = choice(bot_responses)
            Message.send(active_room, active_user, the_response)


# Attempt to add the user
response, code = User.add(active_user, push_enabled)

# If the user does not exists we will get code == 201 i.e. we are registering them
if code == 201:
    print(f"Registering user with username \"{active_user}\"")
# Connect the user to the push notification service which has two purposes:
# Providing push notification if the user has it enabled and provide the user with live message updates:
client = socket()
client.connect(('127.0.0.1', 5005))

# Provide the username that has connected to the push notification server:
client.send(active_user.encode('utf8'))

# Tell the user that they have successfully connected:
print(f"Connected to the chat as \"{active_user}\"")


# Define a function to join a room which will be used later for commands:
def join(rooms: list = None):
    global active_room
    message_to_user = ''
    # Is rooms None?
    if rooms is None:
        rooms = []  # Start with an empty list

    # If no arguments has been provided:
    if len(rooms) == 0:
        # Give the user a list of available rooms:
        # Request all rooms:
        r, c = Room.get_all(active_user)

        # The request will send back all rooms as a dictionary as specified by the API.
        # Only get the keys from the dictionary.
        all_rooms = list(r.keys())
        if len(all_rooms) == 0:
            # If there are no rooms:
            message_to_user += "There are currently no rooms available.\n"
            print("There are currently no rooms available.")
            # Prompt the user to create a new room:
            message_to_user += "Enter the name of a new room:\n"
            new_room = input("Enter the name of a new room: ")
        else:
            message_to_user += "These rooms are currently available:\n"
            print("These rooms are currently available:")
            print(all_rooms)
            message_to_user += "Enter the name of the room you want to join\nor enter a new name to create a new " \
                               "room:\n "
            new_room = input("Enter the name of the room you want to join\n"
                             "or enter a new name to create a new room:\n")
        message_to_user += f"{new_room}\n"
        rooms = [new_room]

    for room in rooms:
        r, c = Room.join(room, active_user)
        # If the room does not exists, we create the room:
        if c == 404:
            message_to_user += f"Creating a new room with room name \"{room}\"\n"
            print(f"Creating a new room with room name \"{room}\"")
            Room.add(room, active_user)
        message_to_user += f"Joining room with name \"{room}\"\n"
        print(f"Joining room with name \"{room}\"")
        active_room = room
    # Give the user a moment to process everything that has happened:
    sec = 3
    while sec > 0:
        clear_console()
        print(f"{message_to_user}\n")
        print(f"Entering {active_room} in {sec}...")
        sec -= 1
        sleep(1)

    # Then fetch all the messages in the active room:
    if user_is_bot:  # In case of a bot send an initial greeting in this room
        Message.send(active_room, active_user, choice(bot_responses['greet']))


# This function will refresh the terminal based on if the program is ran on windows or linux
def clear_console():
    if platform.__contains__('win'):
        system('cls')
    else:
        system('clear')


# This function refreshes all messages inside the active room
def refresh_messages_in_this_room():
    global active_room
    clear_console()
    # Get all the messages inside that room:
    all_messages, c = Message.get_all_from_room(active_room, active_user)
    print(30 * '-')
    for message in all_messages:
        print(f"{message['user']}: {message['message']} \t\t {message['time']}")
    if user_is_bot and len(all_messages) > 0:
        # Grab the last message:
        with_message = all_messages[-1]['message']
        from_user = all_messages[-1]['user']
        bot_respond_to_message(from_user, with_message)
    print(30 * '-')


# After we have connected the chat as the user we need to join the room provided in the terminal
# If none was provided then we will just simply force the user to create a room:
join(arguments.room)


# When an user has joined a room we should start listening for live messages:
# For this we start a thread:
def live_messages():
    while True:
        # Server will first send us a room_id
        room_id = client.recv(1024).decode('utf8')
        unread = client.recv(1024).decode('utf8')
        if active_room == room_id:
            refresh_messages_in_this_room()
        elif push_enabled:
            print(f"You have {unread} unread messages in room \"{room_id}\"")
        print(30 * '-')


# We must also be able to send messages:
def send_messages():
    refresh_messages_in_this_room()
    while True:
        sleep(0.1)
        print(30 * '-')
        message = input('').strip()
        # Only non-bot users can use this thread to send messages:
        if not commands(message) and message and not user_is_bot:
            Message.send(active_room, active_user, message)
        else:
            clear_console()
            refresh_messages_in_this_room()


# Define commands so we can navigate and interact with the program:
def commands(cmd: str):
    cmds = {
        '/join': join,
        '/exit': exit_program,
        '/toggle_push': toggle_push_notification
    }

    # Parse the incoming string:
    # Convert everything to lowercase and split
    word_list = cmd.lower().split()
    if len(word_list) == 0:
        return False

    cmd = word_list.pop(0)

    if cmd in cmds:
        cmds[cmd](word_list)
        return True
    return False


def exit_program(void):
    print("Exiting program!")
    abort()


def toggle_push_notification(void):
    global push_enabled
    push_enabled = not push_enabled
    User.toggle_push(active_user)


# Start a thread for live messages:
live_message_thread = Thread(target=live_messages)
live_message_thread.start()

# Start a thread for sending messages:
send_message_thread = Thread(target=send_messages)
send_message_thread.start()
