# DevSecOps Implementation Journal

## Project Information

**Project Title:** Design and Implementation of a Production-Ready Cloud-Native DevSecOps Platform on AWS using Terraform, Kubernetes, and GitHub Actions

**Purpose:** To document implementation activities, verification results, security assessments, and experimental progress.

**Project Status:** In Progress

---

## Milestone 1: Environment and Repository Setup

**Date:** 31 October 2026

**Status:** Completed

### Implementation

- Installed and verified Git.
- Installed and configured Visual Studio Code.
- Installed and verified AWS CLI.
- Installed and verified Terraform.
- Installed Docker Desktop.
- Verified Docker installation using the hello-world image.
- Verified WSL 2.
- Installed and verified kubectl.
- Created the `devsecops-platform` project directory.
- Created the initial directory structure.
- Initialized the Git repository.
- Created README.md and .gitignore.
- Created the GitHub repository.
- Pushed the initial project commit.

### Result

The local development environment and Git repository were prepared successfully.

---

## Milestone 2: Sample Flask Application

**Date:** 31 October 2026

**Status:** Completed

### Objective

Develop a lightweight Python Flask application with home, health-check, and version endpoints.

### Implementation

Created the Flask application with the following endpoints:

| Endpoint | Purpose |
|---|---|
| `/` | Returns application information |
| `/health` | Returns application health status |
| `/version` | Returns application version |

Application version:

`1.0.0`

### Verification

The three application endpoints were tested successfully.

### Result

The sample application was developed and verified before containerization.

---

## Milestone 3: Docker Containerization

**Date:** 31 October 2026

**Status:** Completed

### Implementation

- Created a Dockerfile.
- Configured the Python runtime.
- Installed application dependencies.
- Created a dedicated non-root Linux user named `appuser`.
- Configured the application to listen on port 5000.
- Built the initial Docker image `devsecops-app:v1`.
- Built the updated Docker image `devsecops-app:v2`.

### Container Security Configuration

The Dockerfile includes:

- Non-root application execution.
- Reduced image size through a slim Python base image.
- Disabled Python bytecode generation.
- Enabled unbuffered application output.
- Installed dependencies through requirements.txt.

### Verification

- Docker image built successfully.
- Container started successfully.
- Container status checked using `docker ps`.
- Home endpoint tested.
- Health endpoint tested.
- Version endpoint tested.
- Container logs inspected.

### Result

The Flask application operated successfully inside Docker.

---

## Milestone 4: Initial Container Vulnerability Assessment

**Date:** 1 November 2026

**Status:** Completed

### Tool

Trivy 0.76.1

### Target

Docker image:

`devsecops-app:v1`

Operating-system base:

Debian 13.7

### Initial Scan Results

| Severity | Vulnerability records |
|---|---:|
| Critical | 0 |
| High | 49 |
| Medium | 62 |
| Low | 63 |
| Unknown | 1 |
| **Total** | **175** |

### Scan Categories

- Operating-system packages: 166 records.
- Python packages: 9 records.

### Notable Python Package Findings

- Flask 3.1.2
- msgpack 1.1.2
- setuptools 70.3.0
- urllib3 2.7.0

### Interpretation

The initial container vulnerability assessment identified findings in operating-system and Python-related components.

The findings established the initial security baseline for subsequent remediation.

The reported counts represent scanner records and should not be interpreted as confirmed exploitable vulnerabilities.

### Evidence

- `security/trivy-image-report.json`
- `security/trivy-image-summary.txt`

---

## Milestone 5: Dependency Remediation and Comparative Vulnerability Scan

**Date:** 1 November 2026

**Status:** Initial remediation completed; further triage required.

### Baseline and Updated Images

| Image | Purpose |
|---|---|
| `devsecops-app:v1` | Original baseline |
| `devsecops-app:v2` | Updated image |

### Remediation

- Updated Flask from 3.1.2 to 3.1.3.
- Preserved v1 as the baseline image.
- Built v2 as a separate image.
- Re-scanned the updated image using Trivy 0.76.1.

### Comparative Results

| Severity | v1 | v2 |
|---|---:|---:|
| Critical | 0 | 0 |
| High | 49 | 49 |
| Medium | 62 | 62 |
| Low | 63 | 62 |
| Unknown | 1 | 1 |
| **Total** | **175** | **174** |

### Scan Category Comparison

| Category | v1 | v2 |
|---|---:|---:|
| Operating-system findings | 166 | 166 |
| Python findings | 9 | 8 |

### Observation

The Flask finding CVE-2026-27205 was no longer reported in v2 after upgrading Flask to 3.1.3.

The overall finding count decreased by one scanner record.

No reduction was observed in the reported High or Critical severity counts.

### Conclusion

The targeted Flask update removed one reported finding. Further investigation and remediation of remaining operating-system and Python-related findings are required.

