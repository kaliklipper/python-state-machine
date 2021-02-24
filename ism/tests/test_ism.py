"""
This module unit tests the Infinite State Machine.

The module contains the following functions:
    * test_properties_file_set - Test the setting of the ISM's
    property that holds the path to the properties file.
    * test_properties_are_read_in - Test that the values in the
    properties file are read in correctly.

    Assumes the test machine has sqlite3 and MySql installed.
    MySql requires the user 'state_admin' to exist and password of
    wbA7C2B6R7.

"""

# Standard library imports
import json
import os
import re
import unittest

# Local application imports
from time import sleep

import yaml

from ism.ISM import ISM


class TestISM(unittest.TestCase):

    path_sep = os.path.sep
    dir = os.path.dirname(os.path.abspath(__file__))
    sqlite3_properties = f'{dir}{path_sep}resources{path_sep}sqlite3_properties.yaml'
    mysql_properties = f'{dir}{path_sep}resources{path_sep}mysql_properties.yaml'

    @staticmethod
    def get_properties(properties_file) -> dict:
        """Read in the properties file"""
        with open(properties_file, 'r') as file:
            return yaml.safe_load(file)

    @staticmethod
    def SendTestSupportMsg(msg, sender_id, inbound):

        if not os.path.exists(inbound):
            os.makedirs(inbound)

        with open(f'{inbound}{os.path.sep}{sender_id}.json', 'w') as message:
            message.write(json.dumps(msg))
        with open(f'{inbound}{os.path.sep}{sender_id}.smp', 'w') as semaphore:
            semaphore.write('')

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
        """Test that the ism imports the core actions."""

        inbound = self.get_properties(self.mysql_properties)['test']['support']['inbound']

        args = {
            'properties_file': self.mysql_properties,
            'database': {
                'password': 'wbA7C2B6R7'
            }
        }
        ism = ISM(args)
        ism.import_action_pack('ism.tests.support')

        message = {
            "action": "ActionRunSqlQuery",
            "payload": {
                "sql": "SELECT * from actions;",
                "sender_id": 1
            }
        }
        self.SendTestSupportMsg(message, message['payload']['sender_id'], inbound)
        ism.start(join=True)
        # TODO Wait for reply and assert against actions records
        ism.stop()

    def test_import_action_pack(self):
        """Import the test action pack and assert it creates the file '/tmp/test_import_action_pack.txt'

        The action should write a string to the file then deactivate, leaving the file with a line count of 1.
        """

        test_file = '/tmp/test_import_action_pack.txt'
        if os.path.exists(test_file):
            os.remove(test_file)

        args = {
            'properties_file': self.sqlite3_properties
        }
        ism = ISM(args)
        ism.import_action_pack('ism.tests.test_action_pack')
        ism.start()
        sleep(1)
        ism.stop()
        sleep(1)
        self.assertTrue(os.path.exists(test_file))
        with open(test_file, 'r') as file:
            self.assertTrue(len(file.readlines()) == 1, f'Unexpected line count for {test_file}, 1 expected.')


if __name__ == '__main__':
    unittest.main()
