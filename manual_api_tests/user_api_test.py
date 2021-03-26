import requests

route = 'http://127.0.0.1:5000/api/user/'


def get_all_test():
    print(requests.get(route).json())


def get_test():
    user_id = input("Which user id do you want to get? ")
    print(f"Getting {user_id}: ")
    print(requests.get(route + user_id).json())


def post_test():
    user_id = input("Enter user id for posting: ")
    name = input(f"Enter name:str of user id {user_id}: ")
    while True:
        try:
            age = int(input(f"Enter age:int of {user_id}: "))
            break
        except ValueError:
            print("Age must be an integer")
    email = input(f"Enter email:str of user id {user_id}: ")
    print(requests.post(route + user_id, {'name': name, 'age': age, 'email': email}).json())


def delete_test():
    user_id = input("Which user id do you want to get? ")
    print(f"Deleting {user_id}: ")
    print(requests.delete(route + user_id).json())


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
