from pathlib import Path
from typing import Any

import yaml


def discover_yaml_files(path: Path) -> list[Path]:
    if path.is_file():
        return [path]

    patterns = ("*.yaml", "*.yml")
    files: list[Path] = []
    for pattern in patterns:
        files.extend(path.rglob(pattern))
    return sorted(files)


def load_yaml_documents(path: Path) -> list[dict[str, Any]]:
    documents: list[dict[str, Any]] = []
    with path.open(encoding="utf-8") as stream:
        for document in yaml.safe_load_all(stream):
            if isinstance(document, dict):
                documents.append(document)
    return documents


def resource_name(resource: dict[str, Any]) -> str:
    kind = resource.get("kind", "Unknown")
    metadata = resource.get("metadata") or {}
    name = metadata.get("name", "unnamed")
    return f"{kind}/{name}"
