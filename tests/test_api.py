import json
import unittest
from mock import patch
from bogus.server import Bogus

from swiftsuru import app, conf


class APITest(unittest.TestCase):

    def setUp(self):
        self.maxDiff = None
        self.client = app.test_client()
        self.content_type = "application/x-www-form-urlencoded"

    @patch("swiftsuru.api.SwiftsuruDBClient")
    @patch("swiftsuru.api.SwiftClient")
    @patch("swiftsuru.api.KeystoneClient")
    def test_add_instance(self, mock_keystoneclient, mock_swiftclient, mock_dbclient):
        mock_dbclient.return_value.get_plan.return_value = {'tenant': 'tenant_name'}
        mock_dbclient.retun_value.get_plan.retun_value = {'name': 'plan', 'tenant': 'tenant'}

        data = "name=myinstance&plan=small&team=myteam"
        response = self.client.post("/resources",
                                    data=data,
                                    content_type=self.content_type)

        self.assertEqual(response.status_code, 201)

        expected_username = 'myteam_myinstance'
        expected_role = conf.KEYSTONE_DEFAULT_ROLE

        self.assertTrue(mock_keystoneclient.return_value.create_user.called)
        _, _, kargs = mock_keystoneclient.return_value.create_user.mock_calls[0]

        self.assertEqual(kargs['name'], expected_username)
        self.assertEqual(kargs['role_name'], expected_role)
        self.assertEqual(len(kargs['password']), 8)
        self.assertEqual(kargs['enabled'], True)
        self.assertEqual(kargs['project_name'], 'tenant_name')

    def test_add_instance_should_have_a_plan(self):
        data = "name=mysql_instance&team=myteam"
        response = self.client.post("/resources",
                                    data=data,
                                    content_type=self.content_type)

        self.assertEqual(response.status_code, 500)

    @patch("swiftsuru.api.SwiftsuruDBClient")
    def test_remove_instance_returns_200(self, dbclient_mock):
        response = self.client.delete("/resources/my_instance")
        self.assertEqual(response.status_code, 200)

        _, _, kargs = dbclient_mock.return_value.remove_instance.mock_calls[0]
        expected = 'my_instance'
        computed = kargs.get('name')

        self.assertEqual(computed, expected)

    @patch("swiftsuru.api.KeystoneClient")
    @patch("swiftsuru.api.SwiftsuruDBClient")
    @patch("swiftsuru.api.utils.conf")
    def test_bind_export_swift_enviroments_and_returns_201(self, conf_mock, dbclient_mock, keystoneclient_mock):
        bog = Bogus()
        bog.register(("/api/ipv4/acl/10.4.3.2/24", lambda:("{}",200)),
                     method="PUT",
                     headers={"Location": "/api/jobs/1"})
        url = bog.serve()
        conf_mock.ACLAPI_URL = url
        dbclient_mock.return_value.get_instance.return_value = {"name": 'intance_name',
                                                                "team": 'intance_team',
                                                                "container": 'intance_container',
                                                                "plan": 'intance_plan',
                                                                "user": 'intance_user',
                                                                "password": 'instance_password'}

        dbclient_mock.return_value.get_instance.return_value = {"name": 'plan_name',
                                                                "tenant": 'plan_tenant',
                                                                "description": 'plan_desc'}

        keystoneclient_mock.return_value.get_storage_endpoints.return_value = {
            "adminURL": "http://localhost",
            "publicURL": "http://localhost",
            "internalURL": "http://localhost"
        }

        data = "app-host=myapp.cloud.tsuru.io&unit-host=10.4.3.2"
        response = self.client.post("/resources/intance_name/bind",
                                    data=data,
                                    content_type=self.content_type)

        self.assertEqual(response.status_code, 201)

        expected_keys = ["SWIFT_ADMIN_URL",
                         "SWIFT_PUBLIC_URL",
                         "SWIFT_INTERNAL_URL",
                         "SWIFT_AUTH_URL",
                         "SWIFT_CONTAINER",
                         "SWIFT_TENANT",
                         "SWIFT_USER",
                         "SWIFT_PASSWORD"]

        computed = json.loads(response.get_data())

        self.assertEquals(len(computed), len(expected_keys))

        for key in expected_keys:
            self.assertIn(key, computed.keys())

    @patch("swiftsuru.api.KeystoneClient")
    @patch("swiftsuru.api.SwiftsuruDBClient")
    @patch("swiftsuru.api.utils.conf")
    def test_bind_calls_aclapi_through_aclapiclient(self, conf_mock, dbclient_mock, keystoneclient_mock):
        bog = Bogus()
        bog.register(("/api/ipv4/acl/10.4.3.2/24", lambda:("{}",200)),
                     method="PUT",
                     headers={"Location": "/api/jobs/1"})
        url = bog.serve()
        conf_mock.ACLAPI_URL = url
        data = "app-host=myapp.cloud.tsuru.io&unit-host=10.4.3.2"
        response = self.client.post("/resources/intance_name/bind",
                                    data=data,
                                    content_type=self.content_type)

        self.assertEqual(response.status_code, 201)
        self.assertIn("/api/ipv4/acl/10.4.3.2/24", bog.called_paths)

    @patch("swiftclient.client.Connection.get_auth")
    def test_unbind_returns_200(self, get_auth_mock):
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

        expected = [{u'name': u'Infra', u'description': u'Tenant para Infra'}]
        computed = json.loads(response.get_data())
        self.assertEqual(computed, expected)
