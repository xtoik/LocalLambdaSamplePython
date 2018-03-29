
CONFIG
======
Specify the IP address of your machine in the __init__ method of the class ./dal/server_monitor_context.py

LAUNCH
======
sam local start-api

java -Djava.library.path=./dist/DynamoDBLocal_lib -jar ./dist/DynamoDBLocal.jar -inMemory

TEST
====
List: curl http://localhost:3000/servers

Get: curl http://localhost:3000/server/VillaconejosSQLServer01

Add: curl -H "Content-Type: application/json" -X POST -d '{"server_id":"VillaconejosSQLServer02", "iisPresent":"false", "memory": 1073741824, "upToDate": "false"}' http://localhost:3000/server

Delete: curl -X DELETE http://localhost:3000/server/VillaconejosSQLServer01

Update: curl -H "Content-Type: application/json" -X PUT -d '{"server_id":"VillaconejosSQLServer01", "iisPresent":"false", "memory": 1073741824, "upToDate": "true"}' http://localhost:3000/server


ENJOY!
======