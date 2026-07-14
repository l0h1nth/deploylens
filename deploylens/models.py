from dataclasses import dataclass, field

from deploylens.policy import DeploymentPolicy


@dataclass(frozen=True)
class Finding:
    rule_id: str
    severity: str
    title: str
    message: str
    resource: str
    file: str
    points: int

    def to_dict(self) -> dict[str, object]:
        return {
            "rule_id": self.rule_id,
            "severity": self.severity,
            "title": self.title,
            "message": self.message,
            "resource": self.resource,
            "file": self.file,
            "points": self.points,
        }


@dataclass(frozen=True)
class CostEstimate:
    monthly_cpu_usd: float = 0.0
    monthly_memory_usd: float = 0.0

    @property
    def monthly_total_usd(self) -> float:
        return round(self.monthly_cpu_usd + self.monthly_memory_usd, 2)

    def to_dict(self) -> dict[str, float]:
        return {
            "monthly_cpu_usd": round(self.monthly_cpu_usd, 2),
            "monthly_memory_usd": round(self.monthly_memory_usd, 2),
            "monthly_total_usd": self.monthly_total_usd,
        }


@dataclass(frozen=True)
class ScanReport:
    environment: str
    scanned_files: list[str]
    findings: list[Finding] = field(default_factory=list)
    cost_estimate: CostEstimate = field(default_factory=CostEstimate)
    policy: DeploymentPolicy | None = None

    @property
    def risk_score(self) -> int:
        return min(sum(finding.points for finding in self.findings), 100)

    @property
    def risk_level(self) -> str:
        if self.risk_score >= 80:
            return "critical"
        if self.risk_score >= 60:
            return "high"
        if self.risk_score >= 30:
            return "medium"
        return "low"

    def to_dict(self) -> dict[str, object]:
        data: dict[str, object] = {
            "environment": self.environment,
            "risk_score": self.risk_score,
            "risk_level": self.risk_level,
            "scanned_files": self.scanned_files,
            "cost_estimate": self.cost_estimate.to_dict(),
            "findings": [finding.to_dict() for finding in self.findings],
        }
        if self.policy is not None:
            data["policy"] = {
                "source": self.policy.source,
                "fail_threshold": self.policy.fail_threshold,
                "max_monthly_cost": self.policy.max_monthly_cost,
            }
        return data
