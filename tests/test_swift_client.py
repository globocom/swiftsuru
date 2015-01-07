import unittest

from mock import patch, call
from collections import namedtuple

from bogus.server import Bogus

from swiftsuru.swift_client import SwiftClient
from swiftsuru.conf import AUTH_URL, USER, KEY


class SwiftClientTest(unittest.TestCase):

    def setUp(self):
        self.url = "swifturl.com/AUTH_user"
        self.token = "AUTH_tk65ade122e45449f2aefdffcf72a30bd7"
        Bogus.called_paths = []

    @patch("swiftsuru.swift_client.swiftclient")
    def test_init_should_obtain_token(self, swiftclient):
        swiftclient.client.Connection.return_value.get_auth.return_value = (self.url, self.token)
        cli = SwiftClient()
        calls = [call(authurl='http://127.0.0.1:8080/auth/v1', user='test:tester', key='testing')]
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

    @patch("swiftclient.client.Connection.get_auth")
    def test_create_account(self, get_auth_mock):
        b = Bogus()
        url = b.serve()
        get_auth_mock.return_value = ("{}/v1/AUTH_user".format(url), "AUTH_t0k3n")
        with patch("swiftsuru.swift_client.AUTH_URL", new_callable=lambda: url):
            cli = SwiftClient()
            cli.create_account({"X-Account-Meta-Book": "MobyDick", "X-Account-Meta-Subject": "Literature"})
            self.assertIn("/v1/AUTH_user", Bogus.called_paths)

    @patch("swiftclient.client.Connection.get_auth")
    def test_remove_account(self, get_auth_mock):
        b = Bogus()
        url = b.serve()
        get_auth_mock.return_value = ("{}/v1/AUTH_user".format(url), "AUTH_t0k3n")
        with patch("swiftsuru.swift_client.AUTH_URL", new_callable=lambda: url):
            cli = SwiftClient()
            cli.remove_account("MobyDick")
            self.assertIn("/v1/AUTH_user", Bogus.called_paths)

    @patch("swiftclient.client.Connection.get_auth")
    def test_account_containers(self, get_auth_mock):
        b = Bogus()
        handler = ("/v1/AUTH_user?format=json", lambda: ('[{"count": 0, "bytes": 0, "name": "mycontainer"}]', 200))
        b.register(handler, method="GET")
        url = b.serve()
        get_auth_mock.return_value = ("{}/v1/AUTH_user?format=json".format(url), "AUTH_t0k3n")

        with patch("swiftsuru.swift_client.AUTH_URL", new_callable=lambda: url):
            cli = SwiftClient()
            containers = cli.account_containers()

        expected = [{"count": 0, "bytes": 0, "name": "mycontainer"}]
        self.assertListEqual(expected, containers)

    @patch("swiftclient.client.Connection.get_auth")
    def test_create_container(self, get_auth_mock):
        b = Bogus()
        url = b.serve()
        get_auth_mock.return_value = ("{}/v1/AUTH_user".format(url), "AUTH_t0k3n")
        with patch("swiftsuru.swift_client.AUTH_URL", new_callable=lambda: url):
            cli = SwiftClient()
            cli.create_container("my_container", {"X-Container-Meta-something": "some metadata"})
            self.assertIn("/v1/AUTH_user/my_container", b.called_paths)

    @patch("swiftclient.client.Connection.get_auth")
    def test_remove_container(self, get_auth_mock):
        b = Bogus()
        url = b.serve()
        get_auth_mock.return_value = ("{}/v1/AUTH_user".format(url), "AUTH_t0k3n")
        with patch("swiftsuru.swift_client.AUTH_URL", new_callable=lambda: url):
            cli = SwiftClient()
            cli.remove_container("my_container", {"X-Container-Meta-something": "some metadata"})
            self.assertIn("/v1/AUTH_user/my_container", b.called_paths)

    @patch("swiftclient.client.Connection.get_auth")
    def test_set_cors_http_request(self, get_auth_mock):
        b = Bogus()
        url = b.serve()
        get_auth_mock.return_value = ("{}/v1/AUTH_user".format(url), "AUTH_t0k3n")
        with patch("swiftsuru.swift_client.AUTH_URL", new_callable=lambda: url):
            cli = SwiftClient()
            cli.set_cors("my_container", "http://localhost")
            self.assertIn("/v1/AUTH_user/my_container", b.called_paths)

    @patch("swiftclient.client.Connection.get_auth")
    @patch("swiftclient.client.Connection.head_container")
    @patch("swiftclient.client.Connection.post_container")
    def test_set_cors_should_set_url(self, post_container_mock, head_container_mock, get_auth_mock):
        get_auth_mock.return_value = ("http://somehost/v1/AUTH_user", "AUTH_t0k3n")
        head_container_mock.return_value = {}

        cli = SwiftClient()
        cli.set_cors('mycontainer', 'http://myhost')

        expected_header = {'X-Container-Meta-Access-Control-Allow-Origin': 'http://myhost'}
        post_container_mock.assert_called_once_with('mycontainer', expected_header)

    @patch("swiftclient.client.Connection.get_auth")
    @patch("swiftclient.client.Connection.head_container")
    @patch("swiftclient.client.Connection.post_container")
    def test_set_cors_appending_url_to_a_pre_existent_cors_header(self, post_container_mock, head_container_mock, get_auth_mock):
        get_auth_mock.return_value = ("http://somehost/v1/AUTH_user", "AUTH_t0k3n")
        head_container_mock.return_value = {
            'x-container-meta-access-control-allow-origin': 'http://somehost'
        }

        cli = SwiftClient()
        cli.set_cors('mycontainer', 'http://myhost')

        expected_header = {'X-Container-Meta-Access-Control-Allow-Origin': 'http://somehost http://myhost'}
        post_container_mock.assert_called_once_with('mycontainer', expected_header)

    @patch("swiftclient.client.Connection.get_auth")
    @patch("swiftclient.client.Connection.head_container")
    def test_get_cors_of_a_container(self, head_container_mock, get_auth_mock):
        get_auth_mock.return_value = ("http://somehost/v1/AUTH_user", "AUTH_t0k3n")
        head_container_mock.return_value = {
            'x-container-meta-access-control-allow-origin': 'http://somehost'
        }

        cli = SwiftClient()
        computed_cors = cli.get_cors('mycontainer')

        self.assertEqual('http://somehost', computed_cors)

    @patch("swiftclient.client.Connection.get_auth")
    @patch("swiftclient.client.Connection.head_container")
    @patch("swiftclient.client.Connection.post_container")
    def test_unset_cors_of_a_container(self, post_container_mock, head_container_mock, get_auth_mock):
        get_auth_mock.return_value = ("http://somehost/v1/AUTH_user", "AUTH_t0k3n")
        head_container_mock.return_value = {
            'x-container-meta-access-control-allow-origin': 'http://somehost'
        }

        cli = SwiftClient()
        cli.unset_cors('mycontainer', 'http://somehost')

        expected_header = {'X-Container-Meta-Access-Control-Allow-Origin': ''}
        post_container_mock.assert_called_once_with('mycontainer', expected_header)

    @patch("swiftclient.client.Connection.get_auth")
    @patch("swiftclient.client.Connection.head_container")
    @patch("swiftclient.client.Connection.post_container")
    def test_unset_cors_of_a_container_with_more_than_one_host_on_cors_headers(self, post_container_mock, head_container_mock, get_auth_mock):
        get_auth_mock.return_value = ("http://somehost/v1/AUTH_user", "AUTH_t0k3n")
        head_container_mock.return_value = {
            'x-container-meta-access-control-allow-origin': 'http://somehost https://otherhost http://thirdhost'
        }

        cli = SwiftClient()
        cli.unset_cors('mycontainer', 'http://somehost')

        expected_header = {'X-Container-Meta-Access-Control-Allow-Origin': 'https://otherhost http://thirdhost'}
        post_container_mock.assert_called_once_with('mycontainer', expected_header)
