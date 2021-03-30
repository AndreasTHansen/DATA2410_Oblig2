from socket import socket
from connections import User, Room, Message
from threading import Thread
from time import sleep

user, code = User.add('uyqn')
if code != 201:
    user, code = User.get('uyqn')

client = socket()
client.connect(('127.0.0.1', 6969))
client.send(user['username'].encode('utf8'))

User.add('botman')
Room.add('chicken', 'uyqn')
Room.add('wings', 'uyqn')
Room.add('thighs', 'uyqn')

Room.join('chicken', 'botman')
Room.join('wings', 'botman')
Room.join('thighs', 'botman')


def listen_for_push():
    while True:
        message = client.recv(1024).decode('utf8')
        print(message)


Thread(target=listen_for_push).start()

sleep(2)

for i in range(10):
    Message.send('chicken', 'botman', 'Hello')
    Message.send('thighs', 'botman', 'Hello')
    Message.send('wings', 'botman', 'Hello')
