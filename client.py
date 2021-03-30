from connections import User, Room, Message
import sys
from socket import socket, SHUT_RDWR
from threading import Thread

# Replace with input()
user_id = sys.argv[1]
room = sys.argv[2]

is_bot = False
if user_id in ["Joe", "Anna", "Peter"]:
    is_bot = True

push_active = False
active_room = None


# Check user
def sign_in():
    global user_id
    global push_active

    response, code = User.get(user_id)

    if is_bot:

        # We only need to add the user, if it is a bot
        # Either user does not exist, or it already exists
        while code == 404 or code == 409:
            User.add(user_id)

    else:
        if not response['push-notification']:
            push_active = input(f"Do you want to turn on push notification? [y/n] ").strip() == 'y'
            if push_active:
                toggle_push_notification()

        if code == 404:
            print(response['message'])
            print(f"Registering {user_id} as a new user!")
            User.add(user_id, push_active)


Room.add('General', user_id)


def join_room():
    global active_room

    available_rooms, code = Room.get_all(user_id)
    print(f"Available rooms to join: \n {list(available_rooms)}")
    room_id = input(f"Which room do you want to join? ")
    join_this_room, code = Room.join(room_id, user_id)

    if code == 404:
        print(join_this_room['message'])
        if input(f"Do you want to create a new room \"{room_id}\"? [y/n] ") == 'y':
            Room.add(room_id, user_id)
            join_this_room, code = Room.join(room_id, user_id)

    if code == 409 or code == 200:
        active_room = room_id
        message_history, code = Message.get_all_from_room(active_room, user_id)
        for message in message_history:
            print(f"{message['user']}: {message['message']} \t {message['time']}")


def send_message():
    global user_id
    global active_room
    while True:
        message_input = input()
        if not command(message_input):
            if active_room is None:
                print(f"You have to join a room to send a message!")
                join_room()
            else:
                Message.send(active_room, user_id, message_input)


def listen_for_push(client):
    global push_active
    while push_active:
        message = client.recv(1024).decode('utf8')
        print(message)
    client.shutdown(SHUT_RDWR)
    client.close()


def toggle_push_notification():
    global push_active
    User.toggle_push(user_id)
    push_active = not push_active
    if push_active:
        client = socket()
        client.connect(("127.0.0.1", 5000))
        client.send(user_id.encode('utf8'))
        Thread(target=listen_for_push, args=(client,)).start()


def command(cmd: str) -> bool:
    commands = {
        '/join': join_room,
        '/exit': sys.exit,
        '/toggle_push': toggle_push_notification
    }

    if cmd.strip() in commands:
        commands[cmd.strip()]()
        return True
    return False


sign_in()
join_room()
send_message()
