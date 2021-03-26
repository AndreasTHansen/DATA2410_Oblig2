from manual_api_tests import user_api_test as user
from manual_api_tests import chat_room_api_test as chat_room

tests = {
    'user': user.run_test,
    'chat_room': chat_room.run_test
}

while True:
    print(f"\nAvailable classes to test:\n\t{list(tests.keys())}\nType \"exit\" to exit testing")
    test = input("Pick a class you want to test: ").strip().lower()
    if test == 'exit':
        break
    try:
        tests[test]()
    except KeyError:
        print(f"Class {test} is not available for testing or has not been implemented yet")

