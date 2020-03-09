from argparse import ArgumentParser

import yaml

NoDatesSafeLoader = yaml.SafeLoader
NoDatesSafeLoader.yaml_implicit_resolvers = {
    k: [r for r in v if r[0] != 'tag:yaml.org,2002:timestamp'] for
        k, v in NoDatesSafeLoader.yaml_implicit_resolvers.items()
}

parser = ArgumentParser()
parser.add_argument('-i', dest='input')
parser.add_argument('-o', dest='output')


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