from flask import Flask
from flask_restful import Api, Resource, reqparse, abort, inputs
from datetime import datetime
from socket import socket, SOL_SOCKET, SO_REUSEADDR, AF_INET, SOCK_STREAM
from threading import Thread
from time import sleep
import pickle

app = Flask(__name__)
api = Api(app)

users = {}
rooms = {}

clients = {}


def abort_if_not_exists(some_id: str, iterable: iter, abort_message: str):
    if some_id not in iterable:
        abort(404, message=abort_message)


def abort_if_exists(some_id: str, iterable: iter, abort_message: str):
    if some_id in iterable:
        abort(409, message=abort_message)


# Defining a global restriction; only registered members can perform requests other than registering:
# Return 403: forbidden
def permission_denied(requester: str, room: str = None):
    if requester not in users:
        abort(403, message=f"\"{requester}\" is not a registered user. Permission for request has been denied!")
    if room:
        if requester not in rooms[room]['users']:
            abort(403, message=f"\"{requester}\" is not a member of {room}. Permission for request has been denied!")


class Users(Resource):
    def get(self, user_id: str = None) -> (dict, int):
        # checking global restriction:
        requester = reqparse.RequestParser().add_argument('requester', type=str, required=True).parse_args()
        permission_denied(requester['requester'])
        # Check if any user id has been provided
        if user_id:  # route = "/api/user/<string:user_id>"
            if not user_id.strip():
                return {'message': f"User id is required to fetch a user"}, 400  # Bad request
            # Check if specified user id exists
            abort_if_not_exists(user_id, users, f"Cannot find user with user id \"{user_id}\"")

            user_info = users[user_id].copy()

            # If the requester is not the same as the queried user id we don't need to include the unread-messages
            if requester['requester'] != user_id:
                user_info.pop('unread-messages', None)

            # Return json format of user
            return user_info, 200  # code 200 = OK

        # If no user id has been provided return the whole list as json format
        return users, 200  # code 200 = OK

    def post(self) -> (dict, int):
        # Collect necessary data to create a user {'username': user_id}
        user = reqparse.RequestParser() \
            .add_argument('username', type=str, required=True) \
            .add_argument('rooms', type=list, default=[]) \
            .add_argument('unread-messages', type=dict, default={}) \
            .parse_args(strict=True)

        if not user['username'].strip():
            return {'message': f"Username cannot be empty or blank!"}, 400  # Bad request

        # Check if the user already exists
        abort_if_exists(
            user['username'], users,
            f"\"{user['username']}\" already exists!"
        )  # 409

        # Add the new user to users:
        users.update({user['username']: user})

        # Return the created user in json format
        return {user['username']: user}, 201  # created

    def delete(self, user_id: str) -> (dict, int):
        # checking global restriction:
        requester = reqparse.RequestParser().add_argument('requester', type=str, required=True).parse_args()
        permission_denied(requester['requester'])

        # Adding security layer: Request to delete a user can only be performed by the user themselves:
        if requester['requester'] != user_id:
            return {'message': "Permission denied to deregister another user"}, 451

        # Remove and return the user id, None is returned as default value to avoid KeyError
        return users.pop(user_id, None), 200  # OK


# Add the class to route
api.add_resource(Users, "/api/users", "/api/user/<string:user_id>")


class ChatRooms(Resource):
    # Gets room with room_id.
    # Returns either a key-value pair, or an array of key-value pairs.
    def get(self, room_id: str = None) -> (dict, int):
        # checking global restriction:
        requester = reqparse.RequestParser().add_argument('requester', type=str, required=True).parse_args()
        permission_denied(requester['requester'])

        if room_id:  # route = "/api/room/<string:room_id>"
            # Check if room id exists:
            abort_if_not_exists(room_id, rooms, f"Cannot find room with room id {room_id}!")

            # Return a room without the messages inside that room:
            room_info = rooms[room_id].copy()
            room_info.pop('messages', None)
            return room_info, 200  # OK

        # As there are potential for a lot of messages in each room we will only return a list of rooms together
        # With the users in these rooms
        all_rooms = {
            k: {
                'creator': v['creator'],
                'users': v['users']
            } for (k, v) in rooms.items()
        }
        return all_rooms, 200  # OK

    # Adds room with room_id
    def post(self) -> (dict, int):
        # Retrieve data
        room = reqparse.RequestParser() \
            .add_argument('name', type=str, required=True) \
            .add_argument('creator', type=str, required=True) \
            .add_argument('users', type=list, default=[]) \
            .add_argument('messages', type=list, default=[]) \
            .parse_args()

        # Checking global restriction:
        permission_denied(room['creator'])

        # Abort if the room already exists
        abort_if_exists(room['name'], rooms, f"{room['name']} already exists!")  # 409

        # We will also by default add creator as a user of this room:
        creator = room['creator']
        room['users'].append(creator)
        # Thus, also add the room id to the list of rooms of the user:
        users[creator]['rooms'].append(room['name'])
        users[creator]['unread-messages'].update({room['name']: 0})

        # Add this room to our dictionary with name as id
        rooms.update({room['name']: room})
        # Return the room as json format
        return room, 201  # Created


