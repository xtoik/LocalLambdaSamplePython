"""
Provides the context for the Unit Tests
"""

from contextlib import ContextDecorator
import subprocess
import signal
import time
import os
import io
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import dal.server_monitor_context

class ServersTestContext(ContextDecorator):
    """
    Context manager for the tests on the REST API
    """

    def __enter__(self):
        """
        Method executed when entering in the context
        """
        self._dynamodb_process = subprocess.Popen(['java', '-Djava.library.path=./dist//DynamoDBLocal_lib', '-jar', './dist/DynamoDBLocal.jar',  '-inMemory'], stdout=subprocess.PIPE)
        self._sam_local_process = subprocess.Popen(
            ['sam local start-api'], 
            stdout=subprocess.PIPE, 
            stderr=subprocess.PIPE, 
            shell=True,
            preexec_fn=os.setsid)
    
        ### Wait for initialization
        time.sleep(7)

        return self
    
    def __exit__(self, *exc):
        """
        Method executed when exiting the context
        """
        os.killpg(os.getpgid(self._sam_local_process.pid), signal.SIGTERM)   
        self._dynamodb_process.terminate()
        time.sleep(3)
        return False

    