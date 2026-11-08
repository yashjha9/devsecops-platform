from datetime import datetime, timezone

from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user

from . import db
from .models import Project, Vulnerability, AuditLog

scanner_bp = Blueprint(
    "scanner",
    __name__,
    url_prefix="/api/projects"
)

VALID_SEVERITIES = {
    "CRITICAL", "HIGH", "MEDIUM", "LOW", "UNKNOWN"
}


def extract_cvss_v3(finding):
    sources = finding.get("CVSS") or {}

    # Prefer the NVD CVSS v3 score when available.
    nvd = sources.get("nvd") or {}

    if nvd.get("V3Score") is not None:
        return float(nvd["V3Score"])

    # Otherwise use the first available CVSS v3 score.
    for source in sources.values():
        if source.get("V3Score") is not None:
            return float(source["V3Score"])

    return None


def parse_trivy_report(report):
    if not isinstance(report, dict):
        raise ValueError("Report must be a JSON object")

    if not isinstance(report.get("Results"), list):
        raise ValueError("Invalid Trivy report: Results must be a list")

    parsed = []

    for result in report["Results"]:
        findings = result.get("Vulnerabilities") or []

        for finding in findings:
            vulnerability_id = finding.get("VulnerabilityID")

            if not vulnerability_id:
                continue

            severity = str(
                finding.get("Severity", "UNKNOWN")
            ).upper()

            if severity not in VALID_SEVERITIES:
                severity = "UNKNOWN"

            package_name = finding.get("PkgName", "unknown")
            installed_version = finding.get("InstalledVersion", "unknown")

            component = f"{package_name}@{installed_version}"

            description = finding.get("Description") or ""
            primary_url = finding.get("PrimaryURL")

            if primary_url:
                description = (
                    f"{description}\nReference: {primary_url}"
                ).strip()

            parsed.append({
                "external_id": vulnerability_id,
                "title": finding.get("Title") or vulnerability_id,
                "description": description,
                "severity": severity,
                "cvss_score": extract_cvss_v3(finding),
                "component": component
            })

    return parsed


def ingest_trivy_report(project, report):
    findings = parse_trivy_report(report)

    created = 0
    updated = 0
    now = datetime.now(timezone.utc)

    for finding in findings:
        existing = Vulnerability.query.filter_by(
            project_id=project.id,
            scanner="Trivy",
            external_id=finding["external_id"],
            component=finding["component"]
        ).first()

        if existing:
            existing.title = finding["title"]
            existing.description = finding["description"]
            existing.severity = finding["severity"]
            existing.cvss_score = finding["cvss_score"]
            existing.last_seen = now
            updated += 1

        else:
            item = Vulnerability(
                project_id=project.id,
                scanner="Trivy",
                external_id=finding["external_id"],
                title=finding["title"],
                description=finding["description"],
                severity=finding["severity"],
                cvss_score=finding["cvss_score"],
                component=finding["component"],
                first_seen=now,
                last_seen=now
            )

            db.session.add(item)
            created += 1

    db.session.flush()

    db.session.add(AuditLog(
        user_id=project.owner_id,
        action="scanner.trivy_report_ingested",
        entity_type="project",
        entity_id=project.id,
        details={
            "artifact": report.get("ArtifactName"),
            "created": created,
            "updated": updated,
            "total_processed": len(findings)
        }
    ))

    db.session.commit()

    return {
        "created": created,
        "updated": updated,
        "total_processed": len(findings),
        "artifact": report.get("ArtifactName")
    }


@scanner_bp.route(
    "/<int:project_id>/scan-reports/trivy",
    methods=["POST"]
)
@login_required
def upload_trivy_report(project_id):
    project = Project.query.filter_by(
        id=project_id,
        owner_id=current_user.id
    ).first()

    if not project:
        return jsonify({"error": "Project not found"}), 404

    report = request.get_json(silent=True)

    if not isinstance(report, dict):
        return jsonify({"error": "A valid Trivy JSON report is required"}), 400

    try:
        result = ingest_trivy_report(project, report)

    except ValueError as error:
        db.session.rollback()
        return jsonify({"error": str(error)}), 400

    except Exception:
        db.session.rollback()
        raise

    return jsonify({
        "message": "Trivy report processed successfully",
        "result": result
    }), 200
