# Research Evaluation and Comparative Analysis

## 1. Introduction

This document defines the research evaluation framework for the project titled:

**Design and Implementation of a Production-Ready Cloud-Native DevSecOps Platform on AWS using Terraform, Kubernetes, and GitHub Actions.**

The research investigates the relationship between security effectiveness and continuous delivery efficiency.

The primary research direction is the evaluation of risk-aware security gating in cloud-native CI/CD pipelines.

The evaluation will compare conventional security-gating approaches with a proposed risk-aware decision method.

No performance improvements are claimed until the proposed method has been implemented and experimentally evaluated.

## 2. Research Problem

Modern cloud-native applications use automated pipelines to build, test, scan, and deploy software.

Security checks can identify vulnerable dependencies, insecure source-code patterns, exposed secrets, vulnerable container images, and infrastructure misconfigurations.

However, integrating multiple security tools into CI/CD introduces challenges:

- Increased pipeline execution time.
- Large numbers of security findings.
- Duplicate findings across tools.
- Difficulty prioritizing vulnerabilities.
- False-positive handling.
- Risk of blocking delivery for low-priority findings.
- Difficulty balancing security requirements and deployment efficiency.

The research investigates whether contextual risk prioritization can improve security-gating decisions.

## 3. Research Aim

To design, implement, and evaluate a risk-aware security-gating approach that prioritizes security findings using vulnerability severity, exploitability, and contextual criticality.

## 4. Research Objectives

1. Implement a cloud-native application delivery environment.
2. Integrate container and infrastructure security assessment.
3. Establish a baseline CI/CD configuration.
4. Implement conventional fixed-policy security gating.
5. Develop a risk-aware security-gating method.
6. Evaluate security detection and blocking effectiveness.
7. Measure pipeline execution overhead.
8. Compare the three configurations.
9. Identify limitations and trade-offs.

## 5. Research Questions

**RQ1:** How does security scanning integration affect the execution time of a cloud-native CI/CD pipeline?

**RQ2:** How does conventional fixed-policy gating perform in vulnerability detection and blocking?

**RQ3:** Can contextual risk prioritization improve the balance between security effectiveness and delivery efficiency?

**RQ4:** How sensitive are the proposed gating decisions to changes in risk thresholds and contextual criticality?

## 6. Proposed Research Method

The proposed method uses a risk score to prioritize security findings.

A preliminary model is:

\[
R_i = S_i \times E_i \times C_i
\]

Where:

- \(R_i\): Risk score.
- \(S_i\): Vulnerability severity.
- \(E_i\): Exploitability.
- \(C_i\): Contextual criticality.

The model is intended to aggregate technical vulnerability information and application context into a decision.

### 6.1 Risk Factors

**Severity**

Represents the technical severity of the vulnerability.

**Exploitability**

Represents the available evidence about the feasibility or likelihood of exploitation.

**Contextual Criticality**

Represents the importance and exposure of the affected component in the application environment.

### 6.2 Decision Model

The calculated risk score will be mapped into three categories:

| Category | Decision |
|---|---|
| Low risk | Allow |
| Intermediate risk | Review |
| High risk | Block |

The actual score scales and thresholds must be defined in the implementation and validated experimentally.

### 6.3 Proposed Contribution

The contribution is not the multiplication formula by itself.

The research contribution should consist of a reproducible decision framework incorporating:

- Normalized risk inputs.
- Contextual criticality.
- Finding aggregation.
- Duplicate handling.
- Missing-data treatment.
- Threshold calibration.
- Security-gating decisions.
- Comparative performance evaluation.

## 7. Comparative Experimental Design

Three pipeline configurations will be compared.

### A. Baseline CI/CD

A conventional delivery pipeline without integrated security gating.

Purpose:

Establish baseline execution time and deployment behavior.

### B. Conventional DevSecOps

A pipeline with security scanning and predefined fixed-policy gating.

Purpose:

Establish the security effectiveness and execution overhead of conventional security integration.

### C. Proposed Risk-Aware DevSecOps

A pipeline using the proposed contextual risk-scoring and decision framework.

Purpose:

Evaluate whether risk-aware prioritization improves security decisions and delivery efficiency.

## 8. Evaluation Metrics

| Metric | Purpose |
|---|---|
| Precision | Correctness of positive detections |
| Recall | Coverage of known positive cases |
| F1-score | Combined precision and recall |
| Critical blocking rate | Ability to block critical cases |
| Pipeline execution time | Delivery performance |
| Security overhead | Additional time introduced by security checks |
| CPU utilization | Compute consumption |
| Memory utilization | Memory consumption |
| Deployment reliability | Successful deployment frequency |
| Operational cost | Financial resource consumption |

### 8.1 Detection Metrics

\[
Precision = \frac{TP}{TP+FP}
\]

\[
Recall = \frac{TP}{TP+FN}
\]

