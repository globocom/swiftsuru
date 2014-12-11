"""
Swiftsuru related services to Tsuru
"""
import os
import random
import socket
from aclapiclient import Client, L4Opts


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


aclcli = None


def aclapi_cli():
    global aclcli
    if aclcli is None:
        aclcli = Client(conf.ACLAPI_USER, conf.ACLAPI_PASS, conf.ACLAPI_URL)
    return aclcli


def permit_keystone_access(unit_host):
    l4_opts = L4Opts("eq", conf.KEYSTONE_PORT, "dest")
    aclapi_cli().add_tcp_permit_access(
        desc="access for service for tsuru unit: {}".format(unit_host),
        source="{}/24".format(unit_host),
        dest="{}/32".format(socket.gethostbyname(conf.KEYSTONE_HOST)),
        l4_opts=l4_opts
    )
