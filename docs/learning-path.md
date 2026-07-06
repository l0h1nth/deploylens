# Learning Path

Use this project to learn DevOps in this order.

## Phase 1: Git, GitHub, And The Project Story

Learn:

- What a repository is
- What commits are
- How GitHub Actions starts from a push or pull request

Build:

- Push DeployLens to GitHub
- Read the first CI run
- Download the generated risk report artifact

## Phase 2: Python Automation

Learn:

- How CLIs work
- How YAML parsing works
- How automation tools produce reports

Build:

- Add one new DeployLens rule
- Add a test for that rule

## Phase 3: Docker

Learn:

- Images and containers
- Dockerfile layers
- Non-root users
- Ports

Build:

- Build the sample app image
- Run it locally
- Add image scanning later

## Phase 4: Kubernetes

Learn:

- Namespace
- Deployment
- Service
- Replicas
- Probes
- Requests and limits

Build:

- Fix the risky manifests one by one
- Watch DeployLens score go down

## Phase 5: CI/CD

Learn:

- Workflow triggers
- Jobs and steps
- Artifacts
- Failing a pipeline intentionally

Build:

- Make DeployLens block unsafe pull requests
- Publish reports on every PR

## Phase 6: Security And FinOps

Learn:

- SBOM
- Vulnerability scanning
- Resource cost estimation
- Cloud cost ownership

Build:

- Add dependency scan
- Add image scan
- Improve cost model
