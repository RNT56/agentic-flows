.PHONY: install validate validate-event validate-run report list graph test

install:
	python -m pip install -e . pytest

validate:
	flowctl validate

validate-event:
	flowctl validate-event examples/

validate-run:
	flowctl validate-run examples/runs/

report:
	flowctl report

list:
	flowctl list

graph:
	flowctl graph flows/coding/feature-implementation/flow.yaml --format dot

test:
	pytest
