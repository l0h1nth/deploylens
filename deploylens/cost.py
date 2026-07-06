from typing import Any

from deploylens.models import CostEstimate

HOURS_PER_MONTH = 730
CPU_MONTHLY_USD = 29.20
MEMORY_GIB_MONTHLY_USD = 3.65


def parse_cpu(value: object) -> float:
    text = str(value)
    if text.endswith("m"):
        return float(text.removesuffix("m")) / 1000
    return float(text)


def parse_memory_gib(value: object) -> float:
    text = str(value)
    units = {
        "Ki": 1 / 1024 / 1024,
        "Mi": 1 / 1024,
        "Gi": 1,
        "Ti": 1024,
        "K": 1 / 1000 / 1000,
        "M": 1 / 1000,
        "G": 1,
    }
    for suffix, multiplier in units.items():
        if text.endswith(suffix):
            return float(text.removesuffix(suffix)) * multiplier
    return float(text) / 1024 / 1024 / 1024


def estimate_resource_cost(resources: list[dict[str, Any]]) -> CostEstimate:
    cpu_total = 0.0
    memory_total = 0.0

    for resource in resources:
        if resource.get("kind") != "Deployment":
            continue

        spec = resource.get("spec") or {}
        replicas = int(spec.get("replicas", 1))
        template = spec.get("template") or {}
        pod_spec = template.get("spec") or {}
        containers = pod_spec.get("containers") or []

        for container in containers:
            requests = ((container.get("resources") or {}).get("requests") or {})
            if "cpu" in requests:
                cpu_total += parse_cpu(requests["cpu"]) * replicas
            if "memory" in requests:
                memory_total += parse_memory_gib(requests["memory"]) * replicas

    return CostEstimate(
        monthly_cpu_usd=round(cpu_total * CPU_MONTHLY_USD, 2),
        monthly_memory_usd=round(memory_total * MEMORY_GIB_MONTHLY_USD, 2),
    )
