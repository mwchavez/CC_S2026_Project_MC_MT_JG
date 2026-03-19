# Architecture

## System Overview

CloudHoney consists of five logical layers:

1. **Traffic Generation** — Python simulator producing realistic attack patterns
2. **Honeypot Endpoint** — Flask app on Compute Engine logging all requests
3. **Log Ingestion & Storage** — Cloud Logging → Cloud Storage pipeline
4. **Processing & Alerting** — Cloud Functions + Pub/Sub detection rules + Firestore
5. **Visualization** — Cloud Run dashboard reading from Firestore

## Architecture Diagram

> TODO: Insert draw.io / Lucidchart diagram showing VPC, subnets, data flow, and service relationships

## GCP Service Inventory

| Service | Model | Role in CloudHoney | Underlying Core Services |
|---------|-------|--------------------|--------------------------|
| Compute Engine | IaaS | Hosts the honeypot Flask app | N/A (this IS core compute) |
| Cloud Logging | SaaS | Receives and indexes honeypot event logs | Google's internal log infrastructure |
| Cloud Storage | IaaS | Long-term log retention in JSON format | N/A (core storage) |
| Cloud Functions | PaaS | Serverless event classification and alerting | GKE containers on Compute Engine |
| Pub/Sub | PaaS | Event routing between logging, functions, and alerts | Google's distributed messaging infrastructure |
| Cloud Run | PaaS | Hosts the visualization dashboard | GKE, Compute Engine, Cloud Load Balancing, VPC |
| Firestore | PaaS | Real-time classified event storage for dashboard reads | Spanner-derived infrastructure, Compute Engine |
| Secret Manager | SaaS | Secure storage for SendGrid API key | Google's HSM-backed infrastructure |
| Cloud Monitoring | SaaS | System health and uptime monitoring | Google's internal monitoring stack |
| Cloud IAM | SaaS | Access control for team members and service accounts | Google's identity infrastructure |

## Cloud Domains Covered

- **Security & Identity** — IAM, Secret Manager, honeypot design, detection rules
- **Operations & Monitoring** — Cloud Logging, Cloud Monitoring, alert pipelines
- **Storage & Databases** — Cloud Storage, Firestore
- **DevOps & Automation** — Pub/Sub event-driven architecture, Cloud Functions
- **Compute & Containers** — Compute Engine, Cloud Run

## IAM

### Team Member Roles

| Member | IAM Role | Justification |
|--------|----------|---------------|
| Moses (Project Leader) | Owner | Full administrative access for infrastructure provisioning |
| Developer | Editor | Can create and modify resources, cannot manage IAM or billing |
| Scribe | Viewer | Read-only access for documentation and observation |

### Service Account

- **Name:** `cloudhoney-app`
- **Purpose:** Application-level authentication (no personal credentials in code)
- **Roles granted:**
  - Logs Writer — honeypot writes to Cloud Logging
  - Storage Object Admin — writes to Cloud Storage bucket
  - Pub/Sub Publisher — Cloud Functions publish alert messages
  - Cloud Datastore User — read/write access to Firestore
  - Secret Manager Secret Accessor — read-only access to stored secrets

### Security Decisions

- Service account follows least-privilege: only the specific roles needed for each service
- No service account key files generated; VM uses attached service account identity
- SendGrid API key stored in Secret Manager, never in source code or environment variables
- Budget alert set at $10 to prevent billing overrun
