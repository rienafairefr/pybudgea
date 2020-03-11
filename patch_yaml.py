from pprint import pprint

import jsonpatch
import yaml

from utils import parser


def step_change(openapi):
    patch = []

    def get_new_ref(path):
        new_ref = path.replace('/users/{id_user}', 'User')
        new_ref = new_ref.replace('/connections/{id_connection}', 'Connection')
        new_ref = new_ref.replace('/connectors/{id_connector}', 'Connector')
        new_ref = new_ref.replace('/accounts/{id_account}', 'Account')
        new_ref = new_ref.replace('/investments/{id_investment}', 'Account')
        new_ref = new_ref.replace('/transactionsclusters/{id_transactions_cluster}', 'TransactionsCluster')
        new_ref = new_ref.replace('/transactions/{id_transaction}', 'Transaction')
        new_ref = new_ref.replace('/recipients/{id_recipient}', 'Recipient')
        new_ref = new_ref.replace('/subscriptions/{id_subscription}', 'Subscription')
        new_ref = new_ref.replace('/banks/{id_connector}', 'BankConnector')
        new_ref = new_ref.replace('/webhooks/{id_webhook}', 'WebHook')
        new_ref = new_ref.replace('/providers/{id_connector}', 'Provider')
        while True:
            i = new_ref.find('/')
            if i < 0:
                break
            new_ref = new_ref[:i] + new_ref[i + 1:].capitalize()
        assert '{' not in new_ref and '}' not in new_ref
        return new_ref

    def remapped():
        for k, v in openapi['paths'].items():
            for op in 'get', 'post':
                ref = v.get(op, {}).get('responses', {}) \
                    .get('200', {}).get('content', {}).get('application/json', {}) \
                    .get('schema', {}).get('$ref')

                if ref and 'inline_response' in ref:
                    new_ref = get_new_ref(k)
                    yield openapi['paths'][k][op]['responses']['200']['content']['application/json']['schema'][
                              '$ref'], '#/components/schemas/%s' % new_ref

    remap = {}
    for k, v in remapped():
        value = remap.get(k)
        if value is None or len(value) > len(v):
            remap[k] = v

    remapped_stacks = {
        tuple(k.split('/')[1:]): tuple(v.split('/')[1:]) for k, v in remap.items()
    }

    assert len(set(remapped_stacks.values())) == len(remapped_stacks)

    for url, item in openapi.get('paths').items():
        safe_url = url.replace('/', '~1')
        for method, node in item.items():
            for idx, param in enumerate(node.get('parameters', [])):
                if param['name'] == 'expand':
                    patch.append({
                        "op": "add",
                        "path": "/paths/%s/%s/parameters/%i/required" % (safe_url, method, idx),
                        "value": False
                    })
            patch.append({
                "op": "add",
                "path": "/paths/%s/%s/security" % (safe_url, method),
                "value": [{'Authorization': []}]
            })
            schema_ref = node.get('responses', {}).get('200', {}).get('content', {})\
                .get('application/json', {}).get('schema', {}).get('$ref')
            remapped_ref = remap.get(schema_ref)
            if schema_ref and remapped_ref:
                patch.append({
                    "op": "add",
                    "path": '/paths/%s/%s/responses/200/content/application~1json/schema/$ref' % (safe_url, method),
                    "value": remapped_ref
                })

    for name, item in openapi.get('components', {}).get('schemas', {}).items():
        if 'example' in item:
            patch.append({
                "op": "remove",
                "path": "/components/schemas/%s/example" % name
            })

    for old, new in remapped_stacks.items():
        patch.append({
            "op": "move",
            "from": '/' + '/'.join(old),
            "path": '/' + '/'.join(new)
        })

    patch.append({
        "op": "add",
        "path": "/components/securitySchemes",
        "value": {
            'Authorization': {
                'type': 'apiKey',
                'in': 'header',
                'name': 'Authorization',
            }
        }
    })

    return patch


args = parser.parse_args()

with open(args.input, 'r') as input_yaml:
    openapi_content = yaml.load(input_yaml, Loader=yaml.SafeLoader)
    patch = step_change(openapi_content)
    pprint(patch)
    jp = jsonpatch.JsonPatch(patch)
    jp.apply(openapi_content, in_place=True)

with open(args.output, 'w') as output_yaml:
    yaml.safe_dump(openapi_content, output_yaml, indent=2)
