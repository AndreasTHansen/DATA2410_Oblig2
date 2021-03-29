from flask import Flask
from flask_restful import Api, Resource, reqparse, abort, inputs
from datetime import datetime
from socket import socket, SHUT_RDWR
from threading import Thread

app = Flask(__name__)
api = Api(app)

users = {}
rooms = {}


def abort_if_not_exists(some_id: str, iterable: iter, abort_message: str):
    if some_id not in iterable:
        abort(404, message=abort_message)


def abort_if_exists(some_id: str, iterable: iter, abort_message: str):
    if some_id in iterable:
        abort(409, message=abort_message)


class Users(Resource):
    def get(self, user_id: str = None) -> (dict, int):
        # Check if any user id has been provided
        if user_id:
            if not user_id.strip():
                return {'message': f"User id is required to fetch a user"}, 400  # Bad request
            # Check if specified user id exists
            abort_if_not_exists(user_id, users, f"Cannot find user with user id \"{user_id}\"")

            # Return json format of user
            return users[user_id], 200  # code 200 = OK

        # If no user id has been provided return the whole list as json format
        return users, 200  # code 200 = OK

    def post(self) -> (dict, int):
        # Collect necessary data to create a user {'username': user_id}
        user = reqparse.RequestParser() \
            .add_argument('username', type=str, required=True) \
            .add_argument('push-notification', type=inputs.boolean, required=True) \
            .add_argument('rooms', type=list, default=[]) \
            .add_argument('unread-messages', type=dict, default={}) \
            .parse_args(strict=True)

        if not user['username'].strip():
            return {'message': f"Username cannot be empty or blank!"}, 400  # Bad request

        # Check if the user already exists
        abort_if_exists(
            user['username'], users,
            f"\"{user['username']}\" already exists!"
        )

        # Add the new user to users:
        users.update({user['username']: user})

        # Return the created user in json format
        return {user['username']: user}, 201  # created

    def delete(self, user_id: str = None) -> (dict, int):
        # A user id must be provided to delete a user
        if not user_id:
            # If no user id has been provided return a string to prompting the caller to provide user id
            return {'message': "User id required to delete a user"}, 400  # bad request

        if not user_id.strip():
            return {'message': "User id required to delete a user"}, 400  # bad request

        # Check if provided user id exists:
        abort_if_not_exists(user_id, users, f"Cannot find user with user id {user_id}!")

        # Remove and return the user id, None is returned as default value to avoid KeyError
        return users.pop(user_id, None), 200  # OK

    def patch(self, user_id: str) -> (dict, int):
        abort_if_not_exists(user_id, users, f"Cannot find user with user id \"{user_id}\"!")
        patched = reqparse.RequestParser() \
            .add_argument('username', type=str) \
            .add_argument('push-notification', type=inputs.boolean) \
            .add_argument('rooms', type=list) \
            .add_argument('unread-messages', type=dict) \
            .parse_args()

        for key in patched:
            if patched[key] is not None:
                users[user_id].update({key: patched[key]})

        return users[user_id], 200  # OK


# Add the class to route
api.add_resource(Users, "/api/users", "/api/user/<string:user_id>")


class ChatRooms(Resource):
    # Gets room with room_id.
    # Returns either a key-value pair, or an array of key-value pairs.
    def get(self, room_id: str = None) -> (dict, int):
        if room_id:  # Check if room id has been provided
            # Check if room id exists:
            abort_if_not_exists(room_id, rooms, f"Cannot find room with room id {room_id}!")

            # Return this room in json format
            return rooms[room_id], 200  # OK

        # As there are potential for a lot of messages in each room we will only return a list of rooms together
        # With the users in these rooms
        all_rooms = {k: v['users'] for (k, v) in rooms.items()}
        return all_rooms, 200  # OK

    # Adds room with room_id
    def post(self) -> (dict, int):
        # Retrieve data
        room = reqparse.RequestParser().add_argument('name', type=str, required=True).parse_args()
        # Abort if the room already exists
        abort_if_exists(room['name'], rooms, f"{room['name']} already exists!")  # 409
        # Create a room based on the name given
        new_room = {room['name']: {
            'name': room['name'],
            'users': [],
            'messages': [],
        }}
        # Add this room to our dictionary
        rooms.update(new_room)
        # Return the room as json format
        return new_room, 201  # Created


api.add_resource(ChatRooms, "/api/rooms", "/api/room/<string:room_id>")


