from sys import platform
from os import system
from time import sleep
import json
from re import sub
from random import choice


def clear_console():
    if platform.__contains__('win'):
        system('cls')
    else:
        system('clear')


def test(n: int):
    if n > 2:
        return
    else:
        return n


message = "/join"
message = sub('[^A-Za-z ]+', '', message).lower()
word_list = message.split()

print(word_list.pop(0))
print(word_list)