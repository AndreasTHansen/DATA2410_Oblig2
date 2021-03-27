from requests import get, post, delete

URL = "http://127.0.0.1:5000/api"


class User:
    @staticmethod
    def get_all() -> (dict, int):
        route = URL + '/users'
        response = get(route)
        return response.json(), response.status_code

    @staticmethod
    def add(user_id: str) -> (dict, int):
        route = URL + f'/users'
        response = post(route, {'username': user_id})
        return response.json(), response.status_code

    @staticmethod
    def get(user_id: str) -> (dict, int):
        route = URL + f'/user/{user_id}'
        response = get(route)
        return response.json(), response.status_code

    @staticmethod
    def delete(user_id: str) -> (dict, int):
        route = URL + f'/user/{user_id}'
        response = delete(route)
        return response.json(), response.status_code


class Room:
    @staticmethod
    def get_all() -> (dict, int):
        route = URL + '/rooms'
        response = get(route)
        return response.json(), response.status_code

    @staticmethod
    def add(room_id: str) -> (dict, int):
        route = URL + f'/rooms'
        response = post(route, {'name': room_id})
        return response.json(), response.status_code

    @staticmethod
    def get(room_id: str) -> (dict, int):
        route = URL + f'/room/{room_id}'
        response = get(route)
        return response.json(), response.status_code

    @staticmethod
    def get_all_room_users(room_id: str) -> (dict, int):
        route = URL + f'/room/{room_id}/users'
        response = get(route)
        return response.json(), response.status_code

    @staticmethod
    def join(room_id: str, user_id: str) -> (dict, int):
        route = URL + f'/room/{room_id}/users'
        response = post(route, {'user': user_id})
        return response.json(), response.status_code


class Message:
    @staticmethod
    def get_all(room_id: str, user_id: str) -> (dict, int):
        route = URL + f'/room/{room_id}/messages'
        response = get(route, {'user': user_id})
        return response.json(), response.status_code

    @staticmethod
    def get_all_from_user(room_id: str, user_id: str) -> (dict, int):
        route = URL + f'/room/{room_id}/{user_id}/messages'
        response = get(route)
        return response.json(), response.status_code

    @staticmethod
    def send(room_id: str, user_id: str, message: str) -> (dict, int):
        route = URL + f'/room/{room_id}/{user_id}/messages'
        response = post(route, {'message': message})
        return response.json(), response.status_code
