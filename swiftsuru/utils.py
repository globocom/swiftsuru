"""
Swiftsuru related services to Tsuru
"""
import pymongo
import os
import random

from swiftsuru import conf


def generate_container_name():
    return os.urandom(3).encode('hex')


def generate_password(pw_length=8):
    """ Generate a password
        From: http://interactivepython.org/runestone/static/everyday/2013/01/3_password.html
    """
    alphabet = "abcdefghijklmnopqrstuvwxyz0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ!@#$%^&*"
    mypw = ""

    for i in range(pw_length):
        next_index = random.randrange(len(alphabet))
        mypw = mypw + alphabet[next_index]

    return mypw
