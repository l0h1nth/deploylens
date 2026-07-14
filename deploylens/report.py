from collections import Counter

from deploylens.models import Finding, ScanReport


def render_finding(finding: Finding) -> str:
    return "\n".join(
        [
            f"### {finding.title}",
            "",
            f"- Rule: `{finding.rule_id}`",
            f"- Severity: `{finding.severity}`",
            f"- Resource: `{finding.resource}`",
            f"- File: `{finding.file}`",
            f"- Risk points: `{finding.points}`",
            f"- Why it matters: {finding.message}",
        ]
    )


def render_markdown(report: ScanReport) -> str:
    severity_counts = Counter(finding.severity for finding in report.findings)
    findings = "\n\n".join(render_finding(finding) for finding in report.findings)
    if not findings:
        findings = "No findings. This deployment looks clean for the current rule set."

    policy_lines: list[str] = []
    if report.policy is not None:
        cost_budget = (
            f"${report.policy.max_monthly_cost:.2f}"
            if report.policy.max_monthly_cost is not None
            else "not enforced"
        )
        policy_lines = [
            "## Applied Policy",
            "",
            f"- Source: `{report.policy.source}`",
            f"- Risk failure threshold: {report.policy.fail_threshold}",
            f"- Monthly cost budget: {cost_budget}",
            "",
        ]

    return "\n".join(
        [
            "# DeployLens Risk Report",
            "",
            f"**Environment:** {report.environment}",
            f"**Risk score:** {report.risk_score}/100",
            f"**Risk level:** {report.risk_level}",
            f"**Estimated monthly resource cost:** ${report.cost_estimate.monthly_total_usd}",
            "",
            "## Summary",
            "",
            f"- Files scanned: {len(report.scanned_files)}",
            f"- Findings: {len(report.findings)}",
            f"- Critical: {severity_counts.get('critical', 0)}",
            f"- High: {severity_counts.get('high', 0)}",
            f"- Medium: {severity_counts.get('medium', 0)}",
            f"- Low: {severity_counts.get('low', 0)}",
            "",
            "## Cost Estimate",
            "",
            f"- CPU requests/month: ${report.cost_estimate.monthly_cpu_usd:.2f}",
            f"- Memory requests/month: ${report.cost_estimate.monthly_memory_usd:.2f}",
            f"- Total/month: ${report.cost_estimate.monthly_total_usd:.2f}",
            "",
            *policy_lines,
            "## Findings",
            "",
            findings,
            "",
            "## Recommendation",
            "",
            recommendation(report.risk_score),
            "",
        ]
    )


def recommendation(score: int) -> str:
    if score >= 80:
        return "Block production deployment until the critical risks are fixed."
    if score >= 60:
        return "Require DevOps review before production deployment."
    if score >= 30:
        return "Deployment can continue after the medium-risk items are acknowledged."
    return "Deployment is low risk for the current rule set."
