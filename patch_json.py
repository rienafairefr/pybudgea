import json


with open('swagger.json', 'r') as swagger_json:
    swagger = json.load(swagger_json)

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


with open('swagger_patched.json', 'w') as swagger_patched_json:
    json.dump(swagger, swagger_patched_json, indent=2)
