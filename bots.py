
import random
# Morsomme bots


def JoeBot(msg=None):
    responses = ["Hello, I am Joe", "How you doooing?", "Welcome guys, I am JoeBot"]

    if not msg:
        return random.choice(responses)

    return msg


def PeterBot(msg=None):
    responses = ["Wow, its dead in here, lets turn it uuup!", "Welcome, Welcome! Anyone want to do anything fun?",
                 "Hello! I don't really have much sparetime bit here I am!"]

    if not msg:
        return random.choice(responses)

    return msg


def AnnaBot(msg=None):
    responses = ["You woke me up! Whats your reasoning", "yaaaawn", "Welcome I guess"]

    if not msg:
        return random.choice(responses)

    return msg


def RazorBot(msg=None):
    responses = ["Argh, there is way to many people here", "I am hungry, is anyone else hungry?", "Hello, hope you"
                                                                                                  "guys don't make"
                                                                                                  "to much noice"]

    if not msg:
        return random.choice(responses)

    return msg