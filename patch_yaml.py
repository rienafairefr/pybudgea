import collections

import six
import yaml


def visit_tree(stack, func, r):
    for k, v in r.items():
        if isinstance(v, dict):
            r[k] = func(stack, v)
            stack.append(k)
            visit_tree(stack, func, v)
            stack.pop()


def nested_set(dic, keys, value):
    for key in keys[:-1]:
        dic = dic.setdefault(key, {})
    dic[keys[-1]] = value


with open('openapi.yaml', 'r') as swagger_yaml:
    swagger = yaml.load(swagger_yaml, Loader=yaml.SafeLoader)

    remapped_get = {
        '/connections': 'ConnectionsList',
        '/account_types': 'AccountTypesList',
        '/banks/{id_connector}/logos': 'ConnectorLogosList',
        '/categories': 'CategoriesList'
    }

    remap = {
        swagger['paths'][p]['get']['responses'][200]['content']['application/json']['schema'][
            '$ref']: '#/components/schemas/%s' % v
        for p, v in remapped_get.items()
    }

    remapped_stacks = {
        tuple(k.split('/')[1:]): tuple(v.split('/')[1:]) for k, v in remap.items()
    }


    def treat_node(stack, node):
        if 'parameters' in node:
            parameters = node['parameters']
            for param in parameters:
                if param['name'] == 'expand':
                    param['required'] = False
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


    visit_tree([], treat_node, swagger)

    for old, new in remapped_stacks.items():
        el = swagger
        for path_el in old:
            el = el[path_el]

        nested_set(swagger, new, el)

        el = swagger
        for path_el in old[:-1]:
            el = el[path_el]
        del el[old[-1]]

    swagger['components']['securitySchemes'] = {
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

swagger = update(swagger, merge_in)

with open('openapi.yaml', 'w') as swagger_yaml:
    yaml.dump(swagger, swagger_yaml, indent=2)
