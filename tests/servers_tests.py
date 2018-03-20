"""
Module containing the Unit Tests for the REST API
"""

import unittest
import sys
import os
import json
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from servers import handler
from tests_context import ServersTestContext

class TestServersApi(unittest.TestCase):
    """
    Class implementing the unit tests on the REST API implementation
    """

    def test_list_servers(self):
        """
        Tests that the list_servers method returns the expected result
        """
        with ServersTestContext():
            response = handler({
                'httpMethod': 'GET',
                'pathParameters': None
            }, None)
            print(response)
            self.assertEqual(200, response['statusCode'])
            servers = json.loads(response['body'])
            self.assertEqual(2, len(servers))
            self.assertTrue('server_id' in servers[0])
            self.assertTrue(servers[0]['server_id'].startswith('Villaconejos'))
            self.assertTrue('server_id' in servers[1])
            self.assertTrue(servers[1]['server_id'].startswith('Villaconejos'))

if __name__ == '__main__':
    unittest.main()
