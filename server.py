from flask import Flask
from flask_restful import Api, Resource, reqparse, abort
from json import dumps
from datetime import datetime

app = Flask(__name__)
api = Api(app)

users = {}
rooms = {}
messages = {}

json_indent = 1


def abort_if_not_exists(some_id, some_dict: dict, abort_message: str):
    if some_id not in some_dict:
        abort(404, message=abort_message)


def abort_if_exists(some_id, some_dict: dict, abort_message: str):
    if some_id in some_dict:
        abort(409, message=abort_message)


class User(Resource):
    def get(self, user_id=None) -> (str, int):
        if user_id:
            abort_if_not_exists(user_id, users, f"Cannot find {user_id}")
            return dumps(users[user_id], indent=json_indent), 200
        return dumps(users, indent=json_indent), 200

    def post(self, user_id=None) -> (str, int):
        if not user_id:
            return f"User id required to post a new user", 400
        if user_id:
            abort_if_exists(user_id, users, f"A user with user id {user_id} already exists")
            users[user_id] = reqparse.RequestParser() \
                .add_argument('rooms', type=list, default=[]) \
                .parse_args(strict=True)
            return dumps(users[user_id], indent=json_indent), 201

    def delete(self, user_id=None) -> (str, int):
        if not user_id:
            return f"A user id is required to delete a user", 400

        deleted_user = users.pop(user_id, None)

        if deleted_user is None:
            return f"Could not find {user_id} to delete", 404
        return dumps(deleted_user, indent=json_indent), 200


api.add_resource(User, "/api/user/", "/api/user/<string:user_id>")


class ChatRoom(Resource):
    # Gets room with room_id.
    # Returns either a key-value pair, or an array of key-value pairs.
    def get(self, room_id=None):
        if room_id:
            abort_if_not_exists(room_id, rooms, "Room does not exist")
            return rooms[room_id], 200
        return list(rooms.keys()), 200

    # Adds room with room_id
    def post(self, room_id=None):
        if not room_id:
            return f"Cannot create a room without a room id", 400
        abort_if_exists(room_id, rooms, "Room already exists")
        rooms[room_id] = reqparse.RequestParser() \
            .add_argument('name', type=str, required=True) \
            .add_argument('size', type=int, required=True) \
            .add_argument('users', type=list, default=[]) \
            .add_argument('messages', type=list, default=[]) \
            .parse_args()
        return rooms[room_id], 201


api.add_resource(ChatRoom, "/api/rooms/", "/api/rooms/<string:room_id>")


class RoomUsers(Resource):
    def get(self, room_id):
        abort_if_not_exists(room_id, rooms, f"Unable to find the room with room id {room_id}!")
        return dumps(rooms[room_id]['users']), 200

    def post(self, room_id, user_id):
        abort_if_not_exists(room_id, rooms, f"Cannot find room with room id {room_id}")
        abort_if_not_exists(user_id, users, f"Cannot find user with user id {user_id}")
        rooms[room_id]['users'].append(user_id)
        users[user_id]['rooms'].append(room_id)
        return dumps(rooms[room_id]['users']), 200

    # Adding a delete request so a user can leave a chat room
    def delete(self, room_id, user_id):
        abort_if_not_exists(room_id, rooms, f"Cannot find room with room id {room_id}")
        abort_if_not_exists(user_id, users, f"Cannot find user with user id {user_id}")
        # Since every user_id's should be unique we do not need to have any concern when using remove on an array:
        rooms[room_id]['users'].remove(user_id)
        users[user_id]['rooms'].remove(room_id)
        return dumps(rooms[room_id]['users']), 200


api.add_resource(RoomUsers, "/api/room/<string:room_id>/users", "/api/room/<string:room_id>/users/<string:user_id>")


class RoomMessage(Resource):
    def get(self, room_id):
        abort_if_not_exists(room_id, rooms, f"Cannot find room with room id {room_id}!")
        return dumps(rooms[room_id]['messages'], indent=json_indent), 200


api.add_resource(RoomMessage, "/api/rooms/<room-id>/messages")


class UserMessage(Resource):
    def get(self, room_id, user_id):
        abort_if_not_exists(room_id, rooms, f"Cannot find room with room id {room_id}")
        abort_if_not_exists(user_id, users, f"Cannot find user with user id {user_id}!")

        # Get a list of all messages from a room:
        messages_in_this_room = rooms[room_id]['messages']
        messages_from_user = filter(lambda message: message['user'] == user_id, messages_in_this_room)
        return dumps(list(messages_from_user), indent=json_indent), 200

    def post(self, room_id, user_id):
        abort_if_not_exists(room_id, rooms, f"Cannot find room with room id {room_id}")
        abort_if_not_exists(user_id, users, f"Cannot find user with user id {user_id}!")

        now = datetime.now()
        message = reqparse.RequestParser() \
            .add_argument('user', type=str, default=user_id) \
            .add_argument('room', type=str, default=room_id) \
            .add_argument('time', type=str, default=now.strftime("%c")) \
            .add_argument('message', type=str, required=True) \
            .parse_args()

        rooms[room_id]['messages'].append(message)

        return dumps(message, indent=json_indent), 200


api.add_resource(
    UserMessage,
    "api/rooms/<room-id>/<user-id>/messages",
    "api/rooms/<room-id>/<user-id>/messages/<string:message-id>"
)

if __name__ == "__main__":
    app.run(debug=True)
