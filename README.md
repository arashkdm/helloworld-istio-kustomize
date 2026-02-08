# Helloworld – Kubernetes, Istio, Kustomize & Custom Controller

## Overview

This project demonstrates a small but realistic **platform-style setup** on Kubernetes, focusing on:

* Environment separation (test / prod)
* Traffic management using **Istio Gateway & VirtualService**
* Configuration-driven rollouts using **ConfigMaps**
* A lightweight **custom controller** that reacts to configuration changes
* Declarative configuration with **Kustomize overlays**

The goal is not only to make the application work, but to show **clean structure, clear responsibilities, and production‑style reasoning**.

---

## High-level Architecture

Request flow:

```
Client
  ↓ (Host header)
 среды
Istio IngressGateway
  ↓
VirtualService (test / prod)
  ↓
Kubernetes Service
  ↓
Application Pods
```

Configuration flow:

```
ConfigMap change
  ↓
Custom Controller
  ↓
Patch Deployment annotation
  ↓
Rolling restart of pods
```

---

## Repository Structure

```
.
├── k8s/
│   └── apps/
│       ├── base/
│       │   ├── deployment.yaml
│       │   ├── service.yaml
│       │   ├── configmap.yaml
│       │   ├── istio-gateway.yaml
│       │   └── kustomization.yaml
│       │
│       └── overlays/
│           ├── test/
│           │   ├── virtualservice-test.yaml
│           │   ├── patch-configmap.yaml
│           │   └── kustomization.yaml
│           │
│           └── prod/
│               ├── virtualservice-prod.yaml
│               ├── patch-configmap.yaml
│               └── kustomization.yaml
│
├── controller/
│   ├── controller.py
│   ├── Dockerfile
│   └── requirements.txt
│
└── README.md
```

Key ideas:

* **Base** contains shared resources
* **Overlays** define environment-specific behavior
* `nameSuffix` is used to safely create isolated test/prod resources

---

## Environment Separation Strategy

* `test` and `prod` are deployed **into the same namespace** for simplicity
* Isolation is achieved using:

  * `nameSuffix` (`-test`, `-prod`)
  * separate Services
  * separate VirtualServices
* **Istio Gateway** is duplicated per environment due to suffixing rules

This approach avoids:

* label/selector conflicts
* accidental traffic mixing
* fragile patching of shared resources

---

## Istio Configuration

### Gateway

Defined in `base/istio-gateway.yaml` and then duplicated via Kustomize suffixing.
Each gateway exposes HTTP on port 80 and matches environment-specific hosts:

* `helloworld-test.local`
* `helloworld-prod.local`

### VirtualService

Each environment defines its own VirtualService:

* Explicitly references its **own Gateway** (after suffixing)
* Routes traffic based on the `Host` header
* Forwards requests to the matching Service (`helloworld-test` / `helloworld-prod`)

This design keeps routing logic **explicit and predictable**.

---

## Application Behavior

The application is a simple HTTP server that:

* Reads a `message` value from a ConfigMap
* Returns it as plain text in HTTP responses

This allows easy validation of:

* correct routing
* correct environment isolation
* correct rollout behavior

---

## Custom Controller

### Purpose

The custom controller watches ConfigMaps and ensures that:

> Any change in configuration triggers a rolling restart of the related Deployment.

This mimics a common real‑world requirement where applications do not hot‑reload configuration.

### Behavior

* Watches ConfigMaps with a specific naming convention
* Detects `MODIFIED` events
* Infers the target environment (test / prod)
* Patches the corresponding Deployment with a timestamp annotation

This triggers a standard Kubernetes rolling update.

---

## Testing Scenarios

### 1. Routing via Istio

```bash
curl -H "Host: helloworld-test.local" http://<INGRESS_IP>/
```

Expected result:

```
hello from test environment
```

```bash
curl -H "Host: helloworld-prod.local" http://<INGRESS_IP>/
```

Expected result:

```
hello from prod environment
```

---

### 2. ConfigMap-driven rollout

```bash
kubectl patch configmap helloworld-test \
  -p '{"data":{"message":"changed TEST"}}'
```

Controller logs:

```
[event] type=MODIFIED configmap=helloworld-test env=test
[restart] patched deployment=helloworld-test restartedAt=...
```

After rollout:

```bash
curl -H "Host: helloworld-test.local" http://<INGRESS_IP>/
```

Response:

```
changed TEST
```

```bash
kubectl patch configmap helloworld-prod \
  -p '{"data":{"message":"changed PROD"}}'
```

Controller logs:

```
[event] type=MODIFIED configmap=helloworld-prod env=prod
[restart] patched deployment=helloworld-prod restartedAt=...
```

After rollout:

```bash
curl -H "Host: helloworld-prod.local" http://<INGRESS_IP>/
```

Response:

```
changed PROD
```

---

## Images & Architecture Notes

* Docker images are available on Docker Hub
* Images are built for **linux/amd64 (x86_64)**

⚠️ If your environment differs (e.g. ARM-based cluster):

* Rebuild images locally using the provided Dockerfiles
* Push to your own registry if required

---

## Environment Assumptions

Tested with:

* Kubernetes cluster with external LoadBalancer support
* Istio installed (default profile)
* Kustomize v5+
* Docker / container runtime compatible with amd64 images

---

## Workstation vs Cluster Differences

Things that may require adjustment in different contexts:

* LoadBalancer IP (cloud provider dependent)
* Image architecture (amd64 vs arm64)
* Namespace strategy (single vs multiple namespaces)
* External traffic reaches the application through the Istio IngressGateway service exposed via a LoadBalancer.

These are intentionally kept simple to focus on **core platform concepts**.

---

## Notes & Limitations

* This project prioritizes clarity over maximal reuse
* Some resources (e.g. Gateways) are duplicated intentionally to avoid hidden coupling
* The controller is minimal by design and not hardened for production use

---

## Summary

This repository demonstrates:

* Clean Kustomize layering
* Practical Istio usage
* Configuration-driven deployments
* Platform-style thinking rather than application-only focus

It is intended as a **technical exercise**, not a full production blueprint.
