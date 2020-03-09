import json

import yaml

from utils import parser, nested_set, visit_tree


def step_change(openapi):
    def remapped():
        inline_schemas = []
        for schema in openapi['components']['schemas']:
            if schema.startswith('inline_response'):
                inline_schemas.append('#/components/schemas/%s' % schema)

        def inner_remapped(op):
            for k, v in openapi['paths'].items():
                ref = v.get(op, {}).get('responses', {}).get('200', {}).get('content', {}).get('application/json', {}).get(
                    'schema', {}).get('$ref')
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
                parameters = node['parameters']
                for param in parameters:
                    if param['name'] == 'expand':
                        param['required'] = False
            node['security'] = [
                {'Authorization': []}
            ]
        if len(stack) == 2 and stack[0] == 'components' and stack[1] == 'schemas':
            if 'example' in node:
                del node['example']
            if 'properties' in node:
                for k, v in node['properties'].items():
                    if v.get('type') == 'object' and v.get('title') is None:
                        # should have been inlined
                        json_path = '/%s/%s/properties/%s' % ('/'.join(stack), key, k)

                        print('should be added to the json-patch:' + json.dumps({
                            'op': 'replace', 'path': json_path,
                            'value': {'#ref': '$/components/schemas/****'}
                        }))
        remapped_ref = remap.get(node.get('$ref'))
        if remapped_ref is not None:
            node['$ref'] = remapped_ref
        if 'required' in node and isinstance(node['required'], list):
            if 'id_weboob' in node['required']:
                node['required'].remove('id_weboob')

        return node

    for old, new in remapped_stacks.items():
        el = openapi
        for path_el in old:
            el = el[path_el]

        nested_set(openapi, new, el)

        el = openapi
        for path_el in old[:-1]:
            el = el[path_el]
        del el[old[-1]]

    visit_tree([], treat_node, openapi)

    openapi['components']['securitySchemes'] = {
        'Authorization': {
            'type': 'apiKey',
            'in': 'header',
            'name': 'Authorization',
        }
    }

    openapi['servers'][0]['url'] = 'http:' + openapi['servers'][0]['url']

    return openapi


args = parser.parse_args()

with open(args.input, 'r') as input_yaml,\
        open(args.output, 'w') as output_yaml:
    openapi_content = yaml.load(input_yaml, Loader=yaml.SafeLoader)
    openapi_content = step_change(openapi_content)
    yaml.dump(openapi_content, output_yaml, indent=2)
