import requests
import json
from datetime import datetime
from time import sleep

route = "http://127.0.0.1:5000/api/rooms/"

users = {
    'uyqn': {
        'Name': "Uy Quoc Nguyen",
        'Age': 29,
        'Email': "uy.nguyen92@gmail.com"
    },
    'panders': {
        'Name': "Anders Hagan Ottersland",
        'Age': 21,
        'Email': "anders@epost.no"
    },
    'torresso': {
        'Name': "Andreas Torres Hansen",
        'Age': 21,
        'Email': "andreas@google.com"
    }
}

some_dict = {
    'chicken': {
        'Name': "Chicken wings",
        'Size': 10,
        'Users': {}
    }
}

some_dict['chicken']['Users'].update(users)

users.update({'vader': {
    'Name': 'Anakin Skywalker',
    'Age': 45,
    'Email': 'darth_vader@deathstar.com'
}})

some_dict['chicken']['Users'].update({'vader': users['vader']})

messages = {str(datetime.now()): {
    'user': 'uyqn',
    'room': 'chicken',
    'timestamp': datetime.now().strftime("%c"),
    'message': "I love chickens!"
}}

sleep(0.1)

messages.update({
    str(datetime.now()): {
        'user': 'panders',
        'room': 'chicken',
        'time': datetime.now().strftime("%c"),
        'message': "I love chicken too!"
    }
})

sleep(0.1)

messages.update({
    str(datetime.now()): {
        'user': 'torresso',
        'room': 'chicken',
        'time': datetime.now().strftime("%c"),
        'message': "Let's go grab some chicken then!"
    }
})

filtered = list(messages.values())
filter2 = filter(lambda m: m['user'] == 'panders', filtered)

for x in filter2:
    print(x)

#  response = requests.post(route+'chicken', {'Name': 'Chicken wings', 'Size': 20})

#  print(response.json())
