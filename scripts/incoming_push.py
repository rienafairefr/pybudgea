import json

from budgea.models.push import PushSchema

data = json.load(open('incoming_push.json', 'r'))

push = PushSchema().load(data)

pass