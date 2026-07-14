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
python -m deploylens scan manifests/dev --environment dev --policy .deploylens.yml
python -m deploylens scan manifests/prod --environment prod --policy .deploylens.yml
```

DeployLens:

1. Finds YAML files
2. Validates Kubernetes resource shape and wiring
3. Loads Kubernetes resources
4. Checks each resource against rules
5. Adds risk points for each issue
6. Estimates monthly cost from CPU and memory requests
7. Loads the selected environment's risk and cost gates from `.deploylens.yml`
8. Compares production cost against the configured budget
9. Generates Markdown and JSON reports
10. Exits with failure if validation fails, cost exceeds budget, or the score crosses the configured threshold

In CI, dev is scanned in report-only mode. Prod is scanned with a real gate so high-risk production manifests fail the pipeline.

On pull requests, the CI workflow also posts the dev and prod reports as a single bot comment. If the workflow runs again, it updates the existing comment instead of creating duplicates.

The policy file is committed with the application, so changes to deployment gates have a Git
history and can be reviewed like code. CLI flags can override the file for one-off local tests.

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
