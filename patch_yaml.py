import collections

import six
import yaml


def nested_set(dic, keys, value):
    for key in keys[:-1]:
        dic = dic.setdefault(key, {})
    dic[keys[-1]] = value


def visit_tree(stack, func, r):
    for k, v in r.items():
        if isinstance(v, dict):
            r[k] = func(stack, v)
            stack.append(k)
            visit_tree(stack, func, v)
            stack.pop()


with open('openapi.yaml', 'r') as openapi_yaml:
    openapi = yaml.load(openapi_yaml, Loader=yaml.SafeLoader)

    def remapped():
        inline_schemas = []
        for schema in openapi['components']['schemas']:
            if schema.startswith('inline_response'):
                inline_schemas.append('#/components/schemas/%s' % schema)

        def inner_remapped(op):
            for k, v in openapi['paths'].items():
                ref = v.get(op, {}).get('responses', {}).get(200, {}).get('content', {}).get('application/json', {}).get(
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
                yield openapi['paths'][p][op]['responses'][200]['content']['application/json']['schema'][
                    '$ref'], '#/components/schemas/%s' % v

    remap = dict(remapped())

    remapped_stacks = {
        tuple(k.split('/')[1:]): tuple(v.split('/')[1:]) for k, v in remap.items()
    }

    assert len(set(remapped_stacks.values())) == len(remapped_stacks)

    def treat_node(stack, node):
        if 'parameters' in node:
            parameters = node['parameters']
            for param in parameters:
                if param['name'] == 'expand':
                    param['required'] = False
        if 'content' in node:
            if len(node['content'].keys()) > 1:
                pass
        remapped_ref = remap.get(node.get('$ref'))
        if remapped_ref is not None:
            node['$ref'] = remapped_ref
        if 'required' in node and isinstance(node['required'], list):
            if 'id_weboob' in node['required']:
                node['required'].remove('id_weboob')

        if len(stack) == 2 and stack[0] == 'paths':
            node['security'] = [
                {'Authorization': []}
            ]
        return node


    visit_tree([], treat_node, openapi)

    for old, new in remapped_stacks.items():
        el = openapi
        for path_el in old:
            el = el[path_el]

        nested_set(openapi, new, el)

        el = openapi
        for path_el in old[:-1]:
            el = el[path_el]
        del el[old[-1]]

    openapi['components']['securitySchemes'] = {
        'Authorization': {
            'type': 'apiKey',
            'in': 'header',
            'name': 'Authorization',
        }
    }


def update(d, u):
    for k, v in six.iteritems(u):
        dv = d.get(k, {})
        if not isinstance(dv, collections.Mapping):
            d[k] = v
        elif isinstance(v, collections.Mapping):
            d[k] = update(dv, v)
        else:
            d[k] = v
    return d


with open('merge_in.yaml', 'r') as merge_in_yaml:
    merge_in = yaml.safe_load(merge_in_yaml)

openapi = update(openapi, merge_in)
openapi['servers'][0]['url'] = 'http:' + openapi['servers'][0]['url']

with open('openapi_patched.yaml', 'w') as openapi_yaml:
    yaml.dump(openapi, openapi_yaml, indent=2)
