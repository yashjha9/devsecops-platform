# Functional Validation of Kubernetes NetworkPolicy Enforcement

## 1. Introduction

Kubernetes NetworkPolicy provides a mechanism for controlling network communication to and from pods in a Kubernetes cluster.

It supports network segmentation by defining rules for ingress and egress traffic. These controls help restrict unnecessary communication between application components and reduce the potential attack surface.

This experiment evaluates the functional enforcement of Kubernetes NetworkPolicy in the local environment used for the DevSecOps platform.

A controlled connectivity test was conducted between a temporary client pod in a dedicated namespace and the application Service in the default namespace.

Three conditions were evaluated:

1. Connectivity before applying a NetworkPolicy.
2. Connectivity while an ingress-deny NetworkPolicy was active.
3. Connectivity after deleting the policy.

## 2. Objectives

- Verify cross-namespace connectivity.
- Establish baseline network behavior.
- Apply an ingress-deny NetworkPolicy.
- Observe the effect on application connectivity.
- Verify connectivity restoration after policy removal.
- Preserve reproducible evidence of the experiment.

## 3. Experimental Environment

| Component | Configuration |
|---|---|
| Operating system | Windows |
| Shell | PowerShell |
| Container platform | Docker Desktop |
| Kubernetes context | docker-desktop |
| Kubernetes version | v1.36.1 |
| Node | desktop-control-plane |
| CNI | kindnet |
| CNI image | kindest/kindnetd:v20260528-9350166c |
| Application | DevSecOps Flask application |
| Deployment | devsecops-app |
| Replicas | 2 |
| Service | devsecops-app-service |
| Service type | ClusterIP |
| Service port | 80 |
| Target container port | 5000 |
| Test client image | curlimages/curl:latest |

## 4. Experimental Architecture

The test involved communication between two namespaces.

**Source:**
- Namespace: `netpol-test`
- Pod: `netpol-client`

**Destination:**
- Namespace: `default`
- Service: `devsecops-app-service`
- Application pods: `devsecops-app`

The communication path was:

```text
netpol-test
    |
    v
netpol-client
    |
    v
devsecops-app-service
    |
    v
Application Pod
    |
    v
Container Port 5000
```

The client used the application's health endpoint:

```text
http://devsecops-app-service.default.svc.cluster.local/health
```

## 5. Experimental Procedure

### 5.1 Create the test namespace

```powershell
kubectl create namespace netpol-test
```

Observed result:

```text
namespace/netpol-test created
```

### 5.2 Create the temporary client pod

```powershell
kubectl run netpol-client -n netpol-test --image=curlimages/curl:latest --restart=Never --command -- sleep 3600
```

Verify the pod:

```powershell
kubectl get pods -n netpol-test
```

Observed result:

```text
NAME            READY   STATUS    RESTARTS   AGE
netpol-client   1/1     Running   0          20s
```

### 5.3 Stage 1: Baseline connectivity

Before applying the policy, execute:

```powershell
kubectl exec -n netpol-test netpol-client -- curl -sS --max-time 10 http://devsecops-app-service.default.svc.cluster.local/health
```

Observed result:

```json
{"status":"healthy"}
```

**Interpretation:**

The client successfully accessed the application health endpoint.

This established the baseline condition in which the tested cross-namespace communication was permitted.

### 5.4 Stage 2: Apply the ingress-deny policy

The following policy was created in the default namespace.

```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: devsecops-ingress-test
  namespace: default
spec:
  podSelector:
    matchLabels:
      app: devsecops-app
  policyTypes:
    - Ingress
  ingress: []
```

Apply the policy:

```powershell
@'
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: devsecops-ingress-test
  namespace: default
spec:
  podSelector:
    matchLabels:
      app: devsecops-app
  policyTypes:
    - Ingress
  ingress: []
'@ | kubectl apply -f -
```

Observed result:

```text
networkpolicy.networking.k8s.io/devsecops-ingress-test created
```

### 5.5 Policy explanation

The policy selected application pods using:

```yaml
podSelector:
  matchLabels:
    app: devsecops-app
```

Ingress policy enforcement was enabled using:

```yaml
policyTypes:
  - Ingress
```

No permitted ingress rules were defined:

```yaml
ingress: []
```

Therefore, the policy requested that all ingress traffic to the selected application pods be denied.

### 5.6 Test connectivity while the policy was active

Execute the same command:

