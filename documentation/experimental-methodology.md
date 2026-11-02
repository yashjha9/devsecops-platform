# Experimental Methodology

## 1. Research Overview

This study evaluates the effectiveness and operational impact of integrating security controls into a cloud-native DevSecOps pipeline.

The platform is designed around AWS, Terraform, Kubernetes, Docker, and GitHub Actions. Security analysis is applied across multiple stages of the software delivery lifecycle, including source code, dependencies, infrastructure-as-code, container images, and deployment configuration.

The experimental component compares three CI/CD security approaches:

1. Baseline CI/CD without integrated security gates.
2. Conventional DevSecOps using sequential security scans and fixed policy-based gates.
3. Proposed risk-aware security gating that considers vulnerability severity, exploitability, and application context.

The objective is to investigate whether contextual risk assessment can improve security prioritization while limiting unnecessary pipeline delays.

The methodology distinguishes between platform implementation and experimental evaluation. Results will only be reported after the corresponding experiments have been executed.

## 2. Research Questions

The evaluation is guided by the following research questions.

**RQ1:** How does integrating security scanning into a cloud-native CI/CD pipeline affect vulnerability detection compared with a baseline pipeline?

**RQ2:** How does a conventional fixed-policy security gate compare with a risk-aware security gate in terms of security effectiveness and pipeline execution time?

**RQ3:** Can contextual risk prioritization reduce unnecessary deployment blocks while maintaining an acceptable level of detection and prevention of critical vulnerabilities?

**RQ4:** What operational overhead does the integration of security controls introduce in terms of pipeline duration and resource utilization?

## 3. Research Hypotheses

The following hypotheses will be evaluated experimentally.

- **H1:** Integrating security scanning into CI/CD improves the detection of known security issues compared with a pipeline without integrated security checks.
- **H2:** Risk-aware gating can reduce unnecessary deployment blocks compared with a conventional fixed-policy gate.
- **H3:** Risk-aware gating can provide a measurable trade-off between security effectiveness and pipeline execution time.
- **H4:** Security scanning introduces measurable execution and resource overhead into the CI/CD process.

These are hypotheses, not established findings. They will be accepted, rejected, or treated as inconclusive based on the collected experimental evidence.

## 4. Experimental Environment

The proposed experimental environment consists of the following components.

| Component | Technology | Purpose |
|---|---|---|
| Cloud platform | AWS | Cloud infrastructure |
| Infrastructure provisioning | Terraform | Infrastructure as Code |
| Containerization | Docker | Application packaging |
| Container orchestration | Kubernetes / AWS EKS | Application deployment |
| CI/CD | GitHub Actions | Automated build, test, scan, and deployment |
| Container registry | Amazon ECR | Container image storage |
| Source-code security | Semgrep or SonarQube | Static application security analysis |
| IaC security | Checkov | Terraform configuration analysis |
| Container security | Trivy | Image and dependency vulnerability analysis |
| Secret detection | Gitleaks | Detection of exposed credentials |
| Secret management | AWS Secrets Manager | Centralized secret storage |

The exact tool versions, configurations, scan policies, and infrastructure specifications must be recorded for each experiment.

The local Kubernetes environment may be used for initial functional validation. Experiments intended to make claims about AWS EKS must be executed on EKS and clearly distinguished from local-cluster results.

## 5. Experimental Design

Three experimental configurations will be compared.

### 5.1 Configuration A: Baseline CI/CD

The baseline represents a delivery pipeline without integrated security scanning or security-based deployment gates.

Expected workflow:

1. Retrieve source code.
2. Build the application.
3. Execute application tests.
4. Build the container image.
5. Deploy the application.

This configuration provides a reference for measuring pipeline execution time and deployment behavior without integrated security controls.

### 5.2 Configuration B: Conventional DevSecOps

This configuration integrates security scanners into the delivery pipeline.

Expected workflow:

1. Retrieve source code.
2. Execute source-code security analysis.
3. Scan dependencies and container images.
4. Scan Terraform configurations.
5. Detect exposed secrets.
6. Evaluate findings using fixed severity or policy thresholds.
7. Allow or block deployment according to the configured policy.

The scanning tools and their configurations must remain consistent with those used in Configuration C wherever possible.

### 5.3 Configuration C: Proposed Risk-Aware Security Gating

This configuration uses security findings from the scanning stages and evaluates them using a contextual risk-scoring method.

The proposed method considers:

- Vulnerability severity.
- Exploitability.
- Application or deployment context.

The resulting score is used to classify findings into decision categories:

