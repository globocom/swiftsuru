import json
import unittest
from mock import patch

from bogus.server import Bogus

from swiftsuru import app, conf
from swiftsuru.api import CONTAINER_TEMPLATE_NAME


class APITest(unittest.TestCase):

    def setUp(self):
        self.maxDiff = None
        self.client = app.test_client()
        self.content_type = "application/x-www-form-urlencoded"
        Bogus.called_paths = []

    def test_add_instance_returns_201(self):
        data = "name=mysql_instance&plan=infra&team=myteam"
        response = self.client.post("/resources",
                                    data=data,
                                    content_type=self.content_type)

        self.assertEqual(response.status_code, 201)

    # @patch("swiftsuru.api.SwiftClient")
    # def test_add_instance_calls_create_container(self, mock_swiftclient):
    #     data = "name=mysql_instance&plan=small&team=myteam"
    #     response = self.client.post("/resources",
    #                                 data=data,
    #                                 content_type=self.content_type)

    @patch("swiftsuru.api.KeystoneClient")
    def test_add_instance_calls_create_user(self, mock_keystoneclient):

        data = "name=myinstance&plan=small&team=myteam"
        response = self.client.post("/resources",
                                    data=data,
                                    content_type=self.content_type)

        expected_username = 'myteam_myinstance'
        expected_role = conf.KEYSTONE_DEFAULT_ROLE

        self.assertTrue(mock_keystoneclient.return_value.create_user.called)
        _, _, kargs = mock_keystoneclient.return_value.create_user.mock_calls[0]

        self.assertEqual(kargs['name'], expected_username)
        self.assertEqual(kargs['role'], expected_role)
        self.assertEqual(len(kargs['password']), 8)
        self.assertEqual(kargs['enabled'], True)
        self.assertEqual(kargs['project'], 'small')

    def test_add_instance_should_have_a_plan(self):
        data = "name=mysql_instance&team=myteam"
        response = self.client.post("/resources",
                                    data=data,
                                    content_type=self.content_type)

        self.assertEqual(response.status_code, 500)

    def test_remove_instance_returns_200(self):
        response = self.client.delete("/resources")
        self.assertEqual(response.status_code, 200)

    @patch("swiftclient.client.Connection.get_auth")
    def test_bind_returns_201(self, get_auth_mock):
        b = Bogus()
        url = b.serve()  # for python-swiftclient
        get_auth_mock.return_value = ("{}/v1/AUTH_user".format(url), "AUTH_t0k3n")

        data = "app-host=awesomeapp.tsuru.io&unit-host=10.10.10.10"
        response = self.client.post("/resources/my-swift/bind", data=data, content_type=self.content_type)
        self.assertEqual(response.status_code, 201)

    @patch("swiftclient.client.Connection.get_auth")
    def test_bind_creates_swift_container(self, get_auth_mock):
        b = Bogus()
        url = b.serve()  # for python-swiftclient
        get_auth_mock.return_value = ("{}/v1/AUTH_user".format(url), "AUTH_t0k3n")

        data = "app-host=awesomeapp.tsuru.io&unit-host=10.10.10.10"
        self.client.post("/resources/my-swift/bind", data=data, content_type=self.content_type)
        self.assertIn("/v1/AUTH_user/{}".format(CONTAINER_TEMPLATE_NAME), b.called_paths)

    @patch("swiftclient.client.Connection.get_auth")
    def test_unbind_returns_200(self, get_auth_mock):
        b = Bogus()
        url = b.serve()
        get_auth_mock.return_value = ("{}/v1/AUTH_user".format(url), "AUTH_t0k3n")

        data = "app-host=awesomeapp.tsuru.io&unit-host=10.10.10.10"
        response = self.client.delete("/resources/my-swift/bind", data=data, content_type=self.content_type)
        self.assertEqual(response.status_code, 200)

    def test_healthcheck(self):
        response = self.client.get("/healthcheck")
        content = response.get_data()

        self.assertEqual(response.status_code, 200)
        self.assertIn(content, 'WORKING')

    @patch("swiftsuru.dbclient.SwiftsuruDBClient.list_plans")
    def test_list_plan(self, list_plans_mock):
        list_plans_mock.return_value = [{'name': 'Infra',
                                         'description': 'Tenant para Infra'}]

        response = self.client.get("/resources/plans")
        self.assertEqual(response.status_code, 200)

        expected = {
            'G1/Jornalismo': 'Tenant para G1/Jornalismo',
            'GE/Esportes': 'Tenant para GE/Esportes',
            'GShow/Entretenimento': 'Tenant para GShow/Entretenimento',
            'Infra': 'Tenant para Infra',
            'Plataformas': 'Tenant para Plataformas',
            'Produtos Globo': 'Tenant para Produtos Globo',
            'Webmedia': 'Tenant para Webmedia',
        }

        computed = json.loads(response.get_data())

        self.assertEqual(computed, expected)