### Evidence

- `security/trivy-image-report.json`
- `security/trivy-image-summary.txt`
- `security/trivy-image-report-v2.json`

---

## Milestone 6: SBOM and Runtime Vulnerability Triage

**Date:** 1 November 2026

**Status:** Investigation completed; setuptools finding unresolved.

### Objective

Investigate discrepancies between Trivy's SBOM-derived component findings and the runtime Python package inventory.

### Findings

The v2 Trivy report identified:

- msgpack 1.1.2
- urllib3 2.7.0
- setuptools 70.3.0

Runtime inspection showed that msgpack and urllib3 were vendored within pip 26.2.2 rather than installed as standalone application dependencies.

The inspected Python runtime package inventory did not identify setuptools as an installed Python distribution.

The Trivy report identified setuptools as an SBOM-derived component. Its associated vulnerability findings were retained for further investigation.

### Interpretation

The investigation distinguished between:

- Direct application dependencies.
- Vendored packages within Python tooling.
- SBOM component records.
- Installed runtime distributions.

The setuptools finding was not suppressed or classified as a false positive.

### Conclusion

Vulnerability triage requires consideration of package provenance, runtime context, and SBOM evidence rather than severity alone.

---

## Milestone 7: Local Kubernetes Cluster Setup

**Date:** 2 November 2026

**Status:** Completed

### Implementation

- Enabled Kubernetes through Docker Desktop.
- Verified the Kubernetes context.
- Verified the Kubernetes control plane.
- Verified the Kubernetes node.
- Inspected the Kubernetes system pods.
- Verified the cluster networking component.

### Environment

| Component | Value |
|---|---|
| Kubernetes context | docker-desktop |
| Kubernetes version | v1.36.1 |
| Node | desktop-control-plane |
| Networking component | kindnet |
| Node status | Ready |

### Verification

The Kubernetes control plane and system pods were running successfully.

The local cluster was available for application deployment testing.

---

## Milestone 8: Local Container Registry

**Date:** 2 November 2026

**Status:** Completed

### Implementation

Created a local Docker registry using port 5001.

Registry:

`localhost:5001`

Image:

`localhost:5001/devsecops-app:v2`

### Verification

- Tagged the v2 image.
- Pushed the image to the local registry.
- Verified the image repository through the registry catalog API.
- Verified that a Kubernetes test pod could access the registry catalog.

Registry digest:

```text
sha256:39d18d8e53aaa8cf1555e72b5bf4150c35326001f7a4bd702b9bdf8db63e0f01
```

### Result

The updated application image was successfully pushed to and retrieved from the local registry.

---

## Milestone 9: Kubernetes Application Deployment

**Date:** 2 November 2026

**Status:** Completed

### Implementation

Created Kubernetes manifests:

- `kubernetes/base/deployment.yaml`
- `kubernetes/base/service.yaml`

### Deployment Configuration

| Property | Configuration |
|---|---|
| Deployment | devsecops-app |
| Replicas | 2 |
| Image | localhost:5001/devsecops-app:v2 |
| Image pull policy | IfNotPresent |
| Container port | 5000 |
| CPU request | 100m |
| CPU limit | 500m |
| Memory request | 128Mi |
| Memory limit | 256Mi |

### Service Configuration

| Property | Configuration |
|---|---|
| Service | devsecops-app-service |
| Type | ClusterIP |
| Cluster IP | 10.96.117.26 |
| Service port | 80 |
| Target port | 5000 |

### Verification

- Kubernetes manifest dry-run completed successfully.
- Deployment created successfully.
- Both application replicas reached Running status.
- Deployment reported 2/2 available replicas.
- Service created successfully.
- EndpointSlice identified both application pod IP addresses.
- Application health endpoint tested through port forwarding.

### Result

The Flask application was successfully deployed in the local Kubernetes cluster with two replicas and an internal ClusterIP Service.

---

## Milestone 10: Kubernetes Workload Security Hardening

**Date:** 2 November 2026

**Status:** Completed and verified

### Pod-Level Security Configuration

The Deployment included:

- `runAsNonRoot: true`
- `runAsUser: 1000`
- `runAsGroup: 1000`
- `seccompProfile: RuntimeDefault`
- `automountServiceAccountToken: false`

### Container-Level Security Configuration

The application containers included:

- `allowPrivilegeEscalation: false`
- `readOnlyRootFilesystem: true`
- Linux capabilities dropped using `ALL`

### Verification

Both application replicas were inspected using kubectl JSONPath commands.

The observed values matched the intended security configuration.

### Result

The two application pods were successfully configured and verified with the selected Kubernetes workload security controls.

This verification establishes the presence of the configured controls; it is not a complete Kubernetes security audit.

---

## Milestone 11: Container Image Digest Verification

**Date:** 2 November 2026

**Status:** Completed

