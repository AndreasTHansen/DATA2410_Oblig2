from flask import Flask
from flask_restful import Api, Resource, reqparse, abort

app = Flask(__name__)
api = Api(app)

users = {}
rooms = {}


def abort_if_not_exists(some_id, some_dict: dict, abort_message: str):
    if some_id not in some_dict:
        abort(404, message=abort_message)


def abort_if_exists(some_id, some_dict: dict, abort_message: str):
    if some_id in some_dict:
        abort(409, message=abort_message)


class User(Resource):
    def get(self, user_id=None):
        if user_id:
            abort_if_not_exists(user_id, users, f"Cannot find {user_id}")
            return users[user_id], 200
        return list(users.keys()), 200

    def post(self, user_id=None):
        if not user_id:
            return f"User id required to post a new user", 400
        if user_id:
            abort_if_exists(user_id, users, f"A user with user id {user_id} already exists")
            users[user_id] = reqparse.RequestParser() \
                .add_argument("Name", type=str, required=True) \
                .add_argument("Age", type=int, required=True) \
                .add_argument("Email", type=str, required=True) \
                .parse_args()
            return users[user_id], 201

    def delete(self, user_id=None):
        if not user_id:
            return f"User id is required to delete a user", 400
        if users.pop(user_id, True):
            return f"Could not find {user_id} to delete", 404
        return f"{user_id} has been successfully deleted", 200


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
            .add_argument('Name', type=str, required=True) \
            .add_argument('Size', type=int, required=True) \
            .add_argument('Users', type=dict, default={}) \
            .parse_args()
        return rooms[room_id], 201


api.add_resource(ChatRoom, "/api/rooms/", "/api/rooms/<string:room_id>")


class RoomUsers(Resource):
    def get(self, room_id):
        abort_if_not_exists(room_id, rooms, f"Unable to find the room with room id {room_id}")
        return rooms[room_id]['Users']

    def post(self, room_id, user_id=None):
        abort_if_not_exists(room_id, rooms, f"Cannot find room with room id {room_id}")
        if not user_id:
            pass
        abort_if_not_exists(user_id, users, f"Cannot find user with user id {user_id}")


if __name__ == "__main__":
    app.run(debug=True)
