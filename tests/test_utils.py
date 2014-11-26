import re
import unittest
from mock import patch

from swiftsuru import utils


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
