from connections import User, Room, Message
from json import dumps
from socket import socket
from sys import platform, argv, exit
from os import system, abort
from threading import Thread
from time import sleep

"""
As the program starts we want to fetch the user. First we want to try to add the user. If we get an error code we 
can then assume that the user is already registered. In that case we will just get the user and store the user_id
"""
active_user = argv[1]
client_is_alive = True
# First, we add the requested user:
response, code = User.add(active_user)

if code == 201:
    print(f"{active_user} is not registered. Registering a new user with username: {active_user}!")

# After verifying user we create a socket and tell the server socket that a new user has connected:
client = socket()
client.connect(('127.0.0.1', 5005))
client.send(active_user.encode('utf8'))

# After adding a user we shall prompt the user to join a room:
currently_all_available_rooms, code = Room.get_all(active_user)
if len(currently_all_available_rooms) == 0:
    print(f"Currently there are no available rooms to join")
    active_room = input(f"Create a new room, enter room name: ")
else:
    print(dumps(currently_all_available_rooms, indent=2))
    active_room = input(f"Enter the room name you want to join: ")

# Join the entered room name:
response, code = Room.join(active_room, active_user)
if code == 404:
    # If the user has entered a room that does not exists:
    # We create the entered room and make the active user its creator
    Room.add(active_room, active_user)
    print(f"{active_room} does not exists. Creating a new room with name \"{active_room}\"!")


# At this point the user has joined a room and can send messages. We will handle sending messages with threading:
def clear_console():
    if platform.__contains__('win'):
        system('cls')
    else:
        system('clear')


# First we want to print out all messages that has been sent in that room:
def print_message_history():
    clear_console()
    # Get all the messages inside that room:
    all_messages, code = Message.get_all_from_room(active_room, active_user)
    for message in all_messages:
        print(f"{message['user']}: {message['message']} \t\t {message['time']}")


def send_messages():
    global client_is_alive
    print_message_history()
    while client_is_alive:
        sleep(0.1)
        print(30 * '-')
        message = input('').strip()
        if not commands(message) and message:
            Message.send(active_room, active_user, message)
        else:
            clear_console()
            print_message_history()


# We will also listen for any push_notifications:
def push_notifications():
    global client_is_alive
    while client_is_alive:
        # Server will first send us a room_id
        try:
            room_id = client.recv(1024).decode('utf8')
            unread = client.recv(1024).decode('utf8')
            push_on = int(client.recv(1024).decode('utf8'))
            if active_room == room_id:
                print_message_history()
            elif push_on:
                print(f"You have {unread} messages in room \"{room_id}\"")
        except ConnectionResetError:
            clear_console()
            print("Lost contact with the server!")
            exit_program()
            break


def select_new_active_room():
    global active_room
    all_rooms, code = Room.get_all(active_user)
    print(dumps(all_rooms, indent=2))
    active_room = input("Which room do you want to join? ")
    r, c = Room.join(active_room, active_user)
    if c == 404:
        Room.add(active_room, active_user)
    print_message_history()


def exit_program():
    global client_is_alive
    client_is_alive = False
    print("Exiting program!")
    abort()


def toggle_push_notification():
    User.toggle_push(active_user)


def commands(cmd: str):
    cmds = {
        '/join': select_new_active_room,
        '/exit': exit_program,
        '/toggle_push': toggle_push_notification
    }
    if cmd in cmds:
        cmds[cmd]()
        return True
    return False


push_thread = Thread(target=push_notifications, daemon=True)
push_thread.start()
send_message_thread = Thread(target=send_messages)
send_message_thread.start()
