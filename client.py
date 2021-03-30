from bots import *
from connections import User, Room, Message
import sys
from socket import socket, SHUT_RDWR
from threading import Thread
import time
from datetime import datetime

# Replace with input()
if len(sys.argv) == 3:

    user_id = sys.argv[1]
    room = sys.argv[2]
else:
    user_id = input("Please enter username: ")

is_bot = False
if user_id in ["JoeBot", "AnnaBot", "PeterBot"]:
    is_bot = True

active_room = None


# Check user
def sign_in():
    global user_id

    response, code = User.add(user_id)
    print(response)
    print(code)

    if code != 201:
        user, code = User.get(user_id)
        user_id = user['username']


def join_room():
    global active_room

    available_rooms, code = Room.get_all(user_id)

    if is_bot:
        room_id = room
    else:
        print(f"Available rooms to join: \n {list(available_rooms)}")
        room_id = input(f"Which room do you want to join? ")

    join_this_room, code = Room.join(room_id, user_id)

    if code == 404:
        if is_bot:
            Room.add(room_id, user_id)
            join_this_room, code = Room.join(room_id, user_id)

        else:
            print(join_this_room['message'])
            if input(f"Do you want to create a new room \"{room_id}\"? [y/n] ") == 'y':
                Room.add(room_id, user_id)
                join_this_room, code = Room.join(room_id, user_id)

    if code == 409 or code == 200:
        active_room = room_id
        message_history, code = Message.get_all_from_room(active_room, user_id)
        print(f" You are now in room {active_room}")
        for message in message_history:
            print(f"{message['user']}: {message['message']} \t {message['time']}")


def send_message():
    global user_id
    global active_room

    user_in_rooms = []

    if is_bot:
        rooms, code = Room.get_all(user_id)
        print(rooms)
        for x in rooms:
            users, code = Room.get_all_users(x, user_id)
            if user_id in users:
                user_in_rooms.append(x)

        for x in user_in_rooms:
            if active_room == x:
                Message.send(active_room, user_id, eval(user_id)())
            else:
                Room.join(x, user_id)
                active_room = x

    while True:
        message_input = input()
        if not command(message_input):
            if active_room is None:
                print(f"You have to join a room to send a message!")
                join_room()
            else:
                Message.send(active_room, user_id, message_input)


def command(cmd: str) -> bool:
    commands = {
        '/join': join_room,
        '/exit': sys.exit,
    }

    if cmd.strip() in commands:
        commands[cmd.strip()]()
        return True
    return False


sign_in()
Room.add('General', user_id)
join_room()
send_message()
