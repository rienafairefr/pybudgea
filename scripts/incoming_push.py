import json

from marshmallow import EXCLUDE

from budgea.schemas import PushSchema, ConnectionAccountSchema

data = json.load(open('incoming_push.json', 'r'))
#data = json.load(open('incomping_push_connection_account.json', 'r'))

push = PushSchema().load(data)
#ConnectionAccountSchema().load(data)


pass