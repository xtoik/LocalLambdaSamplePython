"""
Module containing the Unit Tests for the REST API
"""

import unittest
import sys
import os
import json
import requests
import time
import subprocess
import signal
import io
import fcntl
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from servers import handler
from tests_context import ServersTestContext

class TestServersApi(unittest.TestCase):
    """
    Class implementing the unit tests on the REST API implementation
    """

    _dynamodb_process = None
    """
    Holds a reference to the process executing the DynamoDB instance
    """

    _sam_local_process = None
    """
    Holds a reference to the process executing the SAM Local instance
    """

    @classmethod
    def setUpClass(cls):
        """
        Prepares the environment before the execution of the tests defined in the class
        """
        cls._dynamodb_process = subprocess.Popen(['java', '-Djava.library.path=./dist//DynamoDBLocal_lib', '-jar', './dist/DynamoDBLocal.jar',  '-inMemory'])
        cls._sam_local_process = subprocess.Popen(['sam local start-api'], shell=True, preexec_fn=os.setsid)
    
        # Wait for initialization
        time.sleep(7)

    @classmethod
    def tearDownClass(cls):
        """
        Terminates the environment after the execution of the tests defined in the class
        """
        os.killpg(os.getpgid(cls._sam_local_process.pid), signal.SIGTERM)   
        cls._dynamodb_process.terminate()
        time.sleep(3)

    def test_list_servers(self):
        """
        Tests that the list_servers method returns the expected result
        """
        response = requests.get('http://localhost:3000/servers')
        self.assertEqual(200, response.status_code)
        servers = response.json()
        self.assertLessEqual(2, len(servers))
        self.assertTrue('server_id' in servers[0])
        self.assertTrue(servers[0]['server_id'].startswith('Villaconejos'))
        self.assertTrue('server_id' in servers[1])
        self.assertTrue(servers[1]['server_id'].startswith('Villaconejos'))

    def test_get_existing_server(self):
        """
        Tests that the get_server method returns the expected result for an existing server
        """
        server_name = "VillaconejosBOSServer01"
        response = requests.get('http://localhost:3000/server/' + server_name)
        self.assertEqual(200, response.status_code)
        server = response.json()
        self.assertEqual(server_name, server['server_id'])
        self.assertEqual(1073741824, server['memory'])
        self.assertEqual('true', server['iisPresent'])
    
    def test_get_not_existing_server(self):
        """
        Tests that the get_server method returns the expected result for a not existing server
        """
        response = requests.get('http://localhost:3000/server/notExistingServer')
        self.assertEqual(404, response.status_code)

    def test_delete_existing_server(self):
        """
        Tests that the delete_server method works as expected for an existing server
        """
        server_name = "VillaconejosSQLServer02"
        response = requests.delete('http://localhost:3000/server/' + server_name)
        self.assertEqual(200, response.status_code)
        time.sleep(2)
        response = requests.get('http://localhost:3000/server/' + server_name)
        self.assertEqual(404, response.status_code)

    def test_delete_not_existing_server(self):
        """
        Tests that the delete_server method works as expected for a not existing server
        """
        response = requests.delete('http://localhost:3000/server/notExistingServer')
        self.assertEqual(404, response.status_code)

    def test_add_not_existing_server(self):
        """
        Tests that the add_server method works as expected for a not existing server
        """
        #with ServersTestContext():
        payload = {
            "server_id": "VillaconejosBOSServer02", 
            "iisPresent": "false", 
            "memory": 1073741824, 
            "upToDate": "false"
        }
        response = requests.post('http://localhost:3000/server', json=payload)            
        self.assertEqual(201, response.status_code)

        # test that the new server has been integrated correctly in the database
        time.sleep(2)
        response = requests.get('http://localhost:3000/server/VillaconejosBOSServer02')
        self.assertEqual(200, response.status_code)
        server = response.json()
        self.assertEqual('VillaconejosBOSServer02', server['server_id'])
        self.assertEqual(1073741824, server['memory'])
        self.assertEqual('false', server['upToDate'])

    def test_add_existing_server(self):
        """
        Tests that the add_server method works as expected for an existing server
        """
        #with ServersTestContext():
        payload = {
            "server_id": "VillaconejosBOSServer01", 
            "iisPresent": "false", 
            "memory": 1073741824, 
            "upToDate": "false"
        }
        response = requests.post('http://localhost:3000/server', json=payload)

        self.assertEqual(409, response.status_code)

    def test_update_existing_server(self):
        """
        Tests that the update_server method works as expected for an existing server
        """
        #with ServersTestContext():
        server_name = "VillaconejosSQLServer01"
        payload = {
            "server_id": server_name, 
            "iisPresent": "true", 
            "memory": 1073741824, 
            "upToDate": "true"
        }
        response = requests.put('http://localhost:3000/server', json=payload)            
        self.assertEqual(200, response.status_code)

        # test that the server updated has been integrated in the database
        time.sleep(2)
        response = requests.get('http://localhost:3000/server/' + server_name)
        self.assertEqual(200, response.status_code)
        server = response.json()
        self.assertEqual(payload['server_id'], server['server_id'])
        self.assertEqual(payload['memory'], server['memory'])
        self.assertEqual(payload['upToDate'], server['upToDate'])

    def test_update_not_existing_server(self):
        """
        Tests that the update_server method works as expected for a not existing server
        """
        #with ServersTestContext():
        server_name = "test_update_not_existing_server"
        payload = {
            "server_id": server_name, 
            "iisPresent": "false", 
            "memory": 1073741824, 
            "upToDate": "false"
        }
        response = requests.put('http://localhost:3000/server', json=payload)            
        self.assertEqual(404, response.status_code)

        # test that the server updated has not been integrated in the database
        time.sleep(2)
        response = requests.get('http://localhost:3000/server/' + server_name)
        self.assertEqual(404, response.status_code)

if __name__ == '__main__':
    unittest.main()
