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
