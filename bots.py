import random


# Morsomme bots


def JoeBot():
    responses = ["Hello, I am Joe", "How you doooing?", "Welcome guys, I am JoeBot"]

    return random.choice(responses)


def PeterBot():
    responses = ["Wow, its dead in here, lets turn it uuup!", "Welcome, Welcome! Anyone want to do anything fun?",
                 "Hello! I don't really have much sparetime bit here I am!"]

    return random.choice(responses)


def AnnaBot():
    responses = ["You woke me up! Whats your reasoning", "yaaaawn", "Welcome I guess"]

    return random.choice(responses)
