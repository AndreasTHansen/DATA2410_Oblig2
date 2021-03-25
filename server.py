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
        if user_id:
            pass


if __name__ == "__main__":
    app.run(debug=True)
