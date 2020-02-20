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

swagger_patched.json: swagger.json
	pipenv run python patch_json.py

openapi.yaml: swagger_patched.json
	docker run --rm --user `id -u`:`id -g` -v ${PWD}:/local openapitools/openapi-generator-cli:${OPENAPIGEN_VERSION} \
	           generate -i /local/swagger_patched.json \
	           -g openapi-yaml -o /local/openapi-yaml
	cp openapi-yaml/openapi/openapi.yaml openapi.yaml
	rm -rf openapi-yaml

openapi_patched.yaml: merge_in.yaml swagger_patched.json openapi.yaml
	pipenv run python patch_yaml.py

docker_image: $(wildcard generator/**/*)  $(wildcard generator/*)
	docker build -t pybudgea-custom-codegen generator

api: openapi_patched.yaml Makefile $(wildcard templates/**/*) $(wildcard templates/*) docker_image
	docker run --rm --user `id -u`:`id -g` -v ${PWD}:/local openapitools/openapi-generator-cli:${OPENAPIGEN_VERSION} \
	           generate -i /local/openapi_patched.yaml \
	           -t /local/templates \
	           --git-user-id rienafairefr \
	           --git-repo-id pybudgea \
	           -g python -o /local/api \
	           -p projectName=pybudgea \
	           -p packageName=budgea \
	           -p packageVersion="$(VERSION)" \
	           -p appName="pybudgea" \
	           -p infoEmail="rienafairefr@gmail.com"
	docker run --rm --user `id -u`:`id -g` -v ${PWD}:/local pybudgea-custom-codegen \
	           generate -i /local/openapi_patched.yaml \
	           -g customcodegen -o /local/api \
	           -p packageName=budgea
