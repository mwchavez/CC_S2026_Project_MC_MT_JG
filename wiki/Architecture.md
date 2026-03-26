# Architecture > IAM (Identity and Access Management)

**Project:** CloudHoney — GCP-Based Financial Sector Honeypot & Security Event Monitoring Platform  
**Project ID:** `cloudhoney-sp26`  
**Region:** `us-central1`  
**Last Updated:** March 2026

---

## Overview

CloudHoney follows the **principle of least privilege** across all identity and access management decisions. Every team member and service account is granted only the minimum permissions required to perform their specific role. This approach is consistent with financial sector security standards, where over-provisioned access is considered a critical vulnerability.

In GCP, IAM operates at three levels: **project-level roles** (broad permissions across all resources), **resource-level roles** (scoped to specific services), and **service accounts** (non-human identities attached to applications and VMs). CloudHoney uses all three.

---

## Team Member IAM Roles

Team members access the GCP Console using their personal Google accounts. Each member is assigned a **project-level IAM role** based on their responsibilities.

| Team Member | Project Role | GCP IAM Role | Justification |
|---|---|---|---|
| Moses Chavez (Project Leader) | Architecture, infrastructure, integration | `Owner` (`roles/owner`) | Full administrative control required for provisioning all 12 GCP services, managing billing, configuring IAM, and troubleshooting cross-service issues. Only one team member holds this role. |
| Marissa Turner (Developer) | Honeypot app, traffic simulator, dashboard | `Editor` (`roles/editor`) | Read/write access to all resources for development and deployment. Cannot modify IAM policies or billing — preventing accidental permission escalation. |
| Juliana Garza (Scribe) | Documentation, research, compliance | `Viewer` (`roles/viewer`) | Read-only access to all resources for documentation and verification. Cannot create, modify, or delete any cloud resources — appropriate for a documentation-focused role. |

### Design Decision: Why Not Custom Roles?

GCP supports custom IAM roles with granular permission sets. For a production financial institution, custom roles would be preferred to further restrict access. For this academic project, GCP's predefined basic roles (`Owner`, `Editor`, `Viewer`) provide a clear and auditable separation of duties that maps directly to team responsibilities. The tradeoff — slightly broader permissions than strictly necessary for the Developer and Scribe roles — is acceptable given the project's academic scope and short lifecycle.

---

## Service Account Configuration

CloudHoney uses a **dedicated service account** for all application-level operations. No personal credentials are ever used in code, environment variables, or configuration files.

### Service Account: `cloudhoney-app-sa`

- **Full identifier:** `cloudhoney-app-sa@cloudhoney-sp26.iam.gserviceaccount.com`
- **Purpose:** Attached to the Compute Engine honeypot VM and used by Cloud Functions to interact with GCP services at runtime.
- **Authentication method:** GCP-managed — the service account is attached directly to the VM and Cloud Functions. No key files are downloaded or stored.

### Granted Roles

| IAM Role | Role ID | Purpose | Services Accessed |
|---|---|---|---|
| Logs Writer | `roles/logging.logWriter` | Write honeypot event logs to Cloud Logging | Cloud Logging |
| Cloud Datastore User | `roles/datastore.user` | Read/write classified events to Firestore (Native mode uses Datastore IAM roles) | Firestore |
| Pub/Sub Publisher | `roles/pubsub.publisher` | Publish log events and alert messages to Pub/Sub topics | Pub/Sub |
| Secret Manager Secret Accessor | `roles/secretmanager.secretAccessor` | Read-only access to retrieve the SendGrid API key at runtime | Secret Manager |
| Storage Object Creator | `roles/storage.objectCreator` | Write log exports to Cloud Storage bucket | Cloud Storage |

### Least-Privilege Analysis

| Role | Access Level | Notes |
|---|---|---|
| Logs Writer | Write-only to Cloud Logging | Cannot read or delete logs — appropriate for an application that only emits events. |
| Cloud Datastore User | Read/write to Firestore | Required for both Cloud Functions (write classified events) and the dashboard (read events). Does not grant admin or delete-collection permissions. |
| Pub/Sub Publisher | Publish-only | Cannot create/delete topics or manage subscriptions. Can only push messages to existing topics. |
| Secret Manager Secret Accessor | Read-only for secret values | Cannot create, delete, or modify secrets. Can only retrieve the *value* of an existing secret at runtime. This is the most restrictive Secret Manager role available. |
| Storage Object Creator | Write-only to Cloud Storage | Cannot read, list, or delete existing objects. Can only create new objects in the bucket — appropriate for a write-only log export pipeline where log integrity must be preserved. |

