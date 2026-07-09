from pathlib import Path

from deploylens.scanner import scan_path


def test_scanner_finds_intentional_risks() -> None:
    report = scan_path(Path("manifests/dev"), environment="dev")
    rule_ids = {finding.rule_id for finding in report.findings}

    assert report.environment == "dev"
    assert "IMG_MUTABLE_TAG" in rule_ids
    assert "K8S_MISSING_LIMITS" in rule_ids
    assert "K8S_PUBLIC_LOADBALANCER" in rule_ids
    assert "SEC_RUN_AS_NON_ROOT" in rule_ids
    assert "SEC_PRIVILEGE_ESCALATION" in rule_ids
    assert "SEC_WRITABLE_ROOT_FILESYSTEM" in rule_ids
    assert report.risk_score >= 60


def test_cost_estimate_uses_requests() -> None:
    report = scan_path(Path("manifests/dev"), environment="dev")

    assert report.cost_estimate.monthly_total_usd > 0


def test_prod_manifest_is_low_risk() -> None:
    report = scan_path(Path("manifests/prod"), environment="prod")

    assert report.environment == "prod"
    assert report.risk_score < 30
    assert report.findings == []
