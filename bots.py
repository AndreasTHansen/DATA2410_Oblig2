
import random
# Morsomme bots


def JoeBot():
    responses = ["Hello, I am Joe", "How you doooing?", "Welcome guys, I am JoeBot"]

    return random.choice(responses)

def Peter():
    responses = ["Wow, its dead in here, lets turn it uuup!", "Welcome, Welcome! Anyone want to do anything fun?",
                 "Hello! I don't really have much sparetime bit here I am!"]

    return random.choice(responses)

def Anna(room_id):
    #Logge inn

    sign_in()
    join_room()

    #Velge rom

    #Skrive meldinger