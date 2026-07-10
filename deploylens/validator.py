from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml

from deploylens.parser import discover_yaml_files, resource_name


@dataclass(frozen=True)
class ValidationIssue:
    code: str
    message: str
    file: str
    resource: str = "unknown"

    def to_dict(self) -> dict[str, str]:
        return {
            "code": self.code,
            "message": self.message,
            "file": self.file,
            "resource": self.resource,
        }


@dataclass(frozen=True)
class ValidationReport:
    scanned_files: list[str]
    issues: list[ValidationIssue] = field(default_factory=list)

    @property
    def passed(self) -> bool:
        return len(self.issues) == 0

    def to_dict(self) -> dict[str, object]:
        return {
            "passed": self.passed,
            "scanned_files": self.scanned_files,
            "issues": [issue.to_dict() for issue in self.issues],
        }


def validate_path(path: Path) -> ValidationReport:
    yaml_files = discover_yaml_files(path)
    issues: list[ValidationIssue] = []
    resources: list[tuple[Path, dict[str, Any]]] = []

    for yaml_file in yaml_files:
        try:
            documents = list(yaml.safe_load_all(yaml_file.read_text(encoding="utf-8")))
        except yaml.YAMLError as error:
            issues.append(
                ValidationIssue(
                    code="YAML_PARSE_ERROR",
                    message=f"YAML could not be parsed: {error}",
                    file=str(yaml_file),
                )
            )
            continue

        for document in documents:
            if document is None:
                continue
            if not isinstance(document, dict):
                issues.append(
                    ValidationIssue(
                        code="YAML_DOCUMENT_NOT_OBJECT",
                        message="Kubernetes YAML documents must be objects.",
                        file=str(yaml_file),
                    )
                )
                continue

            resources.append((yaml_file, document))
            issues.extend(validate_required_fields(yaml_file, document))

    issues.extend(validate_deployment_selectors(resources))
    issues.extend(validate_service_targets(resources))

    return ValidationReport(scanned_files=[str(file) for file in yaml_files], issues=issues)


def validate_required_fields(file: Path, resource: dict[str, Any]) -> list[ValidationIssue]:
    issues: list[ValidationIssue] = []
    kind = resource.get("kind")

    if not resource.get("apiVersion"):
        issues.append(
            ValidationIssue(
                code="K8S_MISSING_API_VERSION",
                message="Resource is missing apiVersion.",
                file=str(file),
                resource=resource_name(resource),
            )
        )

    if not kind:
        issues.append(
            ValidationIssue(
                code="K8S_MISSING_KIND",
                message="Resource is missing kind.",
                file=str(file),
                resource=resource_name(resource),
            )
        )

    if kind != "Kustomization":
        metadata = resource.get("metadata") or {}
        if not metadata.get("name"):
            issues.append(
                ValidationIssue(
                    code="K8S_MISSING_METADATA_NAME",
                    message="Resource is missing metadata.name.",
                    file=str(file),
                    resource=resource_name(resource),
                )
            )

    return issues


def validate_deployment_selectors(
    resources: list[tuple[Path, dict[str, Any]]],
) -> list[ValidationIssue]:
    issues: list[ValidationIssue] = []

    for file, resource in resources:
        if resource.get("kind") != "Deployment":
            continue

        spec = resource.get("spec") or {}
        selector = ((spec.get("selector") or {}).get("matchLabels") or {})
        template = spec.get("template") or {}
        template_labels = ((template.get("metadata") or {}).get("labels") or {})

        if not selector:
            issues.append(
                ValidationIssue(
                    code="K8S_DEPLOYMENT_SELECTOR_MISSING",
                    message="Deployment selector.matchLabels is required.",
                    file=str(file),
                    resource=resource_name(resource),
                )
            )
            continue

        if not labels_match(selector, template_labels):
            issues.append(
                ValidationIssue(
                    code="K8S_DEPLOYMENT_SELECTOR_MISMATCH",
                    message="Deployment selector labels must match pod template labels.",
                    file=str(file),
                    resource=resource_name(resource),
                )
            )

    return issues


def validate_service_targets(
    resources: list[tuple[Path, dict[str, Any]]],
) -> list[ValidationIssue]:
    issues: list[ValidationIssue] = []
    deployments = [resource for _, resource in resources if resource.get("kind") == "Deployment"]

    for file, resource in resources:
        if resource.get("kind") != "Service":
            continue

        spec = resource.get("spec") or {}
        selector = spec.get("selector") or {}
        ports = spec.get("ports") or []

        if not selector:
            issues.append(
                ValidationIssue(
                    code="K8S_SERVICE_SELECTOR_MISSING",
                    message="Service selector is required.",
                    file=str(file),
                    resource=resource_name(resource),
                )
            )
            continue

        matching_deployments = [
            deployment
            for deployment in deployments
            if labels_match(selector, deployment_template_labels(deployment))
        ]
        if not matching_deployments:
            issues.append(
                ValidationIssue(
                    code="K8S_SERVICE_SELECTOR_NO_MATCH",
                    message="Service selector does not match any Deployment pod template labels.",
                    file=str(file),
                    resource=resource_name(resource),
                )
            )
            continue

        named_ports = {
            port.get("name")
            for deployment in matching_deployments
            for container in deployment_containers(deployment)
            for port in container.get("ports", [])
            if port.get("name")
        }

        for port in ports:
            target_port = port.get("targetPort")
            if isinstance(target_port, str) and target_port not in named_ports:
                issues.append(
                    ValidationIssue(
                        code="K8S_SERVICE_TARGET_PORT_MISSING",
                        message=f"Service targetPort '{target_port}' does not match a named container port.",
                        file=str(file),
                        resource=resource_name(resource),
                    )
                )

    return issues


def labels_match(selector: dict[str, str], labels: dict[str, str]) -> bool:
    return all(labels.get(key) == value for key, value in selector.items())


def deployment_template_labels(deployment: dict[str, Any]) -> dict[str, str]:
    spec = deployment.get("spec") or {}
    template = spec.get("template") or {}
    metadata = template.get("metadata") or {}
    return metadata.get("labels") or {}


def deployment_containers(deployment: dict[str, Any]) -> list[dict[str, Any]]:
    spec = deployment.get("spec") or {}
    template = spec.get("template") or {}
    pod_spec = template.get("spec") or {}
    return pod_spec.get("containers") or []
