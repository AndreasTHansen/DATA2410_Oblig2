from client import *
import random
# Morsomme bots


def Joe(msg):
    responses = ["Hey how you doing?", "Hello guys!"]

    return random.choice(responses)


def Anna(room_id):
    #Logge inn

    sign_in()
    join_room()

    #Velge rom

    #Skrive meldinger