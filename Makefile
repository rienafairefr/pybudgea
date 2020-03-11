.PHONY: clean

VERSION ?= $(shell pipenv run python -c "from setuptools_scm import get_version;print(get_version())")
OPENAPIGEN_VERSION ?= v4.2.3

test:setupto
	pipenv run py.test tests

clean:
	rm -rf api
	rm -f openapi.yaml
	rm -f openapi_*.yaml
	rm -f swagger_*.json

swagger_00.json: swagger.json
	pipenv run python patch_json.py -i swagger.json -o swagger_00.json

openapi_00.yaml: swagger_00.json
	docker run --rm --user `id -u`:`id -g` -v ${PWD}:/local openapitools/openapi-generator-cli:${OPENAPIGEN_VERSION} \
	           generate -i /local/swagger_00.json \
	           -g openapi-yaml -o /local/openapi-yaml
	cp openapi-yaml/openapi/openapi.yaml openapi_00.yaml
	rm -rf openapi-yaml

openapi_05.yaml: openapi_00.yaml merge_in_yaml.py merge_in_0.yaml
	pipenv run python merge_in_yaml.py -i openapi_00.yaml -o openapi_05.yaml -m merge_in_0.yaml

openapi_06.yaml: openapi_05.yaml patch_yaml.py
	pipenv run python patch_yaml.py -i openapi_05.yaml -o openapi_06.yaml

openapi_10.yaml: openapi_06.yaml merge_in.yaml merge_in_yaml.py
	pipenv run python merge_in_yaml.py -i openapi_06.yaml -o openapi_10.yaml -m merge_in.yaml

openapi_20.yaml: openapi_10.yaml patch_autogen.py
	pipenv run python patch_autogen.py -i openapi_10.yaml -o openapi_20.yaml

openapi.yaml: openapi_20.yaml diff_openapi.json patch_diff_yaml.py
	pipenv run python patch_diff_yaml.py -i openapi_20.yaml -o openapi.yaml -d diff_openapi.json

docker_image: $(wildcard generator/**/*) $(wildcard generator/*)
	docker build -t pybudgea-custom-codegen generator

clean_api:
	rm -rf api

api: openapi.yaml Makefile $(wildcard templates/**/*) $(wildcard templates/*) docker_image
	docker run --rm --user `id -u`:`id -g` -v ${PWD}:/local pybudgea-custom-codegen \
	           generate -i /local/openapi.yaml \
	           -t /local/templates \
	           --git-user-id rienafairefr \
	           --git-repo-id pybudgea \
	           -g eu.rienafairefr.customcodegen.PythonCustomCodegen -o /local/api \
	           -p projectName=pybudgea \
	           -p packageName=budgea \
	           -p packageVersion="$(VERSION)" \
	           -p appName="pybudgea" \
	           -p infoEmail="rienafairefr@gmail.com"