\[
F1 = 2 \times \frac{Precision \times Recall}{Precision+Recall}
\]

Where:

- TP = True Positives.
- FP = False Positives.
- FN = False Negatives.

The unit of analysis and the ground-truth labeling rules must be established before computing these metrics.

### 8.2 Pipeline Performance

The absolute security overhead is:

\[
Overhead = T_{\text{secured}}-T_{\text{baseline}}
\]

The relative overhead is:

\[
Overhead(\%) =
\frac{T_{\text{secured}}-T_{\text{baseline}}}
{T_{\text{baseline}}}\times100
\]

### 8.3 Critical Blocking Rate

\[
Critical\ Blocking\ Rate =
\frac{\text{Correctly blocked critical cases}}
{\text{Critical cases requiring blocking}}\times100
\]

## 9. Experimental Result Tables

The following tables are templates for recording actual results.

### 9.1 Security Effectiveness

| Metric | Baseline A | Conventional B | Proposed C |
|---|---:|---:|---:|
| True positives | Pending | Pending | Pending |
| False positives | Pending | Pending | Pending |
| False negatives | Pending | Pending | Pending |
| Precision | Pending | Pending | Pending |
| Recall | Pending | Pending | Pending |
| F1-score | Pending | Pending | Pending |
| Critical blocking rate | Pending | Pending | Pending |

### 9.2 Pipeline Performance

| Metric | Baseline A | Conventional B | Proposed C |
|---|---:|---:|---:|
| Average execution time | Pending | Pending | Pending |
| Median execution time | Pending | Pending | Pending |
| Standard deviation | Pending | Pending | Pending |
| CPU utilization | Pending | Pending | Pending |
| Memory utilization | Pending | Pending | Pending |
| Deployment success rate | Pending | Pending | Pending |
| Cost per run | Pending | Pending | Pending |

### 9.3 Risk-Gating Decisions

| Benchmark case | Expected decision | Proposed decision | Correctness |
|---|---|---|---|
| Case 1 | Pending | Pending | Pending |
| Case 2 | Pending | Pending | Pending |
| Case 3 | Pending | Pending | Pending |

These tables must be populated from actual experimental measurements.

## 10. Threshold Sensitivity Analysis

The proposed method depends on risk thresholds.

The evaluation should investigate how different threshold values affect:

- Number of blocked findings.
- Number of review decisions.
- Number of permitted deployments.
- Critical vulnerability blocking.
- False-positive blocking.
- Pipeline execution time.

Thresholds should be selected using a documented calibration process.

The final test data should not be used to tune thresholds in a way that artificially favors the proposed method.

## 11. Statistical Analysis

For repeated execution measurements, calculate:

- Mean.
- Median.
- Standard deviation.
- Minimum.
- Maximum.

Where sufficient observations and suitable assumptions exist, confidence intervals and appropriate statistical tests may be used.

The selected statistical method must be justified.

A statistically significant result should not automatically be interpreted as a practically meaningful improvement.

## 12. Expected Research Outcomes

The study is intended to establish:

1. A working cloud-native DevSecOps implementation.
2. A reproducible security-scanning workflow.
3. A contextual risk-scoring and gating method.
4. A comparative assessment of three pipeline configurations.
5. Quantitative evidence of security effectiveness.
6. Measurements of pipeline execution overhead.
7. A documented analysis of security-efficiency trade-offs.

These are research objectives, not completed findings.

## 13. Limitations

Potential limitations include:

- Benchmark size and representativeness.
- Scanner database changes.
- False-positive classifications.
- Risk-factor subjectivity.
- Threshold selection bias.
- Runner performance variation.
- Differences between local Kubernetes and AWS EKS.
- Limited generalizability to other applications.

## 14. Reproducibility Requirements

Each experiment should record:

- Git commit identifier.
- Application version.
- Container image digest.
- Scanner version.
- Vulnerability database timestamp.
- Terraform version.
- Kubernetes version.
- Runner configuration.
- Benchmark identifier.
- Risk-scoring configuration.
- Pipeline execution timestamps.
- Raw scan reports.
- Deployment outcomes.

## 15. Final Research Evaluation

The proposed risk-aware approach should be evaluated against both baseline CI/CD and conventional DevSecOps gating.

The final analysis must consider security effectiveness and delivery performance together.

A method that reduces pipeline execution time but allows critical vulnerabilities may not be preferable.

Similarly, a method that blocks nearly every finding may create unnecessary delivery interruptions.

The final research conclusion should identify the conditions under which the proposed method provides value, the trade-offs it introduces, and its limitations.

## 16. Conclusion

This evaluation framework provides a structured approach for investigating risk-aware security gating in cloud-native DevSecOps pipelines.

The proposed method will be assessed using documented benchmark cases, controlled experimental configurations, measurable security metrics, and delivery-performance measurements.

The final research contribution will be determined by the experimental results rather than by the proposed algorithm alone.