import pytest

from securerelease import create_app, db
from securerelease.models import User, Project, Vulnerability, AuditLog
from securerelease.scanner_ingestion import ingest_trivy_report


@pytest.fixture
def app(tmp_path, monkeypatch):
    database_file = tmp_path / "scanner_test.db"
    monkeypatch.setenv("DATABASE_URL", f"sqlite:///{database_file.as_posix()}")

    test_app = create_app()
    test_app.config["TESTING"] = True

    with test_app.app_context():
        db.drop_all()
        db.create_all()
        yield test_app
        db.session.remove()
        db.drop_all()
        db.engine.dispose()


def test_trivy_reconciliation(app):
    with app.app_context():
        user = User(
            username="scanner_test",
            email="scanner_test@example.com",
            password_hash="test-hash"
        )
        db.session.add(user)
        db.session.flush()

        project = Project(
            name="Scanner Test Project",
            slug="scanner-test-project",
            owner_id=user.id
        )
        db.session.add(project)
        db.session.flush()

        missing_finding = Vulnerability(
            project_id=project.id,
            scanner="Trivy",
            external_id="CVE-TEST-001",
            title="Finding missing from new scan",
            severity="HIGH",
            status="open",
            component="package-a@1.0"
        )

        returning_finding = Vulnerability(
            project_id=project.id,
            scanner="Trivy",
            external_id="CVE-TEST-002",
            title="Finding returning in new scan",
            severity="MEDIUM",
            status="not_detected",
            component="package-b@2.0"
        )

        resolved_finding = Vulnerability(
            project_id=project.id,
            scanner="Trivy",
            external_id="CVE-TEST-003",
            title="Previously resolved finding",
            severity="LOW",
            status="resolved",
            component="package-c@3.0"
        )

        db.session.add_all([
            missing_finding,
            returning_finding,
            resolved_finding
        ])
        db.session.commit()

        report = {
            "SchemaVersion": 2,
            "ArtifactName": "scanner-reconciliation-test",
            "Results": [
                {
                    "Target": "test-image",
                    "Vulnerabilities": [
                        {
                            "VulnerabilityID": "CVE-TEST-002",
                            "Title": "Finding returning in new scan",
                            "Severity": "MEDIUM",
                            "PkgName": "package-b",
                            "InstalledVersion": "2.0"
                        },
                        {
                            "VulnerabilityID": "CVE-TEST-004",
                            "Title": "New finding",
                            "Severity": "LOW",
                            "PkgName": "package-d",
                            "InstalledVersion": "4.0"
                        }
                    ]
                }
            ]
        }

        result = ingest_trivy_report(project, report)

        assert result["created"] == 1
        assert result["updated"] == 1
        assert result["marked_not_detected"] == 1
        assert result["total_processed"] == 2

        assert db.session.get(
            Vulnerability, missing_finding.id
        ).status == "not_detected"

        assert db.session.get(
            Vulnerability, returning_finding.id
        ).status == "open"

        assert db.session.get(
            Vulnerability, resolved_finding.id
        ).status == "resolved"

        new_finding = Vulnerability.query.filter_by(
            project_id=project.id,
            external_id="CVE-TEST-004"
        ).one()
        assert new_finding.status == "open"

        audit = AuditLog.query.filter_by(
            action="scanner.trivy_report_ingested",
            entity_id=project.id
        ).one()
        assert audit.details["total_processed"] == 2
