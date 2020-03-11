import jsonpatch
import yaml

from utils import parser

parser.add_argument('-d', dest='diff')

args = parser.parse_args()

with open(args.diff, 'r') as patch_file, \
        open(args.input, 'r') as input_yaml:
    openapi = yaml.load(input_yaml, Loader=yaml.SafeLoader)
    json_patch = jsonpatch.JsonPatch.from_string(patch_file.read())
    json_patch.apply(openapi, in_place=True)

with open(args.output, 'w') as output_yaml:
    yaml.safe_dump(openapi, output_yaml, indent=2)
