from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml


@dataclass(frozen=True)
class DeploymentPolicy:
    fail_threshold: int = 80
    max_monthly_cost: float | None = None
    source: str = "command defaults"

    def with_overrides(
        self,
        fail_threshold: int | None = None,
        max_monthly_cost: float | None = None,
    ) -> "DeploymentPolicy":
        return DeploymentPolicy(
            fail_threshold=(
                fail_threshold if fail_threshold is not None else self.fail_threshold
            ),
            max_monthly_cost=(
                max_monthly_cost
                if max_monthly_cost is not None
                else self.max_monthly_cost
            ),
            source=self.source,
        )


def load_policy(path: Path, environment: str) -> DeploymentPolicy:
    try:
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
    except FileNotFoundError as error:
        raise ValueError(f"policy file not found: {path}") from error
    except yaml.YAMLError as error:
        raise ValueError(f"invalid YAML in policy file {path}: {error}") from error

    if not isinstance(data, dict):
        raise ValueError("policy must be a YAML mapping")
    if data.get("version") != 1:
        raise ValueError("policy version must be 1")

    environments = data.get("environments")
    if not isinstance(environments, dict):
        raise ValueError("policy must define an environments mapping")

    settings = environments.get(environment)
    if not isinstance(settings, dict):
        raise ValueError(f"environment {environment!r} is not defined in {path}")

    fail_threshold = settings.get("fail_threshold", 80)
    _validate_fail_threshold(fail_threshold)

    max_monthly_cost = settings.get("max_monthly_cost")
    _validate_max_monthly_cost(max_monthly_cost)

    return DeploymentPolicy(
        fail_threshold=fail_threshold,
        max_monthly_cost=(
            float(max_monthly_cost) if max_monthly_cost is not None else None
        ),
        source=str(path),
    )


def _validate_fail_threshold(value: Any) -> None:
    if isinstance(value, bool) or not isinstance(value, int) or not 0 <= value <= 101:
        raise ValueError("fail_threshold must be an integer between 0 and 101")


def _validate_max_monthly_cost(value: Any) -> None:
    if value is None:
        return
    if isinstance(value, bool) or not isinstance(value, (int, float)) or value < 0:
        raise ValueError("max_monthly_cost must be a non-negative number")