```powershell
kubectl exec -n netpol-test netpol-client -- curl -sS --max-time 10 http://devsecops-app-service.default.svc.cluster.local/health
```

Observed result:

```text
curl: (28) Connection timed out after 10001 milliseconds
command terminated with exit code 28
```

**Interpretation:**

The client could no longer successfully reach the application health endpoint while the ingress-deny policy was active.

This behavior was consistent with the intended policy and provided functional evidence of NetworkPolicy enforcement for the tested traffic path.

### 5.7 Stage 3: Delete the temporary policy

Execute:

```powershell
kubectl delete networkpolicy devsecops-ingress-test -n default
```

The policy was successfully deleted.

### 5.8 Verify connectivity restoration

Repeat the original test:

```powershell
kubectl exec -n netpol-test netpol-client -- curl -sS --max-time 10 http://devsecops-app-service.default.svc.cluster.local/health
```

Observed result:

```json
{"status":"healthy"}
```

**Interpretation:**

Connectivity was restored after removing the temporary NetworkPolicy.

This demonstrated that the observed network restriction was reversible and associated with the policy condition.

## 6. Experimental Results

| Stage | Condition | Observed result | Status |
|---|---|---|---|
| 1 | No test policy | Healthy response | Passed |
| 2 | Ingress-deny policy active | Connection timeout | Passed |
| 3 | Policy removed | Healthy response | Passed |

### 6.1 Overall observation

The experiment demonstrated three distinct network behaviors:

- Normal communication before policy application.
- Restricted communication while the policy was active.
- Restored communication after policy removal.

The same client, destination Service, and health endpoint were used throughout the experiment.

## 7. Analysis

The results provide functional evidence that the current kindnet-based local Kubernetes environment enforces ingress NetworkPolicy restrictions for the specific cross-namespace HTTP communication path tested.

This experiment also demonstrates that successful creation of a NetworkPolicy manifest is not sufficient evidence of actual enforcement.

The observed change in application connectivity provides stronger behavioral evidence than manifest validation alone.

The experiment supports the use of NetworkPolicy as a network-segmentation control in the DevSecOps platform.

## 8. Limitations

### 8.1 Limited traffic coverage

Only one cross-namespace HTTP communication path was tested.

Other protocols, ports, external connections, and traffic directions were not evaluated.

### 8.2 Limited policy coverage

Only ingress-deny behavior was tested.

Egress policies, DNS exceptions, namespace-specific allow rules, and complex policy combinations remain untested.

### 8.3 Local cluster environment

The experiment used Docker Desktop Kubernetes rather than AWS EKS.

Results should not automatically be generalized to every Kubernetes CNI implementation or AWS networking configuration.

### 8.4 Timeout interpretation

A connection timeout is consistent with traffic being blocked, but does not independently reveal the precise packet-processing mechanism.

### 8.5 Repeatability

The recorded experiment was executed once as a complete three-stage sequence. Additional repeated trials would strengthen the evaluation.

### 8.6 Test image reproducibility

The test image used the mutable `latest` tag. Future experiments should pin the image by digest.

## 9. Cleanup

The temporary NetworkPolicy was deleted:

```powershell
kubectl delete networkpolicy devsecops-ingress-test -n default
```

The temporary client pod was deleted:

```powershell
kubectl delete pod netpol-client -n netpol-test
```

The user confirmed successful deletion of the client pod.

The `netpol-test` namespace remained present at the end of the recorded experiment.

It may be removed when no longer needed:

```powershell
kubectl delete namespace netpol-test
```

## 10. Conclusion

The functional validation experiment was completed successfully.

The baseline test demonstrated successful application access. The ingress-deny policy then prevented successful communication along the tested path. After policy deletion, connectivity was restored.

These observations provide empirical evidence that the local Kubernetes networking implementation enforces NetworkPolicy for the tested cross-namespace HTTP path.

Further experiments are required to evaluate egress restrictions, additional communication paths, repeated execution, and behavior in AWS EKS.

## Appendix A: Evidence to Preserve

Recommended evidence:

1. Test namespace creation.
2. Test client pod running status.
3. Baseline health response.
4. NetworkPolicy creation output.
5. Connection timeout while policy was active.
6. NetworkPolicy deletion output.
7. Restored health response.
8. Test client deletion output.

These observations should be retained as terminal screenshots or text logs for the implementation report and viva presentation.