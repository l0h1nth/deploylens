# Deployment Guide

This guide explains how to test DeployLens version 1 on your machine.

## Local Analyzer Test

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements-dev.txt
pytest
python -m deploylens scan manifests/base --output reports/deploylens-report.md --json-output reports/deploylens-report.json
```

The report should show a high or critical score because the starter Kubernetes manifest intentionally has risky settings.

## Local App Test

```bash
docker build -t deploylens-sample:latest sample-app
docker run --rm -p 8080:8080 deploylens-sample:latest
```

In another terminal:

```bash
curl http://127.0.0.1:8080/healthz
```

## Local Kubernetes Test

With `kind`:

```bash
kind create cluster --name deploylens
docker build -t deploylens-sample:latest sample-app
kind load docker-image deploylens-sample:latest --name deploylens
kubectl apply -k manifests/base
kubectl -n deploylens port-forward svc/deploylens-sample 8080:80
```

Then:

```bash
curl http://127.0.0.1:8080/healthz
```

## What To Say In The README Or Interview

DeployLens catches deployment risk before production by scanning Kubernetes manifests inside CI/CD. It checks reliability, cost, and operations signals, then generates a report that can be used as a pull request gate.
