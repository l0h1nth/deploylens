.PHONY: install test lint scan scan-dev scan-prod app-build app-run

install:
	pip install -r requirements-dev.txt

test:
	pytest

lint:
	ruff check deploylens tests

scan:
	python -m deploylens scan manifests/dev --environment dev --output reports/deploylens-dev-report.md --json-output reports/deploylens-dev-report.json --fail-threshold 101
	python -m deploylens scan manifests/prod --environment prod --output reports/deploylens-prod-report.md --json-output reports/deploylens-prod-report.json --fail-threshold 80

scan-dev:
	python -m deploylens scan manifests/dev --environment dev --output reports/deploylens-dev-report.md --json-output reports/deploylens-dev-report.json --fail-threshold 101

scan-prod:
	python -m deploylens scan manifests/prod --environment prod --output reports/deploylens-prod-report.md --json-output reports/deploylens-prod-report.json --fail-threshold 80

app-build:
	docker build -t deploylens-sample:latest sample-app

app-run:
	docker run --rm -p 8080:8080 deploylens-sample:latest
