from pathlib import Path
from typing import Any

from deploylens.cost import estimate_resource_cost
from deploylens.models import Finding, ScanReport
from deploylens.parser import discover_yaml_files, load_yaml_documents
from deploylens.rules import check_deployment, check_rollback_docs, check_service, load_rule_points


def scan_path(path: Path) -> ScanReport:
    yaml_files = discover_yaml_files(path)
    rule_points = load_rule_points()
    findings: list[Finding] = []
    resources: list[dict[str, Any]] = []

    for yaml_file in yaml_files:
        for resource in load_yaml_documents(yaml_file):
            resources.append(resource)
            kind = resource.get("kind")
            if kind == "Deployment":
                findings.extend(check_deployment(resource, yaml_file, rule_points))
            elif kind == "Service":
                findings.extend(check_service(resource, yaml_file, rule_points))

    repo_root = Path.cwd()
    findings.extend(check_rollback_docs(repo_root, rule_points))

    return ScanReport(
        scanned_files=[str(file) for file in yaml_files],
        findings=findings,
        cost_estimate=estimate_resource_cost(resources),
    )
