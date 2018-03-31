"""
Module providing access to the Server Monitor data
"""
import boto3
from botocore.exceptions import ClientError
import time

class ServerMonitorContext:
    """
    Context used to access the server monitor data in the DB
    """

    def __init__(self):
        """
        Initializes a new instance of the L{ServerMonitorContext} class 
        """
        self.table_name = 'servers'
        self.dynamodb_client = boto3.client('dynamodb', region_name='eu-central-1', endpoint_url="http://192.168.2.159:8000")
        try:
            self.dynamodb_client.describe_table(
                TableName = self.table_name)
        except ClientError as ce:
            if ce.response['Error']['Code'] == 'ResourceNotFoundException':
                self._initializeDb()
            else:
                raise
    
    def get_server(self, serverId):
        """
        Gets a server by its serverId
        """
        server = self.dynamodb_client.get_item(
            TableName=self.table_name,
            Key={
                'server_id':{
                    'S': serverId
                }
            }
        )

        ret = None
        if 'Item' in server:            
            ret = self._unbox_record(server['Item'])
        
        return ret
    
    def list_servers(self):
        """
        Gets a list of the servers in the DB
        """
        servers = self.dynamodb_client.scan(
            TableName=self.table_name)
        unboxed_servers = []
        for server in servers['Items']:
            unboxed_servers.append(self._unbox_record(server))
        return unboxed_servers

    def delete_server(self, serverId):
        """
        Deletes a server from the DB
        """
        response = self.dynamodb_client.delete_item(
            TableName=self.table_name,
            Key={
                'server_id':{
                    'S': serverId
                },
            },
            ReturnValues='ALL_OLD'
        )
        
        ret = False
        if 'Attributes' in response:
            ret = True

        return ret

    def add_server(self, serverData):
        """
        Adds a server to the DB
        """
        server = self._box_record(serverData)
        ret = True
        try:
            self.dynamodb_client.put_item(
                TableName=self.table_name,
                Item=server,
                ConditionExpression='attribute_not_exists(server_id)'
            )
        except ClientError as err:
            if err.response['Error']['Code'] == 'ConditionalCheckFailedException':
                ret = False
            else:
                raise

        return ret

    def update_server(self, serverData):
        """
        Updates the given server in the DB
        """
        server = self._box_record(serverData)
        ret = True
        try:
            self.dynamodb_client.put_item(
                TableName=self.table_name,
                Item=server,
                ConditionExpression='attribute_exists(server_id)'
            )
        except ClientError as err:
            if err.response['Error']['Code'] == 'ConditionalCheckFailedException':
                ret = False
            else:
                raise
                
        return ret

    def _box_record(self, record):
        """
        Encapsulates a record as DynamoDB is expecting it
        """
        for key in record.keys():
            if isinstance(record[key], int) or isinstance(record[key], float):
                record[key] = {'N': str(record[key])}
            else :
                record[key] = {'S': str(record[key])}
        print('Boxed record: ' + str(record))
        return record

    def _unbox_record(self, record):
        """
        Extracts a record from the DynamoDB encapsulation
        """
        for key in record.keys():
            if 'S' in record[key]:
                record[key] = record[key]['S']
            elif 'N' in record[key]:
                if '.' in record[key]['N']:
                    record[key] = float(record[key]['N'])
                else:
                    record[key] = int(record[key]['N'])
            else:
                record[key] = 'unsupported type ' + record[key].keys()[0]
        return record
    
    def _initializeDb(self):
        """
        Initializes the DB creating the table and some test data
        """
        print('Database not initialized. Initializing DB...')
        self.dynamodb_client.create_table(
            AttributeDefinitions = [
                {
                    'AttributeName': 'server_id',
                    'AttributeType': 'S'
                }
            ],
            TableName=self.table_name,
            KeySchema=[
                {
                    'AttributeName': 'server_id',
                    'KeyType': 'HASH'
                }
            ],            
            ProvisionedThroughput={
                'ReadCapacityUnits': 5,
                'WriteCapacityUnits': 5,
            }
        )

        initialized = False
        while not(initialized):
            time.sleep(0.5)
            table_desc = self.dynamodb_client.describe_table(
                TableName = self.table_name)
            initialized = table_desc['Table']['TableStatus'] == 'ACTIVE'

        # Insert some test data
        self.dynamodb_client.batch_write_item(
            RequestItems={
                self.table_name : [
                    {
                        'PutRequest': {
                            'Item': {
                                'server_id': {
                                    'S': 'VillaconejosSQLServer01'
                                },
                                'memory': {
                                    'N': '8589934592'
                                },
                                'iisPresent': {
                                    'S': 'false'
                                }
                            }
                        }
                    },
                    {
                        'PutRequest': {
                            'Item': {
                                'server_id': {
                                    'S': 'VillaconejosSQLServer02'
                                },
                                'memory': {
                                    'N': '8589934592'
                                },
                                'iisPresent': {
                                    'S': 'false'
                                }
                            }
                        }
                    },
                    {
                        'PutRequest': {
                            'Item': {
                                'server_id': {
                                    'S': 'VillaconejosBOSServer01'
                                },
                                'memory': {
                                    'N': '1073741824'
                                },
                                'iisPresent': {
                                    'S': 'true'
                                }
                            }
                        }
                    }
                ]
            }
        )

        print('Database initialized')

# Test it!
#qlo = ServerMonitorContext()  