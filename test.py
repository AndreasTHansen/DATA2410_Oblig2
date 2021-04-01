import argparse
import json
import pickle
import requests
from connections import User, Room, Message
from socket import socket, AF_INET, SOCK_STREAM
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
parser = argparse.ArgumentParser(description="A client that connects to a REST API implemented with Flask"
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
    bots = json.load(f)
    if active_user not in bots:
        exit(f"Unable to summon the bot named \"{active_user}\"\n"
             f"The only bots available are:\n{list(bots.keys())}")
    # If a bot has successfully been summoned then store their responses and close the opened file:
    bot_responses = bots[active_user]
    f.close()


# If the user is a bot we have to decide how the bot should respond to the message:
def bot_respond_to_message(user: str, message: str):
    global active_room
    global active_user
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
            the_response = choice(bot_responses[word])
            Message.send(active_room, active_user, the_response)

            room_users, c = Room.get_all_users(active_room, active_user)  # GET users in this room from API
            data = pickle.dumps((active_room, room_users))  # Convert tuple to bytes
            client.send(data)  # Send data through socket

            refresh_messages_in_this_room()


# Attempt to add the user
code = 0
try:
    response, code = User.add(active_user)
except requests.ConnectionError:
    exit(f"Cannot establish connection to the API server... Make sure the server is running!")

# If the user does not exists we will get code == 201 i.e. we are registering them
if code == 201:
    print(f"Registering user with username \"{active_user}\"")
# Connect the user to the push notification service which has two purposes:
# Providing push notification if the user has it enabled and provide the user with live message updates:
client = socket(AF_INET, SOCK_STREAM)
client.connect(('127.0.0.1', 5005))

# Provide the username that has connected to the push notification server:
client.send(active_user.encode('utf8'))

# Tell the user that they have successfully connected:
print(f"Connected to the chat as \"{active_user}\"")
print(f"Push notification is {'enabled' if push_enabled else 'disabled'}")


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
    refresh_messages_in_this_room()


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
    print(50 * '-')
    for message in all_messages:
        print(f"\n{message['time']}\n{message['user']}: {message['message']}\n")
    if user_is_bot:
        # Grab the last message:
        with_message = all_messages[-1]['message']
        from_user = all_messages[-1]['user']
        bot_respond_to_message(from_user, with_message)
    print(50 * '-')


# After we have connected the chat as the user we need to join the room provided in the terminal
# If none was provided then we will just simply force the user to create a room:
join(arguments.room)


# When an user has joined a room we should start listening for live messages:
# For this we start a thread:
def live_messages():
    while True:
        try:
            room = client.recv(1024).decode('utf8')  # Receive the room from socket
            if active_room == room:  # First check if the room has happened in the active room
                refresh_messages_in_this_room()
            elif push_enabled:  # Then check if push has been enabled
                user_info, c = User.get(active_user)  # Get information about active user:
                unread_messages = user_info.get('unread-messages', None)  # Get the unread messages
                if unread_messages is not None:
                    number_of_unread = unread_messages.get(room, None)  # Grab the number in given room
                    if number_of_unread is not None:
                        # Print notification to the user
                        print(f"You have {number_of_unread} unread messages in {room}")
                    else:
                        print(f"New activity in {room}")  # In case if we're not able to get the desired number
                else:
                    print(f"New activity in {room}")  # In case we do not get the desired dictionary
        except (requests.ConnectionError, ConnectionResetError):
            print(f"Lost connection to the API server. Exiting the program!")
            break


# We must also be able to send messages:
def send_messages():
    while True:
        message = ''  # Initializing message variable
        try:
            message = input('').strip()
        except EOFError:
            exit_program()
        # Only non-bot users can use this thread to send messages:
        if not commands(message) and not user_is_bot and message:
            Message.send(active_room, active_user, message)  # Send the message via API

            room_users, c = Room.get_all_users(active_room, active_user)  # GET users in this room from API
            data = pickle.dumps((active_room, room_users))  # Convert tuple to bytes
            client.send(data)  # Send data through socket


def room_info(rooms: list):
    if len(rooms) == 0:
        rooms = [active_room]
    for room in rooms:
        r, c = Room.get(room, active_user)
        if c == 404:
            print(f"\nRoom with room name \"{active_room}\" does not exists...\n")
        else:
            print(f"\n{json.dumps(r, indent=2)}\n")


# Define commands so we can navigate and interact with the program:
def commands(cmd: str):
    cmds = {
        '/help': None,
        '/join': join,
        '/exit': exit_program,
        '/toggle_push': toggle_push_notification,
        '/room_info': room_info
    }

    help_list = {
        '/join': "/join [room...] to join another room",
        '/exit': "/exit to exit the program",
        '/toggle_push': "/toggle_push to turn on or off push-notification",
        '/room_info': "/room_info [room...] to display information about current active room"
    }

    # Parse the incoming string:
    # Convert everything to lowercase and split
    word_list = cmd.lower().split()
    if len(word_list) == 0:
        return False

    cmd = word_list.pop(0)

    if cmd in cmds:
        if cmd == '/help':
            print(json.dumps(help_list, indent=1))
        else:
            cmds[cmd](word_list)
        return True
    return False


def exit_program(void=None):
    print("Exiting program!")
    abort()


def toggle_push_notification(void=None):
    global push_enabled
    push_enabled = not push_enabled
    print(f"Push notifications has now been {'enabled' if push_enabled else 'disabled'}")


# Start a thread for live messages:
live_message_thread = Thread(target=live_messages)
live_message_thread.start()

# Start a thread for sending messages:
send_message_thread = Thread(target=send_messages, daemon=True)
send_message_thread.start()