api.add_resource(ChatRooms, "/api/rooms", "/api/room/<string:room_id>")


class RoomUsers(Resource):
    def get(self, room_id: str) -> (list, int):
        # checking global restriction:
        requester = reqparse.RequestParser().add_argument('requester', type=str, required=True).parse_args()
        permission_denied(requester['requester'])

        # Check if room_id exists
        abort_if_not_exists(room_id, rooms, f"Unable to find the room with room id {room_id}!")

        # Return json format of all the users in this room
        return rooms[room_id]['users'], 200

    def post(self, room_id: str) -> (list, int):
        # checking global restriction:
        requester = reqparse.RequestParser().add_argument('requester', type=str, required=True).parse_args()
        permission_denied(requester['requester'])
        # Check if room_id exists
        abort_if_not_exists(room_id, rooms, f"Cannot find room with room id {room_id}!")  # 404

        # Since we have checked that the requester is a registered user and we have also checked
        # that the room exists we will then allow the requester to join the room:
        user = requester['requester']

        # If the user is not a member of the room we will append the user to the list of users
        if user not in rooms[room_id]['users']:
            rooms[room_id]['users'].append(user)
            # We will also add the room to the list of rooms the user is a member of
            users[user]['rooms'].append(room_id)
            users[user]['unread-messages'].update({room_id: 0})

        # Return the list of users in this room:
        return rooms[room_id]['users'], 200  # OK


api.add_resource(RoomUsers, "/api/room/<string:room_id>/users")


class Messages(Resource):  # Take a look at this
    def get(self, room_id: str, user_id: str = None) -> (list, int):
        # Check global restrictions:
        requester = reqparse.RequestParser().add_argument('requester', type=str, required=True).parse_args()
        permission_denied(requester['requester'], room=room_id)

        # Check if bot room_id
        abort_if_not_exists(room_id, rooms, f"Cannot find room with room id {room_id}")

        if not user_id:  # route = /api/room/<string:room_id>/messages
            user = requester['requester']

            # Set the requesters unread messages in that room to 0, crucial for push-notifications
            users[user]['unread-messages'].update({room_id: 0})

            # Return all messages from requested the room
            return rooms[room_id]['messages'], 200  # Ok

        # If a user id was provided we must then first check if the user
        abort_if_not_exists(user_id, rooms[room_id]['users'], f"Cannot find user with user id {user_id} in {room_id}!")
        # Get a list of all messages from a room:
        messages_in_this_room = rooms[room_id]['messages']

        # Filter through all the messages in this room and return all the messages from provided user_id
        messages_from_user = filter(lambda message: message['user'] == user_id, messages_in_this_room)
        return list(messages_from_user), 200  # Ok

    def post(self, room_id: str, user_id: str) -> (dict, int):
        # Check if room exists
        abort_if_not_exists(room_id, rooms, f"Cannot find room with room id \"{room_id}\"!")

        # Then check if user_id has permission to post messages in this room:
        # Deny the post request if user is not a member of the room:
        permission_denied(requester=user_id, room=room_id)

        # Create a message json
        now = datetime.now()
        message = reqparse.RequestParser() \
            .add_argument('user', type=str, default=user_id) \
            .add_argument('room', type=str, default=room_id) \
            .add_argument('time', type=str, default=now.strftime("%c")) \
            .add_argument('message', type=str, required=True) \
            .parse_args()

        # Add the message inside this room
        rooms[room_id]['messages'].append(message)

        # Update unread messages of all users inside this room:
        # Crucial for push-notifications
        for user in rooms[room_id]['users']:
            users[user]['unread-messages'][room_id] += 1

        # Return the message
        return message, 200


api.add_resource(
    Messages,
    "/api/room/<string:room_id>/messages",
    "/api/room/<string:room_id>/<string:user_id>/messages"
)


def push_notification(username, client):
    while True:
        try:
            data = client.recv(1024)  # Receive data from client send_message() function
            room, room_users = pickle.loads(data)
            for user in room_users:
                user_client = clients.get(user, None)
                if user_client is not None:
                    user_client.send(room.encode('utf8'))  # Send room id of the new activity
        except (EOFError, ConnectionResetError):
            clients.pop(username, None)
            break


# Creating a socket just for listening:
def listening_socket():
    service = socket(AF_INET, SOCK_STREAM)
    service.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
    service.bind(('127.0.0.1', 5005))
    service.listen()
    while True:
        client, addr = service.accept()
        # Assume that the user has been added:
        # We wait for the client to send the socket the user_id: str
        username = client.recv(1024).decode('utf8')
        if username in clients:
            client.close()
        else:
            clients.update({username: client})

            # Start a thread for this client to push notifications to other clients:
            push_thread = Thread(target=push_notification, args=(username, client))
            push_thread.start()


if __name__ == "__main__":
    listening_thread = Thread(target=listening_socket, daemon=True)
    listening_thread.start()
    app.run(debug=True)
