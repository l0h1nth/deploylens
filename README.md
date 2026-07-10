# DeployLens

DeployLens is a DevOps project that answers one practical question:

> Is this deployment safe, affordable, observable, and rollback-ready before it reaches production?

 DeployLens goes one level deeper: it builds a small CI/CD guardrail that reviews Kubernetes deployment changes and produces a risk report.

## The Real Problem

Teams often ship Kubernetes changes through pull requests, but many risky details are easy to miss:

- No CPU or memory limits
- Containers using `latest` tags
- Containers running without a hardened security context
- Missing liveness or readiness probes
- Only one replica for production
- Public `LoadBalancer` services created by accident
- No rollback notes in the pull request
- No clear deployment risk score

DeployLens scans those signals and creates a simple report that a developer, DevOps engineer, or interviewer can understand.

## What Version 1 Does

- Runs a small sample web app
- Provides Kubernetes manifests for that app
- Includes a Python CLI: `deploylens`
- Validates Kubernetes YAML before risk scoring
- Scans YAML manifests for production-readiness risks
- Checks basic Kubernetes container security settings
- Estimates monthly Kubernetes resource cost from CPU and memory requests
- Generates Markdown and JSON reports
- Runs automatically in GitHub Actions
- Includes tests so the analyzer itself is trusted

## Project Structure

```text
sample-app/              # Small app we deploy and analyze
deploylens/              # The custom DevOps analyzer CLI
rules/                   # Rule configuration and scoring weights
manifests/dev/           # Dev Kubernetes manifests with intentional learning risks
manifests/prod/          # Production-style Kubernetes manifests gated by CI
reports/                 # Generated report output
docs/                    # Learning notes, architecture, deployment guide
tests/                   # Analyzer tests
.github/workflows/       # CI pipeline
```

## Run It Locally

Create a virtual environment:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements-dev.txt
```

Run tests:

```bash
pytest
```

Validate Kubernetes manifests:

```bash
make validate
```

Generate a deployment risk report:

```bash
make scan
```

Open the report:

```bash
sed -n '1,220p' reports/deploylens-dev-report.md
sed -n '1,220p' reports/deploylens-prod-report.md
```

## Run The Sample App

```bash
docker build -t deploylens-sample:latest sample-app
docker run --rm -p 8080:8080 deploylens-sample:latest
```

Test it:

```bash
curl http://127.0.0.1:8080/healthz
curl http://127.0.0.1:8080/
```

## Deploy Locally To Kubernetes

Install a local Kubernetes tool such as `kind` or `minikube`, then:

```bash
kubectl apply -k manifests/dev
kubectl -n deploylens get pods
kubectl -n deploylens port-forward svc/deploylens-sample 8080:80
curl http://127.0.0.1:8080/healthz
```

If you use `kind`, load the local image before applying manifests:

```bash
kind load docker-image deploylens-sample:latest
```

## CI Pipeline

The GitHub Actions workflow:

- run Python tests
- lint the code
- validate dev and prod Kubernetes manifests
- build the sample app image
- generate dev and prod DeployLens risk reports
- block production manifests when the risk score is 80 or higher
- upload the report as a CI artifact

## Interview Pitch

> I built DeployLens, a CI/CD risk analyzer for Kubernetes deployments. It scans manifests during pull requests, checks reliability and cost signals, generates a deployment risk score, and outputs a report that helps teams catch unsafe production changes before deployment.

That pitch shows application delivery, CI/CD, Kubernetes, reliability, security thinking, FinOps awareness, and automation.
