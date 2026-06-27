.PHONY: install validate validate-event list graph test

install:
	python -m pip install -e . pytest

validate:
	flowctl validate

validate-event:
	flowctl validate-event examples/

list:
	flowctl list

graph:
	flowctl graph flows/coding/feature-implementation/flow.yaml --format dot

test:
	pytest
