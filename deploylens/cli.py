import argparse
import json
from pathlib import Path

from deploylens.report import render_markdown
from deploylens.scanner import scan_path


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="deploylens",
        description="Scan Kubernetes manifests and generate a deployment risk report.",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    scan = subparsers.add_parser("scan", help="Scan Kubernetes YAML manifests.")
    scan.add_argument("path", type=Path, help="File or directory containing Kubernetes YAML.")
    scan.add_argument(
        "--output",
        type=Path,
        default=Path("reports/deploylens-report.md"),
        help="Markdown report path.",
    )
    scan.add_argument(
        "--json-output",
        type=Path,
        default=Path("reports/deploylens-report.json"),
        help="JSON report path.",
    )
    scan.add_argument(
        "--fail-threshold",
        type=int,
        default=80,
        help="Exit with code 2 when risk score is greater than or equal to this value.",
    )
    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    if args.command == "scan":
        report = scan_path(args.path)
        markdown = render_markdown(report)

        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.json_output.parent.mkdir(parents=True, exist_ok=True)

        args.output.write_text(markdown, encoding="utf-8")
        args.json_output.write_text(json.dumps(report.to_dict(), indent=2), encoding="utf-8")

        print(markdown)

        if report.risk_score >= args.fail_threshold:
            raise SystemExit(2)
