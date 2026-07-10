from pathlib import Path

from deploylens.validator import validate_path


def test_validates_current_manifests() -> None:
    assert validate_path(Path("manifests/dev")).passed
    assert validate_path(Path("manifests/prod")).passed


def test_detects_deployment_selector_mismatch(tmp_path: Path) -> None:
    manifest = tmp_path / "deployment.yaml"
    manifest.write_text(
        """
apiVersion: apps/v1
kind: Deployment
metadata:
  name: broken
spec:
  selector:
    matchLabels:
      app: api
  template:
    metadata:
      labels:
        app: worker
    spec:
      containers:
        - name: web
          image: example:v1
""",
        encoding="utf-8",
    )

    report = validate_path(tmp_path)
    codes = {issue.code for issue in report.issues}

    assert not report.passed
    assert "K8S_DEPLOYMENT_SELECTOR_MISMATCH" in codes


def test_detects_service_selector_without_matching_deployment(tmp_path: Path) -> None:
    manifest = tmp_path / "service.yaml"
    manifest.write_text(
        """
apiVersion: v1
kind: Service
metadata:
  name: broken
spec:
  selector:
    app: missing
  ports:
    - name: http
      port: 80
      targetPort: http
""",
        encoding="utf-8",
    )

    report = validate_path(tmp_path)
    codes = {issue.code for issue in report.issues}

    assert not report.passed
    assert "K8S_SERVICE_SELECTOR_NO_MATCH" in codes
