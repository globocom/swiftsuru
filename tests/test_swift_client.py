import unittest
from mock import patch, call
from swiftsuru.swift_client import SwiftClient
from swiftsuru.conf import AUTH_URL, USER, KEY


class SwiftClientTest(unittest.TestCase):

    def setUp(self):
        self.url = "swifturl.com/AUTH_user"
        self.token = "AUTH_tk65ade122e45449f2aefdffcf72a30bd7"

    @patch("swiftsuru.swift_client.swiftclient")
    def test_init_should_obtain_token(self, swiftclient):
        swiftclient.client.Connection.return_value.get_auth.return_value = (self.url, self.token)
        cli = SwiftClient()
        calls = [call(authurl='http://127.0.0.1:8080/auth/v1.0', user='test:tester', key='testing')]
        swiftclient.client.Connection.assert_has_calls(calls)

    @patch("swiftsuru.swift_client.swiftclient")
    def test_init_should_call_get_token(self, swiftclient):
        swiftclient.client.Connection.return_value.get_auth.return_value = (self.url, self.token)
        cli = SwiftClient()
        swiftclient.client.Connection.return_value.get_token.assert_called_once()

    @patch("swiftsuru.swift_client.swiftclient")
    def test_init_should_get_client_with_url_and_token(self, swiftclient):
        swiftclient.client.Connection.return_value.get_auth.return_value = (self.url, self.token)
        cli = SwiftClient()
        swiftclient.client.Connection.assert_called_with(preauthurl=self.url, preauthtoken=self.token)

    def test_create_account_should_call_swiftclient_equivalent(self):
        pass
