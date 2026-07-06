.PHONY: install test lint scan app-build app-run

install:
	pip install -r requirements-dev.txt

test:
	pytest

lint:
	ruff check deploylens tests

scan:
	python -m deploylens scan manifests/base --output reports/deploylens-report.md --json-output reports/deploylens-report.json

app-build:
	docker build -t deploylens-sample:latest sample-app

app-run:
	docker run --rm -p 8080:8080 deploylens-sample:latest
