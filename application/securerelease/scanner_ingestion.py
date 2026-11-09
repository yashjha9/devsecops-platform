import hashlib

from datetime import datetime, timezone

from flask import Blueprint, request, jsonify
from flask_login import current_user

from . import db
from .models import (
    Project,
    Vulnerability,
    AuditLog,
    ProjectAPIToken,
    User
)

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

    if report.get("SchemaVersion") != 2:
        raise ValueError("Unsupported or missing Trivy schema version")

    artifact = report.get("ArtifactName")

    if not isinstance(artifact, str) or not artifact.strip():
        raise ValueError("Trivy artifact name is required")

    results = report.get("Results")

    if not isinstance(results, list) or not results:
        raise ValueError("Trivy report must contain at least one result")

    parsed = []

    for result in results:
        if not isinstance(result, dict):
            raise ValueError("Invalid Trivy result entry")

        if not isinstance(result.get("Target"), str) or not result["Target"].strip():
            raise ValueError("Trivy result target is missing")

        vulnerabilities = result.get("Vulnerabilities")

        # Trivy can use null when a target has no vulnerabilities.
        if vulnerabilities is None:
            continue

        if not isinstance(vulnerabilities, list):
            raise ValueError("Invalid Trivy vulnerabilities collection")

        for finding in vulnerabilities:
            if not isinstance(finding, dict):
                raise ValueError("Invalid vulnerability entry")

            vulnerability_id = finding.get("VulnerabilityID")

            if not isinstance(vulnerability_id, str) or not vulnerability_id.strip():
                raise ValueError("Vulnerability ID is missing")

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
    marked_not_detected = 0
    now = datetime.now(timezone.utc)

    # Track findings present in this scan.
    detected_keys = set()

    for finding in findings:
        key = (
            finding["external_id"],
            finding["component"]
        )
        detected_keys.add(key)

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

            if existing.status == "not_detected":
                existing.status = "open"

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

    # Mark previously detected findings absent from this scan.
    previous_findings = Vulnerability.query.filter_by(
        project_id=project.id,
        scanner="Trivy"
    ).all()

    for item in previous_findings:
        key = (item.external_id, item.component)

        if (
            key not in detected_keys
            and item.status not in {"resolved", "accepted", "not_detected"}
        ):
            item.status = "not_detected"
            marked_not_detected += 1

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
            "marked_not_detected": marked_not_detected,
            "total_processed": len(findings)
        }
    ))

    db.session.commit()

    return {
        "created": created,
        "updated": updated,
        "marked_not_detected": marked_not_detected,
        "total_processed": len(findings),
        "artifact": report.get("ArtifactName")
    }

@scanner_bp.route(
    "/<int:project_id>/scan-reports/trivy",
    methods=["POST"]
)
def upload_trivy_report(project_id):
    auth_header = request.headers.get("Authorization", "")
    token = None
    authenticated_user = None

    if auth_header.startswith("Bearer "):
        raw_token = auth_header[len("Bearer "):].strip()

        if not raw_token:
            return jsonify({"error": "Invalid API token"}), 401

        token_hash = hashlib.sha256(
            raw_token.encode("utf-8")
        ).hexdigest()

        api_token = ProjectAPIToken.query.filter_by(
            token_hash=token_hash,
            project_id=project_id,
            revoked_at=None
        ).first()

        if not api_token:
            return jsonify({"error": "Invalid API token"}), 401

        authenticated_user = db.session.get(
            User,
            api_token.user_id
        )

        if not authenticated_user or not authenticated_user.is_active:
            return jsonify({"error": "Invalid API token"}), 401

        token = api_token

    elif current_user.is_authenticated:
        authenticated_user = current_user

    else:
        return jsonify({"error": "Authentication required"}), 401

    project = Project.query.filter_by(
        id=project_id,
        owner_id=authenticated_user.id
    ).first()

    if not project:
        return jsonify({"error": "Project not found"}), 404

    report = request.get_json(silent=True)

    if not isinstance(report, dict):
        return jsonify({"error": "A valid Trivy JSON report is required"}), 400

    try:
        result = ingest_trivy_report(project, report)

        if token:
            db.session.add(AuditLog(
                user_id=authenticated_user.id,
                action="api_token.used",
                entity_type="project",
                entity_id=project.id,
                details={
                    "token_name": token.name,
                    "scanner": "trivy"
                }
            ))
            db.session.commit()

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