class RoomUsers(Resource):
    def get(self, room_id: str) -> (list, int):
        # Check if room_id exists
        abort_if_not_exists(room_id, rooms, f"Unable to find the room with room id {room_id}!")

        # Return json format of all the users in this room
        return rooms[room_id]['users'], 200

    def post(self, room_id: str) -> (list, int):
        # Check if room_id exists
        abort_if_not_exists(room_id, rooms, f"Cannot find room with room id {room_id}!")  # 404

        # To join a room append a user to the list of users in that room:
        # First check if the user is registered:
        user = reqparse.RequestParser().add_argument('user', type=str, required=True).parse_args()
        user = user['user']
        abort_if_not_exists(user, users, f"Cannot find user with user id {user}!")

        # Then check if the user is already in this room
        abort_if_exists(user, rooms[room_id]['users'], f"{user} is already a member of {room_id}")  # 409

        # Add user to users list in this room
        rooms[room_id]['users'].append(user)
        # Add room id to rooms list for this user
        users[user]['rooms'].append(room_id)
        users[user]['unread-messages'].update({room_id: 0})

        return rooms[room_id]['users'], 200


api.add_resource(RoomUsers, "/api/room/<string:room_id>/users")


class Messages(Resource):  # Take a look at this
    def get(self, room_id: str, user_id: str = None) -> (list, int):
        # Check if bot room_id
        abort_if_not_exists(room_id, rooms, f"Cannot find room with room id {room_id}")

        if not user_id:  # If no user id was provided
            # Get the user that requests the message:
            user = reqparse.RequestParser().add_argument('user', type=str, required=True).parse_args()
            # Check if the requested user is in the room:
            abort_if_not_exists(
                user['user'], rooms[room_id]['users'],
                f"Permission denied for {user} to get messages from {room_id}!"
            )

            users[user['user']]['unread-messages'].update({room_id: 0})

            # Return all messages from that room if the user is in the room
            return rooms[room_id]['messages'], 200  # Ok

        # If a user id was provided we must then first check if the user
        abort_if_not_exists(user_id, rooms[room_id]['users'], f"Cannot find user with user id {user_id} in {room_id}!")
        # Get a list of all messages from a room:
        messages_in_this_room = rooms[room_id]['messages']

        # Filter through all the messages in this room and return all the messages this provided user_id
        messages_from_user = filter(lambda message: message['user'] == user_id, messages_in_this_room)
        return list(messages_from_user), 200  # Ok

    def post(self, room_id: str, user_id: str) -> (dict, int):
        # Check if room and user exists
        abort_if_not_exists(room_id, rooms, f"Cannot find room with room id \"{room_id}\"!")
        abort_if_not_exists(user_id, users, f"Cannot find user with user id \"{user_id}\"!")

        # Also check if the user is member of the room
        abort_if_not_exists(
            user_id,
            rooms[room_id]['users'],
            f"user \"{user_id}\" cannot send messages in room \"{room_id}\"..."
        )

        now = datetime.now()
        message = reqparse.RequestParser() \
            .add_argument('user', type=str, default=user_id) \
            .add_argument('room', type=str, default=room_id) \
            .add_argument('time', type=str, default=now.strftime("%c")) \
            .add_argument('message', type=str, required=True) \
            .parse_args()

        rooms[room_id]['messages'].append(message)

        for user in rooms[room_id]['users']:
            users[user]['unread-messages'][room_id] += 1

        return message, 200


api.add_resource(
    Messages,
    "/api/room/<string:room_id>/messages",
    "/api/room/<string:room_id>/<string:user_id>/messages"
)

if __name__ == "__main__":
    app.run(debug=True)

    server = socket()
    server.bind(("127,0,0,1", 5000))
    server.listen()

    clients = {}


    def push(user):
        while users[user]['push-notification']:
            clients_unread_messages = clients[user]['unread-messages']
            users_unread_messages = users[user]['unread-messages']
            for room in user['rooms']:
                number_of_new_messages = users_unread_messages[room] - clients_unread_messages[room]
                if number_of_new_messages > 0:
                    clients[user]['client'] \
                        .send(f"You have {number_of_new_messages} unread messages in room \"{room}\"".encode('utf8'))
                elif number_of_new_messages < 0:
                    clients[user]['unread-messages'][room] = 0

        clients[user]['client'].shutdown(SHUT_RDWR)
        clients[user]['client'].close()
        clients.pop(user, None)



    while True:
        client, address = server.accept()
        username = client.recv(1024).decode('utf8')
        if users[username]['push-notification']:
            clients[username] = {
                'client': client,
                'unread-messages': users[username]['unread-messages']
            }
            Thread(target=push, args=(username,)).start()
