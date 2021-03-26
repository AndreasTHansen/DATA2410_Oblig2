import requests

route = "http://127.0.0.1:5000//api/rooms/"


def get_all_test():
    print(requests.get(route).json())


def get_test():
    room_id = input("Which room id do you want to get? ")
    print(f"Getting {room_id}: ")
    print(requests.get(route + room_id).json())


def post_test():
    room_id = input("Enter user id for posting: ")
    name = input(f"Enter name:str of room id {room_id}: ")
    while True:
        try:
            size = int(input(f"Enter size:int of {room_id}: "))
            break
        except ValueError:
            print("Room size must be an integer")
    print(requests.post(route + room_id, {'Name': name, 'Size': size}).json())


def delete_test():
    room_id = input("Which user id do you want to get? ")
    print(f"Deleting {room_id}: ")
    print(requests.delete(route + room_id).json())


tests = {
    'get_all': get_all_test,
    'get': get_test,
    'post': post_test,
    'delete': delete_test
}


def run_test():
    while True:
        print(f"\navailable tests:\n\t{list(tests.keys())}\nType \"exit\" to exit class test")
        test = input("Choose a test you want to run: ").strip().lower()
        if test == 'exit':
            break
        try:
            tests[test]()
        except KeyError:
            print(f"Request {test} is not available for testing or has not been implemented yet")
