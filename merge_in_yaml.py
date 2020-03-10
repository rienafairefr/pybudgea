from collections import Mapping

import yaml

from utils import parser


def update(d, u):
    for k, v in u.items():
        dv = d.get(k, {})
        if not isinstance(dv, Mapping):
            d[k] = v
        elif isinstance(v, Mapping):
            d[k] = update(dv, v)
        else:
            d[k] = v
    return d


parser.add_argument('-m', dest='merge')
args = parser.parse_args()


with open(args.input, 'r') as input_yaml,\
        open(args.merge, 'r') as merge_in_yaml:
    openapi = yaml.load(input_yaml, Loader=yaml.SafeLoader)
    merge_in = yaml.safe_load(merge_in_yaml)
    updated_openapi = update(openapi, merge_in)

with open(args.output, 'w') as output_yaml:
    yaml.dump(updated_openapi, output_yaml, indent=2)
