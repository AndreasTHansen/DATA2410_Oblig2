import requests

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

print(str.__name__)

#  response = requests.post(route+'chicken', {'Name': 'Chicken wings', 'Size': 20})

#  print(response.json())
