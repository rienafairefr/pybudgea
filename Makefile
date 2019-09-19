.PHONY: clean

VERSION ?= $(shell pipenv run python -c "from setuptools_scm import get_version;print(get_version())")
OPENAPIGEN_VERSION ?= v3.3.4

test:setupto
	pipenv run py.test tests

clean:
	rm -rf api
	rm -f openapi.yaml

openapi.yaml: merge_in.yaml swagger.json
	docker run --rm --user `id -u`:`id -g` -v ${PWD}:/local openapitools/openapi-generator-cli:${OPENAPIGEN_VERSION} \
	           generate -i /local/swagger.json \
	           -g openapi-yaml -o /local/openapi-yaml
	cp openapi-yaml/openapi/openapi.yaml openapi.yaml
	rm -rf openapi-yaml
	pipenv run python patch_yaml.py

api: openapi.yaml Makefile
	docker run --rm --user `id -u`:`id -g` -v ${PWD}:/local openapitools/openapi-generator-cli:${OPENAPIGEN_VERSION} \
	           generate -i /local/openapi.yaml \
	           --git-user-id rienafairefr \
	           --git-repo-id pybudgea \
	           -g python -o /local/api -DprojectName=pybudgea -DpackageName=budgea \
	           -DpackageVersion="$(VERSION)" -DappDescription="This is pybudgea, an autogenerated package to access Budget Insight API"\
	           -DappName="pybudgea" -DinfoEmail="rienafairefr@gmail.com"
