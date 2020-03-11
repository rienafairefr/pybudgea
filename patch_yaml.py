import copy
import json
from pprint import pprint

import jsonpatch
import yaml

from utils import parser, visit_tree


def step_change(openapi):
    patch = []

    def remapped():
        inline_schemas = []
        for schema in openapi['components']['schemas']:
            if schema.startswith('inline_response'):
                inline_schemas.append('#/components/schemas/%s' % schema)

        def inner_remapped(op):
            for k, v in openapi['paths'].items():
                ref = v.get(op, {}).get('responses', {})\
                    .get('200', {}).get('content', {}).get('application/json',{})\
                    .get('schema', {}).get('$ref')
                if ref and ref in inline_schemas:
                    newRef = k.replace('/users/{id_user}', 'User')
                    newRef = newRef.replace('/connections/{id_connection}', 'Connection')
                    newRef = newRef.replace('/connectors/{id_connector}', 'Connector')
                    newRef = newRef.replace('/accounts/{id_account}', 'Account')
                    newRef = newRef.replace('/investments/{id_investment}', 'Account')
                    newRef = newRef.replace('/transactionsclusters/{id_transactions_cluster}', 'TransactionsCluster')
                    newRef = newRef.replace('/transactions/{id_transaction}', 'Transaction')
                    newRef = newRef.replace('/recipients/{id_recipient}', 'Recipient')
                    newRef = newRef.replace('/subscriptions/{id_subscription}', 'Subscription')
                    newRef = newRef.replace('/banks/{id_connector}', 'BankConnector')
                    newRef = newRef.replace('/webhooks/{id_webhook}', 'WebHook')
                    newRef = newRef.replace('/providers/{id_connector}', 'Provider')
                    while True:
                        i = newRef.find('/')
                        if i < 0:
                            break
                        newRef = newRef[:i] + newRef[i + 1:].capitalize()
                    assert '{' not in newRef and '}' not in newRef
                    yield k, newRef

        for op in ('get', 'post'):
            for p, v in inner_remapped(op):
                yield openapi['paths'][p][op]['responses']['200']['content']['application/json']['schema'][
                          '$ref'], '#/components/schemas/%s' % v

    remap = dict(remapped())

    remapped_stacks = {
        tuple(k.split('/')[1:]): tuple(v.split('/')[1:]) for k, v in remap.items()
    }

    assert len(set(remapped_stacks.values())) == len(remapped_stacks)

    def treat_node(stack, key, node):
        if len(stack) == 2 and stack[0] == 'paths':
            if 'parameters' in node:
                for idx, param in enumerate(node['parameters']):
                    if param['name'] == 'expand':
                        patch.append({
                            "op": "add",
                            "path": "/paths/%s/%s/parameters/%s/required" % (stack[1].replace('/', '~1'), key, idx),
                            "value": False
                        })
            patch.append({
                "op": "add",
                "path": "/paths/%s/%s/security" % (stack[1].replace('/', '~1'), key),
                "value": [{'Authorization': []}]
            })
        if len(stack) == 2 and stack[0] == 'components' and stack[1] == 'schemas':
            if 'example' in node:
                patch.append({
                    "op": "remove",
                    "path": "/components/schemas/%s/example" % key
                })
        remapped_ref = remap.get(node.get('$ref'))
        if remapped_ref is not None:
            new_stack = []
            for s in stack:
                new_stack.append(s.replace('/', '~1'))
            new_stack = '/' + '/'.join(new_stack) + '/schema/$ref'
            patch.append({
                "op": "add",
                "path": new_stack,
                "value": remapped_ref
            })

        return node

    visit_tree([], treat_node, openapi)

    for old, new in remapped_stacks.items():
        patch.append({
            "op": "move",
            "from": '/' + '/'.join(old),
            "path": '/' + '/'.join(new)
        })

    patch.append({
        "op": "add",
        "path": "/components/securitySchemes",
        "value": {
            'Authorization': {
                'type': 'apiKey',
                'in': 'header',
                'name': 'Authorization',
            }
        }
    })

    return patch


args = parser.parse_args()

with open(args.input, 'r') as input_yaml:
    openapi_content = yaml.load(input_yaml, Loader=yaml.SafeLoader)
    patch = step_change(openapi_content)
    pprint(patch)
    jp = jsonpatch.JsonPatch(patch)
    jp.apply(openapi_content, in_place=True)

with open(args.output, 'w') as output_yaml:
    yaml.safe_dump(openapi_content, output_yaml, indent=2)
