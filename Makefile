.PHONY: clean

VERSION ?= $(shell pipenv run python -c "from setuptools_scm import get_version;print(get_version())")
OPENAPIGEN_VERSION ?= v4.2.3

test:setupto
	pipenv run py.test tests

clean:
	rm -rf api
	rm -f openapi.yaml
	rm -f openapi_patched.yaml
	rm -f swagger_patched.json

swagger_0.json: swagger.json
	pipenv run python patch_json.py

openapi.yaml: swagger_patched.json
	docker run --rm --user `id -u`:`id -g` -v ${PWD}:/local openapitools/openapi-generator-cli:${OPENAPIGEN_VERSION} \
	           generate -i /local/swagger_patched.json \
	           -g openapi-yaml -o /local/openapi-yaml
	cp openapi-yaml/openapi/openapi.yaml openapi.yaml
	rm -rf openapi-yaml

openapi_00.yaml: openapi.yaml merge_in_yaml.py merge_in_0.yaml
	pipenv run python merge_in_yaml.py -i openapi.yaml -o openapi_00.yaml -m merge_in_0.yaml

openapi_0.yaml: openapi_00.yaml patch_yaml.py
	pipenv run python patch_yaml.py -i openapi_00.yaml -o openapi_0.yaml

openapi_1.yaml: openapi_0.yaml merge_in.yaml merge_in_yaml.py
	pipenv run python merge_in_yaml.py -i openapi_0.yaml -o openapi_1.yaml -m merge_in.yaml

openapi_2.yaml: openapi_1.yaml diff_openapi.json patch_diff_yaml.py
	pipenv run python patch_diff_yaml.py -i openapi_1.yaml -o openapi_2.yaml -d diff_openapi.json

docker_image: $(wildcard generator/**/*) $(wildcard generator/*)
	docker build -t pybudgea-custom-codegen generator

clean_api:
	rm -rf api

api: openapi_2.yaml Makefile $(wildcard templates/**/*) $(wildcard templates/*) docker_image
	docker run --rm --user `id -u`:`id -g` -v ${PWD}:/local pybudgea-custom-codegen \
	           generate -i /local/openapi_2.yaml \
	           -t /local/templates \
	           --git-user-id rienafairefr \
	           --git-repo-id pybudgea \
	           -g eu.rienafairefr.customcodegen.PythonCustomCodegen -o /local/api \
	           -p projectName=pybudgea \
	           -p packageName=budgea \
	           -p packageVersion="$(VERSION)" \
	           -p appName="pybudgea" \
	           -p infoEmail="rienafairefr@gmail.com"
	docker run --rm --user `id -u`:`id -g` -v ${PWD}:/local pybudgea-custom-codegen \
	           generate -i /local/openapi_2.yaml \
	           -g eu.rienafairefr.customcodegen.CustomCodegen -o /local/api \
	           -p packageName=budgea
