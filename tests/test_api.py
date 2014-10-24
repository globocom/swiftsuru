import unittest
from bogus.server import Bogus
from mock import patch
from swiftsuru import app


class APITest(unittest.TestCase):

    def setUp(self):
        self.client = app.test_client()

    def test_add_instance_returns_201(self):
        response = self.client.post("/resources")
        self.assertEqual(response.status_code, 201)

    def test_remove_instance_returns_200(self):
        response = self.client.delete("/resources")
        self.assertEqual(response.status_code, 200)

    @patch("swiftclient.client.Connection.get_auth")
    def test_bind_returns_201(self, get_auth_mock):
        b = Bogus()
        url = b.serve() # for python-swiftclient
        get_auth_mock.return_value = ("{}/v1/AUTH_user".format(url), "AUTH_t0k3n")

        data = "app-host=awesomeapp.tsuru.io&unit-host=10.10.10.10"
        response = self.client.post("/resources/my-swift/bind", data=data, content_type="application/x-www-form-urlencoded")
        self.assertEqual(response.status_code, 201)

    @patch("swiftclient.client.Connection.get_auth")
    def test_bind_creates_swift_account_with_first_name_on_host(self, get_auth_mock):
        b = Bogus()
        url = b.serve() # for python-swiftclient
        get_auth_mock.return_value = ("{}/v1/AUTH_user".format(url), "AUTH_t0k3n")

        data = "app-host=awesomeapp.tsuru.io&unit-host=10.10.10.10"
        self.client.post("/resources/my-swift/bind", data=data, content_type="application/x-www-form-urlencoded")
        self.assertIn("/v1/AUTH_user", b.called_paths)

    def test_unbind_returns_200(self):
        response = self.client.delete("/resources/my-swift/bind")
        self.assertEqual(response.status_code, 200)
