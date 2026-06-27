.PHONY: test validate package regenerate routing py-compile

test: validate routing py-compile

validate: package
	python3 scripts/validate-keystone.py
	python3 scripts/validate-package.py dist/keystone.zip

routing:
	python3 -m unittest tests/test_routing.py

py-compile:
	python3 -m py_compile scripts/build-metadata.py scripts/validate-keystone.py scripts/validate-package.py tests/test_routing.py

package: regenerate
	scripts/package-keystone.sh

regenerate:
	python3 scripts/build-metadata.py
