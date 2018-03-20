"""
Provides the context for the Unit Tests
"""

from contextlib import ContextDecorator
import subprocess
import signal
import time
import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import dal.server_monitor_context

class ServersTestContext(ContextDecorator):
    """
    Context manager for the tests on the REST API
    """

    def __enter__(self):
        """
        Method execute when entering in the context
        """
        self._dynamodb_process = subprocess.Popen(['java', '-Djava.library.path=./dist//DynamoDBLocal_lib', '-jar', './dist/DynamoDBLocal.jar',  '-inMemory'], stdout=subprocess.PIPE)
        time.sleep(3)
        return self
    
    def __exit__(self, *exc):
        """
        Method execuuted when exiting the context
        """
        self._dynamodb_process.terminate()
        return False