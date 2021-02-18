"""
This module unit tests the Infinite State Machine.

The module contains the following functions:
    * test_properties_file_set - Test the setting of the ISM's
    property that holds the path to the properties file.
    * test_properties_are_read_in - Test that the values in the
    properties file are read in correctly.

"""

# Standard library imports
import os
import re
import unittest

# Local application imports
from time import sleep
from ism.ISM import ISM


class TestISM(unittest.TestCase):

    path_sep = os.path.sep
    dir = os.path.dirname(os.path.abspath(__file__))
    sqlite3_properties = f'{dir}{path_sep}resources{path_sep}sqlite3_properties.yaml'
    mysql_properties = f'{dir}{path_sep}resources{path_sep}mysql_properties.yaml'

    def test_properties_file_set(self):
        """Test that ISM sets path to the tests file."""
        args = {
            'properties_file': self.sqlite3_properties
        }
        ism = ISM(args)
        self.assertEqual(ism.properties_file, self.sqlite3_properties)

    def test_properties_are_read_in(self):
        """Test that it imports properties from the tests file."""
        args = {
            'properties_file': self.sqlite3_properties
        }
        ism = ISM(args)
        self.assertEqual(
            ism.properties['database']['password'],
            None,
            f'Unexpected result for database: key read from properties file ({self.sqlite3_properties})'
        )

    def test_user_tag(self):
        """User can set the 'User Tag' to something other than 'default'."""

        args = {
            'properties_file': self.sqlite3_properties,
            'tag': 'test_tag'
        }
        ism = ISM(args)
        ism.start()
        sleep(3)
        self.assertIn('test_tag', ism.get_database_name())

    def test_sqlite3_database_creation(self):
        """Test that the sqlite3 database is created.

        Implies that rdbms key in properties is set to sqlite3 and sqlite3 installed.
        """
        args = {
            'properties_file': self.sqlite3_properties
        }
        ism = ISM(args)
        self.assertTrue(os.path.exists(ism.get_database_name()), 'Sqlite3 database creation failed')

    def test_mysql_database_creation(self):
        """Test that the MySql database is created.

        Implies that rdbms key in properties is set to mysql and mysql installed.
        """
        args = {
            'properties_file': self.mysql_properties,
            'database': {
                'password': 'wbA7C2B6R7'
            }
        }
        ism = ISM(args)
        db_name = ism.get_database_name()
        self.assertTrue(re.match(r'ism_default_.+', db_name),
                        f'Mysql DB name ({db_name}) failed to match expected pattern')

    def test_action_import_sqlite3(self):
        """Test that the ism imports the core actions and runs in the background
        as a daemon.

        """
        args = {
            'properties_file': self.sqlite3_properties
        }
        ism = ISM(args)
        self.assertEqual('STARTING', ism.get_execution_phase())
        ism.start()
        sleep(1)
        ism.stop()
        sleep(1)
        self.assertEqual('RUNNING', ism.get_execution_phase())

    def test_action_import_mysql(self):
        """Test that the ism imports the core actions and runs in the background
        as a daemon.

        """
        args = {
            'properties_file': self.mysql_properties,
            'database': {
                'password': 'wbA7C2B6R7'
            }
        }
        ism = ISM(args)
        self.assertEqual('STARTING', ism.get_execution_phase())
        ism.start()
        sleep(1)
        ism.stop()
        sleep(1)
        self.assertEqual('RUNNING', ism.get_execution_phase())

    def test_import_action_pack(self):
        args = {
            'properties_file': self.sqlite3_properties
        }
        ism = ISM(args)
        ism.import_action_pack('ism.tests.test_action_pack.action_test_startup')
        ism.start()
        sleep(3)
        ism.stop()
        sleep(1)


if __name__ == '__main__':
    unittest.main()
