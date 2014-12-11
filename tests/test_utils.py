import re
import unittest
from collections import namedtuple
from mock import patch

from swiftsuru import utils
from swiftsuru import conf


class UtilsTest(unittest.TestCase):

    def test_should_generate_random_six_character_string(self):

        computed = utils.generate_container_name()

        self.assertEqual(len(computed), 6)

    def test_should_generate_different_values_multiple_calls(self):

        computed1 = utils.generate_container_name()
        computed2 = utils.generate_container_name()
        computed3 = utils.generate_container_name()

        self.assertNotEqual(computed1, computed2)
        self.assertNotEqual(computed1, computed3)
        self.assertNotEqual(computed2, computed3)

    def test_should_contain_only_numbers_and_lowcase_letters(self):

        computed = utils.generate_container_name()

        self.assertTrue(re.match('^[a-z0-9]+$', computed) is not None)

    def test_should_create_password_with_8_characters(self):
        computed = utils.generate_password()

        self.assertEqual(len(computed), 8)

    def test_password_should_contain_numbers_letters_basic_symbols(self):
        """
        Test if password contains numbers, letters or !@#$%^&*
        """
        computed = utils.generate_password()

        self.assertTrue(re.match('^[a-zA-Z0-9!@#$%^&*]+$', computed) is not None)

    @patch("swiftsuru.utils.Client")
    @patch("swiftsuru.utils.L4Opts")
    def test_permit_keystone_access_should_call_aclapiclient_with_keystone_ip_endpoint(self, l4_opts_mock, aclapi_mock):
        utils.aclcli = None
        func_mock = aclapi_mock.return_value.add_tcp_permit_access
        l4_opts_obj = namedtuple("L4Opts", ["to_dict"])(lambda: {})
        l4_opts_mock.return_value = l4_opts_obj
        utils.permit_keystone_access(unit_host="10.10.1.2")
        func_mock.assert_called_once_with(
            desc="keystone access (swift service) for tsuru unit: {}".format("10.10.1.2"),
            source="10.10.1.2/24",
            dest="127.0.0.1/32",
            l4_opts=l4_opts_obj
        )

    @patch("swiftsuru.utils.Client")
    @patch("swiftsuru.utils.L4Opts")
    def test_permit_keystone_access_liberates_correct_port(self, l4_opts_mock, aclapi_mock):
        utils.aclcli = None
        l4_opts_mock.return_value.to_dict.return_value = {}
        utils.permit_keystone_access(unit_host="10.10.1.2")
        l4_opts_mock.assert_called_once_with("eq", conf.KEYSTONE_PORT, "dest")

    @patch("swiftsuru.utils.Client")
    @patch("swiftsuru.utils.L4Opts")
    def test_permit_swift_access_should_call_aclapiclient_with_swift_api_ip_endpoint(self, l4_opts_mock, aclapi_mock):
        utils.aclcli = None
        func_mock = aclapi_mock.return_value.add_tcp_permit_access
        l4_opts_obj = namedtuple("L4Opts", ["to_dict"])(lambda: {})
        l4_opts_mock.return_value = l4_opts_obj
        # swift_host could as well be the DNS name
        utils.permit_swift_access(unit_host="10.10.2.3", swift_host="10.2.3.4", swift_port="35357")
        func_mock.assert_called_once_with(
            desc="swift api access (swift service) for tsuru unit: {}".format("10.10.2.3"),
            source="10.10.2.3/24",
            dest="10.2.3.4/32",
            l4_opts=l4_opts_obj
        )

    @patch("swiftsuru.utils.Client")
    @patch("swiftsuru.utils.L4Opts")
    def test_permit_swift_access_liberates_correct_port(self, l4_opts_mock, aclapi_mock):
        utils.aclcli = None
        l4_opts_mock.return_value.to_dict.return_value = {}
        utils.permit_swift_access(unit_host="10.10.2.3", swift_host="10.2.3.4", swift_port="35357")
        l4_opts_mock.assert_called_once_with("eq", "35357", "dest")
