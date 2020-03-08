import json

import yaml
import jsonpatch

from utils import NoDatesSafeLoader


src = yaml.load(open('openapi_1.yaml'), Loader=NoDatesSafeLoader)
dst = yaml.load(open('openapi_2.yaml'), Loader=NoDatesSafeLoader)

diffed = jsonpatch.JsonPatch.from_diff(src, dst)

json.dump(diffed.patch, open('diff_openapi.json', 'w'))