- **Allow:** The finding does not exceed the configured risk threshold.
- **Review:** The finding requires additional assessment before deployment.
- **Block:** The finding exceeds the configured blocking threshold.

The thresholds will be defined and calibrated during the experimental phase. They must not be selected after observing test outcomes merely to improve reported performance.

To isolate the effect of the decision method, Configuration B and Configuration C should use equivalent scanning tools, scan targets, and scan settings. Their principal difference should be the security decision policy.

## 6. Proposed Risk-Scoring Method

The proposed method uses a contextual risk score:

\[
R_i = S_i \times E_i \times C_i
\]

Where:

- \(R_i\) = Risk score for finding \(i\).
- \(S_i\) = Severity of the finding.
- \(E_i\) = Exploitability of the finding.
- \(C_i\) = Contextual criticality of the affected application component.

### 6.1 Severity

Severity represents the impact level associated with a security finding.

A possible normalized scale is:

| Score | Severity |
|---|---|
| 1 | Low |
| 2 | Medium |
| 3 | High |
| 4 | Critical |

Severity should be derived consistently from scanner output or a documented severity mapping.

### 6.2 Exploitability

Exploitability represents how feasible it is for an attacker to exploit the finding.

The assessment should consider available vulnerability intelligence, exploit availability, attack prerequisites, and exposure.

A normalized scale can be defined as:

| Score | Exploitability |
|---|---|
| 1 | Low |
| 2 | Moderate |
| 3 | High |
| 4 | Very high |

The assessment rules and evidence sources must be documented. If exploitability cannot be established, the finding should be marked unknown rather than assigned an unsupported score.

### 6.3 Contextual Criticality

Contextual criticality represents the importance and exposure of the affected component.

Relevant factors may include:

- Whether the component is externally accessible.
- Whether it handles sensitive data.
- Whether it is part of a critical application function.
- Whether exploitation could affect other services.
- Whether the affected component is deployed in a privileged or sensitive environment.

A possible scale is:

| Score | Context |
|---|---|
| 1 | Low criticality |
| 2 | Moderate criticality |
| 3 | High criticality |
| 4 | Critical component |

The classification criteria must be defined before evaluating the test cases.

### 6.4 Decision Thresholds

The risk score will be mapped to the three deployment decisions:

| Decision | Interpretation |
|---|---|
| Allow | Finding is below the review threshold |
| Review | Finding requires manual or additional automated assessment |
| Block | Finding exceeds the blocking threshold |

The review and blocking thresholds must be calibrated using a development or calibration dataset and then evaluated on a separate test dataset.

The experiment will examine the sensitivity of the results to alternative threshold values.

The proposed formula is a candidate decision model. Its usefulness and reliability must be established experimentally. It should not be described as a novel algorithm solely because it combines three factors.

## 7. Benchmark and Test Dataset

The experimental benchmark should contain both secure and intentionally vulnerable test configurations.

Potential test categories include:

- Source-code security issues.
- Vulnerable application dependencies.
- Container image vulnerabilities.
- Insecure Terraform configurations.
- Kubernetes security misconfigurations.
- Exposed credentials or secrets.

Each test case should have a documented expected outcome, supported by a known vulnerability, controlled configuration, or manually verified security condition.

The benchmark should record:

| Field | Description |
|---|---|
| Test case ID | Unique identifier |
| Test category | Source, dependency, IaC, image, Kubernetes, or secret |
| Expected result | Secure or vulnerable |
| Expected severity | Ground-truth severity where available |
| Exploitability | Documented assessment |
| Contextual criticality | Predefined application-context rating |
| Scanner result | Actual tool output |
| Gate decision | Allow, review, or block |

Duplicate findings referring to the same underlying vulnerability should be handled consistently. The evaluation must distinguish scanner records from unique underlying security issues.

The benchmark should not rely exclusively on scanner-generated findings as ground truth. Known test cases and independent verification are needed to assess false negatives.

## 8. Experimental Procedure

The following procedure will be used for each experimental configuration.

1. Prepare a documented source-code revision and test dataset.
2. Record tool versions and relevant configuration settings.
3. Execute the CI/CD pipeline.
4. Collect scanner outputs and pipeline logs.
5. Record the pipeline execution time.
6. Record CPU and memory utilization where measurable.
7. Record the deployment outcome.
8. Compare detected findings with the benchmark ground truth.
9. Record whether the pipeline allowed, reviewed, or blocked each test case.
10. Repeat the experiment under the same conditions.

