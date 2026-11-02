# Design and Implementation of a Production-Ready Cloud-Native DevSecOps Platform on AWS using Terraform, Kubernetes, and GitHub Actions

## Project Overview

This project focuses on designing and implementing a cloud-native DevSecOps platform that integrates infrastructure automation, containerization, Kubernetes orchestration, and security validation into a continuous delivery workflow.

The intended platform uses Infrastructure as Code (IaC), automated CI/CD, container security scanning, and Kubernetes security controls to improve application deployment consistency and security.

The project also investigates the trade-off between security effectiveness and CI/CD execution overhead through comparative experimentation.

## Project Objectives

1. Develop and containerize a lightweight application.
2. Automate infrastructure provisioning using Terraform.
3. Deploy containerized applications using Kubernetes.
4. Integrate security checks into the CI/CD pipeline.
5. Perform vulnerability scanning of container images and dependencies.
6. Apply Kubernetes workload and network security controls.
7. Investigate risk-aware security gating for continuous delivery.
8. Evaluate security effectiveness, pipeline execution time, and resource overhead.

## Technology Stack

| Category | Technology | Status |
|---|---|---|
| Application | Python, Flask | Implemented |
| Containerization | Docker | Implemented |
| Container scanning | Trivy | Implemented |
| Orchestration | Kubernetes | Local deployment implemented |
| Local environment | Docker Desktop Kubernetes | Implemented |
| Infrastructure as Code | Terraform | Planned / pending verification |
| Cloud provider | AWS | Planned / pending verification |
| Container registry | Local Docker registry | Implemented |
| Cloud registry | Amazon ECR | Planned |
| Managed Kubernetes | Amazon EKS | Planned |
| CI/CD | GitHub Actions | Planned |
| SAST | Semgrep or SonarQube | Planned |
| IaC security | Checkov | Planned |
| Secret scanning | Gitleaks | Planned |
| Secrets management | AWS Secrets Manager | Planned |

## Repository Structure

```text
devsecops-platform/
│
├── application/
│   ├── app.py
│   ├── requirements.txt
│   └── Dockerfile
│
├── security/
│   ├── trivy-image-report.json
│   ├── trivy-image-summary.txt
│   └── trivy-image-report-v2.json
│
├── terraform/
│
├── kubernetes/
│   └── base/
│       ├── deployment.yaml
│       └── service.yaml
│
├── scripts/
│
├── documentation/
│   ├── implementation-log.md
│   ├── networkpolicy-validation.md
│   ├── vulnerability-assessment.md
│   ├── architecture.md
│   ├── experimental-methodology.md
│   └── research-evaluation.md
│
├── README.md
└── .gitignore
```

## Current Implementation

The following components have been implemented and verified:

- Flask application with home, health, and version endpoints.
- Docker containerization.
- Non-root application user in the container.
- Initial and updated Docker images.
- Trivy vulnerability assessment.
- Comparative vulnerability scanning of image versions.
- Local container registry.
- Kubernetes Deployment with two replicas.
- Kubernetes ClusterIP Service.
- Application health and readiness probes.
- Kubernetes pod and container security contexts.
- Functional NetworkPolicy enforcement test.
- Container image digest verification.

## Container Images

| Image | Purpose |
|---|---|
| `devsecops-app:v1` | Original vulnerability assessment baseline |
| `devsecops-app:v2` | Updated application image |
| `localhost:5001/devsecops-app:v2` | Image deployed through the local registry |

Verified deployed image digest:

```text
sha256:39d18d8e53aaa8cf1555e72b5bf4150c35326001f7a4bd702b9bdf8db63e0f01
```

Both application replicas reported this same digest.

## Kubernetes Deployment

The application currently runs with two replicas in the local Docker Desktop Kubernetes cluster.

Service configuration:

- Service name: `devsecops-app-service`
- Service type: `ClusterIP`
- Service port: `80`
- Container port: `5000`

Application health endpoint:

```text
/health
```

## Research Direction

The research investigates whether risk-aware security gating can improve the balance between vulnerability detection effectiveness and CI/CD execution overhead.

The proposed approach considers vulnerability severity, exploitability, and contextual criticality to support allow, review, or block decisions.

The research method and experimental evaluation are documented separately. The proposed algorithm must be implemented and evaluated before its effectiveness can be claimed.

## Documentation

Refer to the `documentation/` directory for:

- Implementation history.
- Vulnerability assessment.
- NetworkPolicy validation.
- Proposed architecture.
- Experimental methodology.
- Research evaluation framework.

## Important Note

The project is under development. The existence of a local Kubernetes deployment does not establish that the complete AWS-based platform is production-ready.

Production readiness requires additional implementation and validation, including cloud infrastructure security, IAM, secrets management, monitoring, reliability, disaster recovery, and CI/CD security controls.