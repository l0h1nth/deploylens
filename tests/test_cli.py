import pytest

from deploylens.cli import main


def test_scan_fails_when_monthly_cost_exceeds_budget(tmp_path, monkeypatch) -> None:
    monkeypatch.setattr(
        "sys.argv",
        [
            "deploylens",
            "scan",
            "manifests/prod",
            "--output",
            str(tmp_path / "report.md"),
            "--json-output",
            str(tmp_path / "report.json"),
            "--fail-threshold",
            "101",
            "--max-monthly-cost",
            "1",
        ],
    )

    with pytest.raises(SystemExit) as error:
        main()

    assert error.value.code == 2


def test_scan_passes_when_monthly_cost_is_within_budget(tmp_path, monkeypatch) -> None:
    monkeypatch.setattr(
        "sys.argv",
        [
            "deploylens",
            "scan",
            "manifests/prod",
            "--output",
            str(tmp_path / "report.md"),
            "--json-output",
            str(tmp_path / "report.json"),
            "--fail-threshold",
            "101",
            "--max-monthly-cost",
            "999",
        ],
    )

    main()


def test_scan_uses_environment_policy(tmp_path, monkeypatch) -> None:
    policy_file = tmp_path / "policy.yml"
    policy_file.write_text(
        "version: 1\nenvironments:\n  prod:\n    max_monthly_cost: 1\n",
        encoding="utf-8",
    )
    monkeypatch.setattr(
        "sys.argv",
        [
            "deploylens",
            "scan",
            "manifests/prod",
            "--environment",
            "prod",
            "--policy",
            str(policy_file),
            "--output",
            str(tmp_path / "report.md"),
            "--json-output",
            str(tmp_path / "report.json"),
        ],
    )

    with pytest.raises(SystemExit) as error:
        main()

    assert error.value.code == 2
