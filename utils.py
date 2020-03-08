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