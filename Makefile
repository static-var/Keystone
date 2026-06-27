.PHONY: test validate package regenerate

test: regenerate package validate

validate:
	python3 scripts/validate-keystone.py
	python3 scripts/validate-package.py dist/keystone.zip

package: regenerate
	scripts/package-keystone.sh

regenerate:
	python3 scripts/build-metadata.py
