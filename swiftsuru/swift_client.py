import swiftclient
from swiftsuru.conf import AUTH_URL, USER, KEY


class SwiftClient(object):
    """
    python-swiftclient abstraction.
    This class authenticates the user and stores an authenticated connection
    with Swift's server.
    It also abstracts swiftclient actions, so you don't have to store the connection
    yourself or perform the actions on top of it, for example, what could be:
        cli = SwiftClient() # do some dirty work for you
        cli.conn.post_account(<...>)
    This is kind of ugly, to make it cleaner we abstract the connection for you, e.g:
        cli = SwiftClient()
        cli.create_account(<...>) # much better!
    """

    def __init__(self):
        """
        Authenticates on swift with AUTH_URL, USER, and KEY from conf.py.
        Gets auth information for next API calls via conn.get_auth() and
        a authenticated client connection for performing actions.
        """
        conn = swiftclient.client.Connection(authurl=AUTH_URL, user=USER, key=KEY)
        auth_url, auth_token = conn.get_auth()
        self.conn = swiftclient.client.Connection(preauthurl=auth_url, preauthtoken=auth_token)

    def create_account(self, headers):
        self.conn.post_account(headers)
