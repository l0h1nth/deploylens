# Rollback Runbook

Use this runbook when a deployment causes errors, failed health checks, or elevated latency.

## Kubernetes Rollback

```bash
kubectl -n deploylens rollout undo deployment/deploylens-sample
kubectl -n deploylens rollout status deployment/deploylens-sample
```

## Verify

```bash
kubectl -n deploylens get pods
kubectl -n deploylens port-forward svc/deploylens-sample 8080:80
curl http://127.0.0.1:8080/healthz
```

## After Rollback

- Open an incident or issue
- Attach the failed DeployLens report
- Explain what changed
- Add a test or rule so the same issue is caught earlier next time
