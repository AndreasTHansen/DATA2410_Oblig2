from requests import get, post, patch, delete

URL = "http://127.0.0.1:5000/api"


class User:
    @staticmethod
    def get_all(requester: str) -> (dict, int):
        route = URL + '/users'
        response = get(route, {'requester': requester})
        return response.json(), response.status_code

    @staticmethod
    def add(user_id: str) -> (dict, int):
        route = URL + f'/users'
        response = post(route, {'username': user_id})
        return response.json(), response.status_code

    @staticmethod
    def get(user_id: str, requester: str = None) -> (dict, int):
        route = URL + f'/user/{user_id}'
        req = user_id if requester is None else requester
        print(f"Requester: {req}")
        response = get(route, {
            'requester': req
        })
        return response.json(), response.status_code

    @staticmethod
    def toggle_push(user_id: str):
        route = URL + f'/user/{user_id}'
        user = get(route, {'requester': user_id}).json()
        response = patch(route, {'requester': user_id, 'push-notification': not user['push-notification']})
        return response.json(), response.status_code

    @staticmethod
    def delete(user_id: str) -> (dict, int):
        route = URL + f'/user/{user_id}'
        response = delete(route, data={'requester': user_id})
        return response.json(), response.status_code


class Room:
    @staticmethod
    def get_all(requester: str) -> (dict, int):
        route = URL + '/rooms'
        response = get(route, {'requester': requester})
        return response.json(), response.status_code

    @staticmethod
    def add(room_id: str, creator: str) -> (dict, int):
        route = URL + f'/rooms'
        response = post(route, {'creator': creator, 'name': room_id})
        return response.json(), response.status_code

    @staticmethod
    def get(room_id, requester: str) -> (dict, int):
        route = URL + f'/room/{room_id}'
        response = get(route, {'requester': requester})
        return response.json(), response.status_code

    @staticmethod
    def get_all_users(room_id, requester: str) -> (dict, int):
        route = URL + f'/room/{room_id}/users'
        response = get(route, {'requester': requester})
        return response.json(), response.status_code

    @staticmethod
    def join(room_id: str, requester: str) -> (dict, int):
        route = URL + f'/room/{room_id}/users'
        response = post(route, {'requester': requester})
        return response.json(), response.status_code


class Message:
    @staticmethod
    def get_all_from_room(room_id: str = None, requester: str = None) -> (dict, int):
        if room_id and requester:
            route = URL + f'/room/{room_id}/messages'
            response = get(route, {'requester': requester})
            return response.json(), response.status_code
        raise ValueError(f"Must specify room and requester")

    @staticmethod
    def get_all_from_user(room_id: str, user_id: str, requester: str = None) -> (dict, int):
        route = URL + f'/room/{room_id}/{user_id}/messages'
        response = get(route, {
            'requester': user_id if requester is None else requester
        })
        return response.json(), response.status_code

    @staticmethod
    def send(room_id, user_id: str, message: str) -> (dict, int):
        route = URL + f'/room/{room_id}/{user_id}/messages'
        response = post(route, {'message': message})
        return response.json(), response.status_code
