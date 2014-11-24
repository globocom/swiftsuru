import re
import unittest
from mock import patch

from swiftsuru import services


class ServicesTest(unittest.TestCase):

    def test_should_generate_random_six_character_string(self):

        computed = services.generate_container_name()

        self.assertEqual(len(computed), 6)

    def test_should_generate_different_values_multiple_calls(self):

        computed1 = services.generate_container_name()
        computed2 = services.generate_container_name()
        computed3 = services.generate_container_name()

        self.assertNotEqual(computed1, computed2)
        self.assertNotEqual(computed1, computed3)
        self.assertNotEqual(computed2, computed3)

    def test_should_contain_only_numbers_and_lowcase_letters(self):

        computed = services.generate_container_name()

        # self.assertRegexpMatches(computed, )
        self.assertTrue(re.match('^[a-z0-9]+$', computed) is not None)
