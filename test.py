from connections import User, Room, Message
from json import dumps, loads
from requests import post, get, patch

print(User.add(user_id='uyqn'))
print(User.delete(user_id='uyqn'))
print(User.add(user_id='panders'))
print(User.get_all(requester='panders'))
print(User.toggle_push('panders'))