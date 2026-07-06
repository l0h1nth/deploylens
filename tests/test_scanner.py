from pathlib import Path

from deploylens.scanner import scan_path


def test_scanner_finds_intentional_risks() -> None:
    report = scan_path(Path("manifests/base"))
    rule_ids = {finding.rule_id for finding in report.findings}

    assert "IMG_MUTABLE_TAG" in rule_ids
    assert "K8S_MISSING_LIMITS" in rule_ids
    assert "K8S_PUBLIC_LOADBALANCER" in rule_ids
    assert report.risk_score >= 60


def test_cost_estimate_uses_requests() -> None:
    report = scan_path(Path("manifests/base"))

    assert report.cost_estimate.monthly_total_usd > 0
