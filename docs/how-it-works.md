# How DeployLens Works

DeployLens has three moving parts.

## 1. Sample App

The `sample-app/` folder contains a tiny HTTP service.

This app is not the main star. It exists so we have something real to containerize, deploy, scan, and improve.

## 2. Kubernetes Manifests

The `manifests/` folder describes how the sample app should run in Kubernetes.

`manifests/dev/` intentionally includes some risky choices:

- one replica
- `latest` image tag
- no hardened container security context
- no CPU or memory limits
- no liveness/readiness probes
- public `LoadBalancer` service

That gives DeployLens real problems to detect while you are learning.

`manifests/prod/` shows the safer production version:

- two replicas
- pinned image tag
- container security context
- CPU and memory requests and limits
- liveness and readiness probes
- internal `ClusterIP` service

## 3. Analyzer CLI

The `deploylens/` package is our custom Python CLI.

When you run:

```bash
python -m deploylens validate manifests/dev
python -m deploylens validate manifests/prod
python -m deploylens scan manifests/dev --environment dev
python -m deploylens scan manifests/prod --environment prod --max-monthly-cost 25
```

DeployLens:

1. Finds YAML files
2. Validates Kubernetes resource shape and wiring
3. Loads Kubernetes resources
4. Checks each resource against rules
5. Adds risk points for each issue
6. Estimates monthly cost from CPU and memory requests
7. Compares production cost against the configured budget
8. Generates Markdown and JSON reports
9. Exits with failure if validation fails, cost exceeds budget, or the score crosses the configured threshold

In CI, dev is scanned in report-only mode. Prod is scanned with a real gate so high-risk production manifests fail the pipeline.

On pull requests, the CI workflow also posts the dev and prod reports as a single bot comment. If the workflow runs again, it updates the existing comment instead of creating duplicates.

## Why This Is DevOps

This project teaches the real DevOps workflow:

- Developers change app and deployment code
- CI runs automatically
- Deployment manifests are inspected before production
- Risk is explained clearly
- Reports are stored as CI artifacts
- Later, the same pipeline can deploy to Kubernetes

The important mindset is:

> DevOps is not only deploying. DevOps is making deployment safer, repeatable, observable, and recoverable.
