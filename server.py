from flask import Flask
from flask_restful import Api, Resource, reqparse, abort

app = Flask(__name__)
api = Api(app)

users = {}


def abort_if_not_exists(some_id, some_dict: dict, abort_message: str):
    if some_id not in some_dict:
        abort(404, message=abort_message)


def abort_if_exists(some_id, some_dict: dict, abort_message: str):
    if some_id in some_dict:
        abort(409, message=abort_message)


class User(Resource):
    def get(self, user_id):
        if user_id == 'all':
            return users
        abort_if_not_exists(
            user_id,
            users,
            f"Cannot find user with user id: {user_id} among registered users"
        )
        return users[user_id]

    def post(self, user_id):
        if user_id:
            abort_if_exists(user_id, users, f"A user with {user_id} already exists")
            users[user_id] = reqparse.RequestParser()\
                .add_argument("Name", type=str, required=True)\
                .add_argument("Age", type=int, required=True)\
                .add_argument("Email", type=str, required=True)\
                .parse_args()
            return users[user_id], 201

    def put(self, user_id):
        if user_id in users:
            users[user_id] = reqparse.RequestParser() \
                .add_argument("Name", type=str, required=True) \
                .add_argument("Age", type=int, required=True) \
                .add_argument("Email", type=str, required=True) \
                .parse_args()
            return users[user_id], 200
        else:
            self.post(user_id)

    def delete(self, user_id):
        if users.pop(user_id, ''):
            return f"Could not find {user_id} to delete", 404
        return f"{user_id} has been successfully deleted", 200


api.add_resource(User, "/api/user/<string:user_id>")

if __name__ == "__main__":
    app.run(debug=True)
