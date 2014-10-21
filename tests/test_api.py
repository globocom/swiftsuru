import unittest
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

    def test_bind_returns_201(self):
        response = self.client.post("/resources/my-swift/bind")
        self.assertEqual(response.status_code, 201)

    def test_unbind_returns_200(self):
        response = self.client.delete("/resources/my-swift/bind")
        self.assertEqual(response.status_code, 200)
