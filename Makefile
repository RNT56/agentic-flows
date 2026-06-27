.PHONY: install validate list graph test

install:
	python -m pip install -e . pytest

validate:
	flowctl validate

list:
	flowctl list

graph:
	flowctl graph flows/coding/feature-implementation/flow.yaml --format dot

test:
	pytest

