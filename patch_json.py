import json

from utils import parser


def step0(swagger):
    for path, node in swagger['paths'].items():
        for method, operation in node.items():
            if 'parameters' in operation:
                parameters = operation['parameters']
                for param in parameters:
                    if param['in'] == 'formData':
                        operation.setdefault('consumes', [])
                        if 'multipart/form-data' not in operation['consumes']:
                            operation['consumes'].append('multipart/form-data')
            if 'responses' in operation:
                for code, value in operation['responses'].items():
                    if 'examples' in value:
                        value.get('schema', {})['example'] = value.pop('examples')
    return swagger


args = parser.parse_args()

with open(args.input, 'r') as swagger_json:
    swagger_content = json.load(swagger_json)
    swagger_content = step0(swagger_content)

with open(args.output, 'w') as swagger_patched_json:
    json.dump(swagger_content, swagger_patched_json, indent=2)
