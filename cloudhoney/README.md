# CloudHoney

**A GCP-Based Honeypot & Security Event Monitoring Platform**

CIS 4355 — Cloud Computing | Spring 2026

---

## Overview

CloudHoney is a cloud-native honeypot and security event monitoring platform deployed on Google Cloud Platform (GCP). The system lures simulated attack traffic toward a decoy endpoint, ingests and stores the resulting log data, processes it through an alert pipeline, and presents findings on a real-time visualization dashboard.

By combining deception-based detection with cloud-native data engineering, CloudHoney demonstrates how modern cloud infrastructure can be applied directly to cybersecurity operations.

## Architecture

```
Traffic Generator  →  Honeypot Endpoint  →  Log Ingestion & Storage  →  Alerts & Dashboard
   (Python)          (Compute Engine)      (Cloud Logging / GCS)       (Cloud Run + Firestore)
```

## GCP Services (10)

| Role | GCP Service | AWS Equivalent |
|------|-------------|----------------|
| Honeypot hosting | Compute Engine | EC2 |
| Log ingestion | Cloud Logging | CloudWatch Logs |
| Object storage | Cloud Storage (GCS) | S3 |
| Serverless processing | Cloud Functions | Lambda |
| Messaging / alerting | Pub/Sub | SNS |
| Dashboard hosting | Cloud Run | ECS / App Runner |
| Real-time data store | Firestore | DynamoDB |
| Secrets management | Secret Manager | Secrets Manager |
| Monitoring | Cloud Monitoring | CloudWatch |
| Access control | Cloud IAM | IAM |

## Repository Structure

```
/honeypot        → Flask honeypot application
/traffic-gen     → Python attack traffic simulator
/functions       → Cloud Functions source code
/dashboard       → Visualization dashboard (Cloud Run)
/infra           → GCP setup scripts and configurations
/docs            → Architecture docs and references
```

## Team

| Name | Role |
|------|------|
| Moses | Project Leader — Architecture, GCP infrastructure, Cloud Functions, Pub/Sub, system integration |
| TBD | Developer — Traffic generator, Flask honeypot, integration testing |
| TBD | Scribe — Research, GitHub Wiki report, documentation |

## Quick Links

- [Project Board](link-to-project-board)
- [GitHub Wiki (Project Report)](link-to-wiki)
- [Architecture Diagram](link-to-diagram)