### Objective

Verify that both running Kubernetes replicas use identical container image content matching the image pushed to the local registry.

### Verification Command

```powershell
kubectl get pods -l app=devsecops-app -o jsonpath="{range .items[*]}{.metadata.name}{'\n'}{.status.containerStatuses[0].imageID}{'\n\n'}{end}"
```

### Observed Digest

Both replicas reported:

```text
sha256:39d18d8e53aaa8cf1555e72b5bf4150c35326001f7a4bd702b9bdf8db63e0f01
```

The digest matched the digest returned during the successful image push.

### Result

Both application replicas were verified to be running identical image content matching the pushed image.

Digest verification establishes image content identity, not publisher authenticity or signature verification.

---

## Milestone 12: Functional Validation of Kubernetes NetworkPolicy Enforcement

**Date:** 2 November 2026

**Status:** Completed

### Objective

Verify whether the local Kubernetes networking implementation enforces ingress NetworkPolicy restrictions.

### Experimental Setup

- Source namespace: `netpol-test`
- Destination namespace: `default`
- Source pod: `netpol-client`
- Destination Service: `devsecops-app-service`
- Destination endpoint: `/health`

### Experiment

Three conditions were evaluated:

1. Baseline connectivity without the temporary policy.
2. Connectivity while an ingress-deny policy was active.
3. Connectivity after deleting the policy.

### Results

| Condition | Observed result |
|---|---|
| Before policy | Healthy response |
| During policy | Connection timeout |
| After policy deletion | Healthy response |

### Interpretation

The results provide functional evidence of NetworkPolicy enforcement for the tested cross-namespace HTTP communication path.

The experiment does not establish enforcement across all possible traffic paths or protocols.

### Cleanup

- Temporary NetworkPolicy deleted.
- Temporary test pod deleted.
- Test namespace remained available after the experiment.

Detailed results are documented in `networkpolicy-validation.md`.

---

## Milestone 13: Terraform-Based AWS Infrastructure

**Status:** Planned / Pending verification

### Planned Activities

- Define AWS infrastructure using Terraform.
- Configure the AWS provider.
- Define networking resources.
- Configure IAM roles and policies.
- Provision the EKS cluster.
- Configure the container registry.
- Validate infrastructure creation and destruction.

### Completion Criteria

This milestone will be marked completed only after successful Terraform validation, infrastructure provisioning, and resource verification.

---

## Milestone 14: GitHub Actions CI/CD Integration

**Status:** Planned / Pending verification

### Planned Activities

- Configure GitHub Actions workflows.
- Automate application build and testing.
- Integrate security scanning.
- Add container image publishing.
- Add Kubernetes deployment automation.
- Capture pipeline execution time and security results.

### Completion Criteria

The workflow must execute successfully and its results must be recorded before this milestone is marked completed.

---

## Milestone 15: Research Algorithm and Comparative Evaluation

**Status:** Planned / Pending implementation and evaluation

### Research Direction

Investigate a risk-aware security-gating approach that considers:

- Vulnerability severity.
- Exploitability.
- Contextual application criticality.

### Planned Decision Categories

- Allow.
- Review.
- Block.

### Planned Comparative Evaluation

Three configurations:

A. Baseline CI/CD without integrated security gating.

B. Conventional DevSecOps with fixed security policies.

C. Proposed risk-aware security gating.

### Planned Metrics

- Precision.
- Recall.
- F1-score.
- Critical vulnerability blocking rate.
- Pipeline execution time.
- Security overhead.
- Resource utilization.
- Deployment reliability.
- Operational cost.

### Completion Criteria

The algorithm must be implemented, tested against a documented benchmark, and evaluated using repeatable experiments before any performance improvement is claimed.

---

## Overall Implementation Status

| Area | Current status |
|---|---|
| Environment setup | Completed |
| Flask application | Completed |
| Docker containerization | Completed |
| Initial Trivy assessment | Completed |
| Targeted dependency remediation | Completed |
| SBOM triage | Completed with unresolved finding |
| Local Kubernetes setup | Completed |
| Local registry | Completed |
| Kubernetes deployment | Completed |
| Workload security hardening | Completed |
| Image digest verification | Completed |
| NetworkPolicy functional validation | Completed |
| AWS infrastructure | Pending |
| ECR and EKS | Pending |
| GitHub Actions CI/CD | Pending |
| Integrated security scanning pipeline | Pending |
| Risk-aware gating algorithm | Pending |
| Comparative research evaluation | Pending |

## Final Progress Statement

The project has established a working local application, containerization workflow, vulnerability assessment process, and Kubernetes deployment with verified workload security controls.

The current implementation provides a foundation for the planned AWS infrastructure, automated CI/CD integration, and research evaluation.

The project remains under development. Production readiness and the effectiveness of the proposed research method have not yet been established.