### What This Service Account Cannot Do

To demonstrate the scope limitation of our least-privilege approach, `cloudhoney-app-sa` explicitly **cannot**:

- Create, modify, or delete GCP resources (VMs, buckets, topics, functions)
- Modify IAM policies or grant permissions to other accounts
- Access billing information
- Create or delete Pub/Sub topics or subscriptions
- Create or delete Secret Manager secrets
- Delete Firestore collections or databases
- Read, list, or delete objects in Cloud Storage (write-only access preserves log integrity)
- Access any GCP services not listed above

---

## Instructor Access

Per course requirements, the following instructor accounts have been added as repository collaborators on GitHub:

| Account | Access |
|---|---|
| `gdparra-edu` | GitHub repository collaborator |
| `cyberknowledge` | GitHub repository collaborator |

Instructor accounts are **not** added to the GCP project IAM policy. GCP resource access for grading will be demonstrated via the live demo and documented in the Wiki.

---

## Compliance Mapping

### PCI DSS Requirement 7 — Restrict Access to System Components and Cardholder Data

> *"Access to system components and cardholder data is limited to only those individuals whose job requires such access."*

**CloudHoney alignment:**
- Team member IAM roles follow separation of duties — only the Project Leader has administrative access.
- The service account is scoped to five specific roles with no admin or delete capabilities.
- The Scribe role is read-only, consistent with the principle that documentation personnel should not have write access to production systems.

### PCI DSS Requirement 8 — Identify Users and Authenticate Access

> *"Every user is assigned a unique ID before being allowed access to system components."*

**CloudHoney alignment:**
- Each team member authenticates with their individual Google account — no shared credentials.
- The service account (`cloudhoney-app-sa`) is a distinct, auditable identity separate from all human users.
- GCP Cloud Audit Logs record every IAM authentication event, providing a complete access trail.

### GLBA Safeguards Rule — Access Controls

> *Financial institutions must implement access controls on customer information systems.*

**CloudHoney alignment:**
- Although CloudHoney processes simulated (not real) financial data, the IAM architecture mirrors the access control patterns required for systems handling actual customer information.
- The dedicated service account with no downloaded keys ensures that application credentials cannot be extracted and reused outside the GCP environment.

### PCI DSS Requirement 6.4.3 — Sensitive Authentication Data Not in Production Code

> *"Sensitive authentication data is not stored in production code."*

**CloudHoney alignment:**
- The SendGrid API key is stored exclusively in Secret Manager.
- The service account retrieves it at runtime via the `Secret Manager Secret Accessor` role.
- No credentials, API keys, or secrets appear in source code, environment variables, or `.env` files.
- The `.gitignore` file explicitly excludes credential files from version control.

---

## Verification Commands

Team members can verify their own IAM configuration using Cloud Shell:

```bash
# List all IAM policy bindings on the project
gcloud projects get-iam-policy cloudhoney-sp26 --format="table(bindings.role, bindings.members)"

# View service account roles
gcloud projects get-iam-policy cloudhoney-sp26 \
  --flatten="bindings[].members" \
  --filter="bindings.members:cloudhoney-app-sa@cloudhoney-sp26.iam.gserviceaccount.com" \
  --format="table(bindings.role)"

# Confirm no service account keys have been downloaded (should return empty)
gcloud iam service-accounts keys list \
  --iam-account=cloudhoney-app-sa@cloudhoney-sp26.iam.gserviceaccount.com \
  --managed-by=user
```

---

## Future Improvements (Production Recommendations)

If CloudHoney were deployed in a production financial institution environment, the following IAM enhancements would be recommended:

1. **Replace basic roles with custom roles** — Define granular permission sets for each team member rather than using `Owner`/`Editor`/`Viewer`.
2. **Enable VPC Service Controls** — Create an API-level security perimeter that prevents data exfiltration even if IAM credentials are compromised.
3. **Implement Workload Identity Federation** — Eliminate service account keys entirely by federating identity from external providers.
4. **Enable Organization Policy Constraints** — Enforce IAM restrictions at the organizational level so individual projects cannot override them.
5. **Require MFA for all human accounts** — Enforce multi-factor authentication as a condition of GCP Console access.