The same application version, benchmark cases, runner environment, and workload should be used across the three configurations wherever possible.

The number of repetitions should be determined before the final evaluation. Repeated runs are needed to account for normal variation in pipeline execution time.

Any failed or incomplete run should be documented, with a predefined rule for deciding whether it is excluded or repeated.

## 9. Evaluation Metrics

The following metrics will be used to evaluate the proposed platform.

### 9.1 True Positives, False Positives, True Negatives, and False Negatives

- **True Positive (TP):** A vulnerable test case correctly identified as vulnerable.
- **False Positive (FP):** A secure test case incorrectly identified as vulnerable.
- **True Negative (TN):** A secure test case correctly identified as secure.
- **False Negative (FN):** A vulnerable test case not identified as vulnerable.

These definitions must be applied consistently to the chosen unit of analysis, such as a unique vulnerability or a benchmark test case.

### 9.2 Precision

Precision measures the proportion of positive findings that are correct.

\[
Precision = \frac{TP}{TP + FP}
\]

Higher precision indicates fewer false positives.

### 9.3 Recall

Recall measures the proportion of actual vulnerable cases correctly detected.

\[
Recall = \frac{TP}{TP + FN}
\]

Higher recall indicates fewer missed vulnerable cases.

### 9.4 F1-Score

The F1-score is the harmonic mean of precision and recall.

\[
F1 = 2 \times \frac{Precision \times Recall}{Precision + Recall}
\]

It provides a combined measure of detection precision and recall.

### 9.5 Detection Rate

\[
Detection\ Rate = \frac{Detected\ Vulnerable\ Cases}{Total\ Vulnerable\ Cases} \times 100
\]

The detection rate will be calculated against the verified benchmark ground truth.

### 9.6 Critical Blocking Rate

\[
Critical\ Blocking\ Rate =
\frac{Critical\ Vulnerable\ Cases\ Correctly\ Blocked}
{Total\ Critical\ Vulnerable\ Cases}
\times 100
\]

This metric measures whether critical vulnerable cases are prevented from reaching deployment.

### 9.7 Pipeline Execution Time

Pipeline execution time is the elapsed time between the defined pipeline start and completion events.

The mean, median, and variation across repeated runs will be reported.

### 9.8 Security Overhead

Security overhead measures the additional execution time introduced by security checks.

\[
Security\ Overhead =
\frac{T_{secured} - T_{baseline}}
{T_{baseline}}
\times 100
\]

Where:

- \(T_{secured}\) = Execution time of the secured pipeline.
- \(T_{baseline}\) = Execution time of the baseline pipeline.

### 9.9 Resource Utilization

CPU and memory utilization will be recorded where the execution environment provides reliable measurements.

The collection method, sampling interval, and measurement scope must be documented.

### 9.10 Deployment Reliability

Deployment reliability will be evaluated using successful deployment attempts relative to total valid deployment attempts.

\[
Deployment\ Success\ Rate =
\frac{Successful\ Deployments}
{Total\ Deployment\ Attempts}
\times 100
\]

Security blocks must be distinguished from technical deployment failures.

### 9.11 Recovery Time

Recovery time measures the time required to restore the application to a healthy state after a defined deployment or application failure.

The failure scenario and recovery start and end events must be specified before measurement.

### 9.12 Cost

Where cloud resources are used, infrastructure and execution costs will be estimated using recorded resource consumption and applicable AWS pricing.

Local development results must not be presented as AWS operating costs.

## 10. Data Collection and Analysis

Data will be collected from:

- GitHub Actions execution logs.
- Security scanner reports.
- Trivy vulnerability reports.
- Checkov IaC scan reports.
- Source-code security scan reports.
- Gitleaks reports.
- Kubernetes deployment status and events.
- Application health-check responses.
- Infrastructure and resource monitoring records.
- AWS cost information, where applicable.

A structured experiment dataset will be maintained with configuration identifiers, timestamps, tool versions, test-case identifiers, scan results, gate decisions, execution duration, and deployment outcomes.

The analysis will include:

1. Comparison of detection metrics across the three configurations.
2. Comparison of pipeline duration and security overhead.
3. Comparison of critical vulnerability blocking performance.
4. Analysis of false-positive and false-negative behavior.
5. Comparison of deployment reliability.
6. Analysis of CPU, memory, and cost where sufficient data exists.
7. Sensitivity analysis for risk-scoring thresholds.

Results will be presented using tables and appropriate charts.

For repeated measurements, descriptive statistics such as mean, median, standard deviation, and interquartile range will be reported as appropriate.

