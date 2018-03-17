from botocore.exceptions import ClientError
import json
import sys

from dal.server_monitor_context import ServerMonitorContext

def handler(event, context):
    try:
        dbContext = ServerMonitorContext()

        # Take a look to the event received
        print('Event Information: ' + str(event))

        ret = None

        if event['httpMethod'] == 'GET':
            if event['pathParameters'] is not None:
                ret = _get_server(dbContext, event['pathParameters']['serverId'])
            else:
                ret = _list_servers(dbContext)
        elif event['httpMethod'] == 'DELETE':
            ret = _delete_server(dbContext, event['pathParameters']['serverId'])
        elif event['httpMethod'] == 'POST':
            ret = _add_server(dbContext, event['body'])
        elif event['httpMethod'] == 'PUT':
            ret = _update_server(dbContext, event['body'])

        return ret
    except ClientError as err:
        print(err)
        return {
            "statusCode": 500,
            "body": str(err)
        }
    except:
        print("Unexpected error: " + str(sys.exc_info()[0]))
        raise

def _get_server(dbContext, serverId):
    server = dbContext.get_server(serverId)
    print(server)
    ret = None
    if server is not None:
        ret = {
            'statusCode': 200,
            'body': json.dumps(server)
        }
    else:
        ret = {
            'statusCode': 404,
            'body': 'server not found'
        }

    return ret

def _list_servers(dbContext):
    servers = dbContext.list_servers()
    print(servers)
    return {
        'statusCode': 200,
        'body': json.dumps(servers)
    }

def _delete_server(dbContext, serverId):
    ret = None
    if dbContext.delete_server(serverId):
        ret = {
            'statusCode': 200,
            'body': 'server deleted'
        }
    else:
        ret = {
            'statusCode': 404,
            'body': 'server not found'
        }

    return ret

def _add_server(dbContext, serverData):
    print(serverData)
    server = json.loads(serverData)
    ret = None
    if dbContext.add_server(server):
        ret = {
            'statusCode': 201,
            'body': 'server added'
        }
    else:
        ret = {
            'statusCode': 409,
            'body': 'server already exists'
        }

    return ret

def _update_server(dbContext, serverData):
    print(serverData)
    server = json.loads(serverData)
    ret = None
    if dbContext.update_server(server):
        ret = {
            'statusCode': 200,
            'body': 'server updated'
        }
    else:
        ret = {
            'statusCode': 404,
            'body': 'server not found'
        }

    return ret
