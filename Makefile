.PHONY: test validate package regenerate routing unit py-compile

test: validate unit py-compile

validate: package
	python3 scripts/validate-keystone.py
	python3 scripts/validate-package.py dist/keystone.zip

routing:
	python3 -m unittest tests/test_routing.py

unit:
	python3 -m unittest discover -s tests -p 'test_*.py'

py-compile:
	python3 -m py_compile scripts/build-metadata.py scripts/validate-keystone.py scripts/validate-package.py tests/test_routing.py tests/test_package_validator.py

package: regenerate
	scripts/package-keystone.sh

regenerate:
	python3 scripts/build-metadata.py
