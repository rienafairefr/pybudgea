import collections
import re

import yaml
from inflection import camelize


def nested_set(dic, keys, value):
    for key in keys[:-1]:
        dic = dic.setdefault(key, {})
    dic[keys[-1]] = value


def visit_tree(stack, func, r):
    for k, v in r.items():
        if isinstance(v, dict):
            r[k] = func(stack, k, v)
            stack.append(k)
            visit_tree(stack, func, v)
            stack.pop()


with open('openapi.yaml', 'r') as openapi_yaml:
    openapi = yaml.load(openapi_yaml, Loader=yaml.SafeLoader)


    def sanitize_value(value, replace_match, replace_value, exception_list):
        if len(exception_list) == 0 or replace_match not in exception_list:
            return value.replace(replace_match, replace_value)
        return value

    def sanitize_name(name, remove_char_regex=r'\W', exception_list=None):
        exception_list = exception_list or []
        if name is None:
            return 'ERROR_UNKNOWN'
        if name == '$':
            return 'value'

        name = sanitize_value(name, r'\[\]', "", exception_list)

        # input[] => input
        name = sanitize_value(name, r"\[\]", "", exception_list)

        # input[a][b] => input_a_b
        name = sanitize_value(name, r"\[", "_", exception_list)
        name = sanitize_value(name, r"\]", "", exception_list)

        # input(a)(b) => input_a_b
        name = sanitize_value(name, r"\(", "_", exception_list)
        name = sanitize_value(name, r"\)", "", exception_list)

        # input.name => input_name
        name = sanitize_value(name, r"\.", "_", exception_list)

        # input-name => input_name
        name = sanitize_value(name, "-", "_", exception_list)

        # a|b => a_b
        name = sanitize_value(name, r"\|", "_", exception_list)

        # input name and age => input_name_and_age
        name = sanitize_value(name, " ", "_", exception_list)

        # /api/films/get => _api_films_get
        # \api\films\get => _api_films_get
        name = name.replace("/", "_")
        name = name.replace(r"\\", "_")

        # remove everything else other than word, number and _
        # $php_variable => php_variable
        name = re.sub(remove_char_regex, "", name)
        return name

    def autogen_operation_id(path, http_method):
        tmp_path = path.replace('\{', "")
        tmp_path = tmp_path.replace('\}', "")
        parts = (tmp_path + '/' + http_method).split('/')
        builder = ""
        if tmp_path == '/':
            builder += 'root'
        for part in parts:
            if len(part) > 0:
                if len(builder) == 0:
                    part = part[0].lower() + part[1:]
                else:
                    part = camelize(part)
                builder += part
        return sanitize_name(builder)

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
            if 'operationId' not in node:
                node['operationId'] = autogen_operation_id(stack[-1], key)
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
    for k, v in u.items():
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
