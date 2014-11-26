
import ming
import unittest

from mock import patch, Mock
from swiftsuru.dbclient import SwiftsuruDBClient


class SwiftsuruDBClientTest(unittest.TestCase):

    def setUp(self):
        fake_mongo = ming.create_datastore('mim://')

        patch("swiftsuru.dbclient.SwiftsuruDBClient.set_connection",
              Mock(return_value=fake_mongo.conn)).start()

        self.db = SwiftsuruDBClient()

    def tearDown(self):
        patch.stopall()

    def test_list_plans_returns_a_list(self):
        assert isinstance(self.db.list_plans(), list)

    def test_add_and_get_a_plan(self):
        self.db.add_plan("PlanName", "plan_tenant", "Plan Description")

        plan = self.db.get_plan("PlanName")
        self.assertEqual(plan.get("description"), "Plan Description")

    def test_remove_plan(self):
        self.db.add_plan("PlanName", "plan_tenant", "Plan Description")
        self.assertGreater(len(self.db.list_plans()), 0)

        self.db.remove_plan("PlanName")
        self.assertEqual(len(self.db.list_plans()), 0)

    def test_list_instances_returns_a_list(self):
        assert isinstance(self.db.list_instances(), list)

    def test_add_and_get_an_instance(self):
        self.db.add_instance("myswift", "storm", "e2opim", "Infra", "storm", "stormpass")

        instance = self.db.get_instance("myswift")
        self.assertEqual(instance.get("container"), "e2opim")

    def test_get_instances_by_plan(self):
        self.db.add_instance("myswift", "storm", "e2opim", "Infra", "storm", "stormpass")

        instances = self.db.get_instances_by_plan("Infra")
        self.assertGreater(len(instances), 0)

        instance = instances[0]
        self.assertEqual(instance.get("container"), "e2opim")

    def test_remove_instance(self):
        self.db.add_instance("myswift", "storm", "e2opim", "Infra", "storm", "stormpass")
        self.db.remove_instance("myswift")

        instance = self.db.get_instance("myswift")
        self.assertEqual(instance.get("deleted"), True)
