from pathlib import Path
from typing import Any

import yaml

from deploylens.models import Finding
from deploylens.parser import resource_name

DEFAULT_RULES_PATH = Path("rules/deploylens-rules.yml")


def load_rule_points(path: Path = DEFAULT_RULES_PATH) -> dict[str, int]:
    if not path.exists():
        return {}

    data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    rules = data.get("rules", {})
    return {
        rule_id: int(rule_config.get("points", 0))
        for rule_id, rule_config in rules.items()
        if isinstance(rule_config, dict)
    }


def points(rule_points: dict[str, int], rule_id: str, fallback: int) -> int:
    return rule_points.get(rule_id, fallback)


def check_deployment(
    resource: dict[str, Any],
    file: Path,
    rule_points: dict[str, int],
) -> list[Finding]:
    findings: list[Finding] = []
    name = resource_name(resource)
    spec = resource.get("spec") or {}
    template = spec.get("template") or {}
    pod_spec = template.get("spec") or {}
    containers = pod_spec.get("containers") or []
    replicas = spec.get("replicas", 1)

    if replicas < 2:
        findings.append(
            Finding(
                rule_id="K8S_REPLICA_SINGLE",
                severity="medium",
                title="Deployment has fewer than two replicas",
                message="Production workloads usually need at least two replicas for availability.",
                resource=name,
                file=str(file),
                points=points(rule_points, "K8S_REPLICA_SINGLE", 12),
            )
        )

    for container in containers:
        container_name = container.get("name", "unnamed")
        image = str(container.get("image", ""))
        resources = container.get("resources") or {}
        requests = resources.get("requests") or {}
        limits = resources.get("limits") or {}
        security_context = container.get("securityContext") or {}

        if image.endswith(":latest") or ":" not in image:
            findings.append(
                Finding(
                    rule_id="IMG_MUTABLE_TAG",
                    severity="high",
                    title="Container image tag is mutable",
                    message=f"Container '{container_name}' uses '{image}'. Pin images to immutable versions.",
                    resource=name,
                    file=str(file),
                    points=points(rule_points, "IMG_MUTABLE_TAG", 22),
                )
            )

        if "cpu" not in requests or "memory" not in requests:
            findings.append(
                Finding(
                    rule_id="K8S_MISSING_REQUESTS",
                    severity="high",
                    title="Container is missing CPU or memory requests",
                    message=f"Container '{container_name}' needs requests for scheduling and cost visibility.",
                    resource=name,
                    file=str(file),
                    points=points(rule_points, "K8S_MISSING_REQUESTS", 18),
                )
            )

        if "cpu" not in limits or "memory" not in limits:
            findings.append(
                Finding(
                    rule_id="K8S_MISSING_LIMITS",
                    severity="high",
                    title="Container is missing CPU or memory limits",
                    message=f"Container '{container_name}' needs limits to reduce noisy-neighbor risk.",
                    resource=name,
                    file=str(file),
                    points=points(rule_points, "K8S_MISSING_LIMITS", 18),
                )
            )

        if "readinessProbe" not in container:
            findings.append(
                Finding(
                    rule_id="K8S_MISSING_READINESS",
                    severity="medium",
                    title="Container has no readiness probe",
                    message=f"Container '{container_name}' may receive traffic before it is ready.",
                    resource=name,
                    file=str(file),
                    points=points(rule_points, "K8S_MISSING_READINESS", 12),
                )
            )

        if "livenessProbe" not in container:
            findings.append(
                Finding(
                    rule_id="K8S_MISSING_LIVENESS",
                    severity="medium",
                    title="Container has no liveness probe",
                    message=f"Container '{container_name}' may not be restarted automatically when unhealthy.",
                    resource=name,
                    file=str(file),
                    points=points(rule_points, "K8S_MISSING_LIVENESS", 10),
                )
            )

        if security_context.get("runAsNonRoot") is not True:
            findings.append(
                Finding(
                    rule_id="SEC_RUN_AS_NON_ROOT",
                    severity="high",
                    title="Container is not required to run as non-root",
                    message=f"Container '{container_name}' should set securityContext.runAsNonRoot: true.",
                    resource=name,
                    file=str(file),
                    points=points(rule_points, "SEC_RUN_AS_NON_ROOT", 16),
                )
            )

        if security_context.get("allowPrivilegeEscalation") is not False:
            findings.append(
                Finding(
                    rule_id="SEC_PRIVILEGE_ESCALATION",
                    severity="high",
                    title="Container can allow privilege escalation",
                    message=(
                        f"Container '{container_name}' should set "
                        "securityContext.allowPrivilegeEscalation: false."
                    ),
                    resource=name,
                    file=str(file),
                    points=points(rule_points, "SEC_PRIVILEGE_ESCALATION", 16),
                )
            )

        if security_context.get("readOnlyRootFilesystem") is not True:
            findings.append(
                Finding(
                    rule_id="SEC_WRITABLE_ROOT_FILESYSTEM",
                    severity="medium",
                    title="Container root filesystem is writable",
                    message=(
                        f"Container '{container_name}' should set "
                        "securityContext.readOnlyRootFilesystem: true when possible."
                    ),
                    resource=name,
                    file=str(file),
                    points=points(rule_points, "SEC_WRITABLE_ROOT_FILESYSTEM", 8),
                )
            )

    return findings


def check_service(
    resource: dict[str, Any],
    file: Path,
    rule_points: dict[str, int],
) -> list[Finding]:
    spec = resource.get("spec") or {}
    if spec.get("type") != "LoadBalancer":
        return []

    return [
        Finding(
            rule_id="K8S_PUBLIC_LOADBALANCER",
            severity="medium",
            title="Service creates a public LoadBalancer",
            message="Public load balancers can increase cost and exposure. Confirm this is intentional.",
            resource=resource_name(resource),
            file=str(file),
            points=points(rule_points, "K8S_PUBLIC_LOADBALANCER", 14),
        )
    ]


def check_rollback_docs(root: Path, rule_points: dict[str, int]) -> list[Finding]:
    candidates = [
        root / "ROLLBACK.md",
        root / "docs" / "rollback.md",
        root / "docs" / "runbook.md",
    ]
    if any(candidate.exists() for candidate in candidates):
        return []

    return [
        Finding(
            rule_id="OPS_MISSING_ROLLBACK_DOC",
            severity="medium",
            title="Rollback documentation is missing",
            message="Production changes should explain how to recover if deployment fails.",
            resource="repository",
            file=str(root),
            points=points(rule_points, "OPS_MISSING_ROLLBACK_DOC", 10),
        )
    ]
