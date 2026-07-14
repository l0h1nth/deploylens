from pathlib import Path

import pytest

from deploylens.policy import load_policy


def test_loads_environment_policy() -> None:
    policy = load_policy(Path(".deploylens.yml"), "prod")

    assert policy.fail_threshold == 80
    assert policy.max_monthly_cost == 25.0


def test_rejects_unknown_environment() -> None:
    with pytest.raises(ValueError, match="environment 'staging' is not defined"):
        load_policy(Path(".deploylens.yml"), "staging")


def test_rejects_invalid_threshold(tmp_path) -> None:
    policy_file = tmp_path / "policy.yml"
    policy_file.write_text(
        "version: 1\nenvironments:\n  prod:\n    fail_threshold: 200\n",
        encoding="utf-8",
    )

    with pytest.raises(ValueError, match="fail_threshold"):
        load_policy(policy_file, "prod")
