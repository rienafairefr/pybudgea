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


with open('swagger.yaml', 'r') as swagger_yaml:
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
        print(stack)
        if node.get('name') == 'expand':
            node['required'] = False
        remapped_ref = remap.get(node.get('$ref'))
        if remapped_ref is not None:
            node['$ref'] = remapped_ref
        if len(stack) == 3 and stack[0] == 'paths':
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
            'name': 'authorization',
        }
    }

with open('swagger.yaml', 'w') as swagger_yaml:
    yaml.dump(swagger, swagger_yaml)
