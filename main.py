from requests import get, post, delete
from server import Users, ChatRooms, RoomUsers, Messages
from random import choice


def route(resource, user_id: str = None, room_id: str = None) -> str or None:
    resource = resource.__name__.lower()
    url = "http://127.0.0.1:5000"
    routes = {
        'users':
            f"/api/user" + ('s' if user_id is None else f"/{user_id}"),
        'chatrooms':
            f"/api/room" + ('s' if room_id is None else f"/{room_id}"),
        'roomusers':
            f"/api/room/{room_id}/users",
        'messages':
            f"/api/room/{room_id}/" + ('messages' if user_id is None else f"{user_id}/messages")
    }

    result = url + routes[resource]
    if result.__contains__("None"):
        return None
    return result


def get_test(resource, user_id: str = None, room_id: str = None) -> None:
    get_route = route(resource, user_id, room_id)
    print(30 * "-")
    print(f"/// GET test on {resource.__name__} with user_id = {user_id} and room_id = {room_id} ///")

    if get_route is None:
        raise IOError(f"Some parameters are missing to perform the required GET test")
    print(f"route = {get_route}")
    response = get(get_route)
    print(f"{response.json()}, status code = {response.status_code}")
    print(30 * "-")


def post_test(resource, user_id: str = None, room_id: str = None, data: dict = None) -> None:
    post_route = route(resource, user_id, room_id)
    print(30 * "-")
    print(f"/// POST test on {resource.__name__} with user_id = {user_id} and room_id = {room_id}")

    if post_route is None:
        raise IOError(f"Some parameters are missing to perform the required POST test")
    if resource != Users and resource != ChatRooms and data is None:
        raise IOError(f"data is required for {resource.__name__}")
    print(f"route = {post_route}")
    if data is not None:
        print(f"data = {str(data)}")
    response = post(post_route, data)
    print(f"{response.json()}, status code = {response.status_code}")
    print(30 * "-")


def delete_test(resource, user_id: str = None, room_id: str = None) -> None:
    delete_route = route(resource, user_id, room_id)
    print(30 * "-")
    print(f"/// DELETE test on {resource.__name__} with user_id = {user_id} and room_id = {room_id} ///")

    if delete_route is None:
        raise IOError(f"Some parameters are missing to perform the required DELETE test")
    print(f"route = {delete_route}")
    response = delete(delete_route)
    print(f"{response.json()}, status code = {response.status_code}")
    print(30 * "-")


def class_test(resource, user_ids: list = None, room_ids: list = None, datas: list = None) -> None:
    if resource == Users:
        if user_ids is None:
            print(f"Cannot perform POST test because no user ids has been provided")
        else:
            for user in user_ids:
                post_test(resource, user_id=user)
            for user in user_ids:
                post_test(resource, user_id=user)
        for user in user_ids:
            get_test(resource, user_id=user)
        get_test(Users)
        get_test(Users, user_id="whoswho")

        for user in user_ids:
            delete_test(resource, user_id=user)
            get_test(resource, user_id=user)
        delete_test(Users, user_id="whoswho")
        get_test(Users)

        if user_ids is not None:
            for user in user_ids:
                post_test(resource, user_id=user)

    if resource == ChatRooms:
        for room in room_ids:  # POST test
            post_test(resource, room_id=room)
        for room in room_ids:  # POST test on existing rooms
            post_test(resource, room_id=room)
        for room in room_ids:  # GET test on populated rooms
            get_test(resource, room_id=room)
        get_test(resource)
        get_test(resource, room_id="whichswhich")

    if resource == RoomUsers:
        # Populate rooms and user_ids
        for room in room_ids:
            post_test(ChatRooms, room_id=room)
        for user in user_ids:
            post_test(Users, user_id=user)
        for i in range(len(user_ids)):
            room = choice(room_ids)
            user = choice(user_ids)
            post_test(resource, room_id=room, data={'user': user})
        for room in room_ids:
            get_test(resource, room_id=room)
        get_test(ChatRooms)
        get_test(Users)

    if resource == Messages:
        pass


class_test(RoomUsers, user_ids=['uyqn', 'torresso', 'panders', 'vader', 'varys'], room_ids=['chicken', 'boar', 'pandora', 'group42'])