Inferential statistical tests will only be used when the sample size, measurement design, and test assumptions justify them. Statistical significance will not be claimed without appropriate analysis.

## 11. Validity Considerations

### 11.1 Internal Validity

Differences in runner performance, network conditions, tool versions, scan configuration, and workload can influence results.

These factors should be controlled or recorded to reduce confounding effects.

### 11.2 External Validity

Results obtained from one sample application, benchmark, or Kubernetes environment may not generalize to all cloud-native applications or enterprise deployments.

The scope and characteristics of the experimental environment must be reported.

### 11.3 Construct Validity

Scanner findings are not equivalent to confirmed exploitable vulnerabilities.

The study therefore uses a documented benchmark and independent verification where possible. Detection, risk classification, and deployment blocking are evaluated as distinct outcomes.

### 11.4 Conclusion Validity

A small number of test cases or repeated runs may produce unstable results.

The number of benchmark cases and repetitions must be reported. Conclusions should reflect the available evidence and its limitations.

## 12. Reproducibility

To support reproducibility, the project will maintain:

- Source-code revision identifiers.
- Terraform configuration versions.
- Kubernetes manifest versions.
- GitHub Actions workflow definitions.
- Scanner and dependency versions.
- Scanner configuration and policy files.
- Benchmark test-case definitions.
- Risk-scoring rules and thresholds.
- Raw experiment outputs.
- Data-processing scripts.
- Experiment execution records.

Where practical, the benchmark and evaluation scripts should be version-controlled.

Secrets, access tokens, private keys, and sensitive cloud configuration must never be included in public experiment artifacts.

## 13. Security and Ethical Considerations

Intentionally vulnerable configurations will be restricted to controlled test environments.

Vulnerable images and configurations must not be deployed to publicly accessible production infrastructure.

Cloud resources will use appropriate access controls and least-privilege permissions. Credentials will be managed through secure mechanisms rather than committed to source control.

The experiments will use authorized infrastructure and controlled workloads. No unauthorized penetration testing or exploitation of third-party systems is included in the methodology.

## 14. Limitations

The study has several anticipated limitations:

- Scanner results depend on tool versions, vulnerability databases, and configuration.
- Vulnerability severity does not necessarily represent real-world exploitability.
- Contextual criticality requires documented assessment criteria and may involve judgment.
- The proposed risk score may require calibration for different applications.
- Local Kubernetes experiments cannot establish AWS EKS production performance.
- Pipeline duration can vary because of network conditions, caching, and runner availability.
- A controlled benchmark may not represent the full complexity of enterprise workloads.
- Cost estimates depend on the cloud region, resource configuration, and usage period.

These limitations will be considered when interpreting the results.

## 15. Expected Research Contribution

The expected contribution is an implemented and experimentally evaluated cloud-native DevSecOps platform with a risk-aware security-gating approach.

The study aims to provide:

1. A reproducible CI/CD security integration across application code, dependencies, infrastructure configuration, container images, and deployment configuration.
2. A documented contextual risk-scoring and deployment decision method.
3. A comparative evaluation of baseline, conventional, and risk-aware security-gating approaches.
4. An empirical assessment of security effectiveness, pipeline overhead, and deployment behavior.
5. An analysis of the trade-offs between vulnerability detection, critical-risk prevention, and delivery efficiency.

The contribution will be established through implementation evidence and experimental results. No improvement in detection, pipeline efficiency, or deployment reliability will be claimed until supported by the completed evaluation.

## 16. Current Implementation and Remaining Work

The project has already completed several implementation and validation activities, including:

- Development and containerization of a Flask sample application.
- Docker image construction and vulnerability scanning with Trivy.
- Updating the Flask dependency and comparing image scan reports.
- Local Kubernetes cluster setup.
- Deployment of two application replicas.
- Kubernetes readiness and liveness probe validation.
- Non-root container execution and restrictive security-context configuration.
- Service connectivity and application health-check validation.
- Functional testing of a Kubernetes NetworkPolicy.

The following work remains part of the broader project and experimental evaluation:

- Complete and validate the Terraform infrastructure.
- Implement the GitHub Actions CI/CD workflows.
- Integrate and configure the remaining security scanners.
- Implement the conventional fixed-policy and proposed risk-aware gates.
- Define and validate the benchmark ground truth.
- Execute all three experimental configurations.
- Collect repeated measurements and analyze results.
- Document findings, limitations, and conclusions.

The final report will distinguish completed implementation activities from planned or pending experimental work.