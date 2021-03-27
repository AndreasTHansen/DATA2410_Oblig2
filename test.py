from requests import get, post, delete
from simple import User, Room, Message

URL = "http://127.0.0.1:5000/api"

print(User.add('uyqn'))
print(Room.add('chicken'))
print(Room.join('chicken', 'uyqn'))
print(Message.send('chicken', 'uyqn', f"I love chicken!"))
print(Message.get_all('chicken','uyqn'))
print(Room.add('Boar'))
print(Room.join('Boar', 'uyqn'))
print(Message.send('chicken', 'uyqn', f"Nezuko-CHAAAAAAN"))