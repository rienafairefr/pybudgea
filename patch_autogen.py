import re

import yaml
from inflection import camelize

from utils import parser


def sanitize_value(value, replace_match, replace_value, exception_list):
    if len(exception_list) == 0 or replace_match not in exception_list:
        return value.replace(replace_match, replace_value)
    return value


def sanitize_name(name, remove_char_regex=r'\W', exception_list=None):
    exception_list = exception_list or []
    if name is None:
        return 'ERROR_UNKNOWN'
    if name == '$':
        return 'value'

    name = sanitize_value(name, r'\[\]', "", exception_list)

    # input[] => input
    name = sanitize_value(name, r"\[\]", "", exception_list)

    # input[a][b] => input_a_b
    name = sanitize_value(name, r"\[", "_", exception_list)
    name = sanitize_value(name, r"\]", "", exception_list)

    # input(a)(b) => input_a_b
    name = sanitize_value(name, r"\(", "_", exception_list)
    name = sanitize_value(name, r"\)", "", exception_list)

    # input.name => input_name
    name = sanitize_value(name, r"\.", "_", exception_list)

    # input-name => input_name
    name = sanitize_value(name, "-", "_", exception_list)

    # a|b => a_b
    name = sanitize_value(name, r"\|", "_", exception_list)

    # input name and age => input_name_and_age
    name = sanitize_value(name, " ", "_", exception_list)

    # /api/films/get => _api_films_get
    # \api\films\get => _api_films_get
    name = name.replace("/", "_")
    name = name.replace(r"\\", "_")

    # remove everything else other than word, number and _
    # $php_variable => php_variable
    name = re.sub(remove_char_regex, "", name)
    return name


def autogen_operation_id(path, http_method):
    tmp_path = path.replace('\{', "")
    tmp_path = tmp_path.replace('\}', "")
    parts = (tmp_path + '/' + http_method).split('/')
    builder = ""
    if tmp_path == '/':
        builder += 'root'
    for part in parts:
        if len(part) > 0:
            if len(builder) == 0:
                part = part[0].lower() + part[1:]
            else:
                part = camelize(part)
            builder += part
    return sanitize_name(builder)


def step_autogen(openapi):
    for path, v in openapi.get('paths', {}).items():
        for method, value in v.items():
            if 'operationId' not in value:
                value['operationId'] = autogen_operation_id(path, method)
    return openapi


args = parser.parse_args()

with open(args.input, 'r') as input_yaml,\
        open(args.output, 'w') as output_yaml:
    openapi_content = yaml.load(input_yaml, Loader=yaml.SafeLoader)
    openapi_content = step_autogen(openapi_content)
    yaml.dump(openapi_content, output_yaml, indent=2)
