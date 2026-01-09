# ZTNA Demo – Policy-Driven Zero Trust Access Control

## Overview

This project is an enterprise-grade **Zero Trust Network Access (ZTNA) demonstration** that showcases how modern organizations can enforce **policy-based access control** using a decoupled authorization engine. The system is built to reflect real-world Zero Trust principles where **no request is trusted by default**, and every access attempt is evaluated dynamically against centrally managed policies.

The demo uses **Open Policy Agent (OPA)** as an external Policy Decision Point (PDP) and a lightweight application service acting as the Policy Enforcement Point (PEP). All components are containerized and orchestrated using Docker Compose to ensure reproducibility and ease of deployment.

---

## Key Objectives

* Demonstrate Zero Trust Architecture concepts in practice
* Implement authorization as a separate, policy-driven service
* Showcase Policy-as-Code using Rego
* Enable real-time access decisions without redeploying applications
* Provide a reproducible and automated demo environment

---

## Architecture Overview

The system follows a classic Zero Trust access flow:

1. A client makes a request to the protected application
2. The application forwards contextual data to OPA for authorization
3. OPA evaluates the request against defined Rego policies
4. OPA returns an allow or deny decision
5. The application enforces the decision at runtime

This architecture mirrors enterprise security platforms such as BeyondCorp-style access models, API gateways, and service mesh authorization layers.

---

## Technology Stack

* **Application Layer:** Python (Flask)
* **Authorization Engine:** Open Policy Agent (OPA)
* **Policy Language:** Rego
* **Containerization:** Docker
* **Orchestration:** Docker Compose
* **Automation:** Shell scripting

---

## Project Structure

```
ZTNA-Demo/
├── app/
│   ├── app.py              # Policy Enforcement Point (PEP)
│   └── requirements.txt
├── opa/
│   ├── policy.rego         # Zero Trust access policies
│   └── data.json           # Policy data and attributes
├── docker-compose.yml      # Multi-service orchestration
├── demo.sh                 # Automated demo and validation script
└── README.md
```

---

## Zero Trust Design Principles Implemented

* **Never Trust, Always Verify**: Every request is evaluated independently
* **Least Privilege Access**: Policies explicitly define what is allowed
* **Decoupled Authorization**: Application logic is isolated from access rules
* **Policy as Code**: Security rules are version-controlled and auditable
* **Dynamic Enforcement**: Policy updates take effect without service restarts

---

## Running the Demo

### Prerequisites

* Docker
* Docker Compose
* curl (for testing endpoints)

### Step 1: Start the Services

```
docker compose up --build
```

### Step 2: Verify Service Health

```
curl http://localhost:8181/health
```

Expected response:

```
{}
```

### Step 3: Run the Automated Demo

```
./demo.sh
```

The script demonstrates both allowed and denied access scenarios based on active policies.

---

## Policy Management

Policies are defined using Rego and evaluated by OPA at runtime. This enables:

* Centralized authorization logic
* Rapid policy iteration
* Clear separation between application code and security rules

Example policy use cases include:

* Role-based access control
* Context-aware decisions
* Environment-specific access rules

---

## Enterprise Relevance

This demo reflects real-world patterns used in:

* Zero Trust Network Access platforms
* API gateways and service meshes
* Cloud-native security architectures
* Compliance-driven access control systems

The architecture is directly extensible to Kubernetes, service mesh environments, and identity-aware proxy systems.

---

## Future Enhancements

* JWT-based identity claims
* Device posture and context-aware policies
* Audit logging and decision tracing
* Kubernetes-native deployment
* Role and attribute-based access control

---

## Conclusion

This project demonstrates how Zero Trust principles can be practically implemented using modern, cloud-native tooling. By externalizing authorization logic and enforcing access through real-time policy evaluation, the system provides a scalable and secure foundation suitable for enterprise environments.

---



