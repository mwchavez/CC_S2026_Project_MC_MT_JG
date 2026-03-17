# CloudHoney — GCP-Based Honeypot & Security Event Monitoring Platform
**CIS 4355 – Cloud Computing | Spring 2026**  
**Faculty:** Dr. Parra  
**Team:** Moses (Project Leader) | Marissa Turner (Developer) | Juliana Garza (Scribe)

---

## 📌 Project Overview

**CloudHoney** is a cloud-native honeypot and security event monitoring platform deployed on **Google Cloud Platform (GCP)**. It lures simulated attack traffic toward a decoy web endpoint, ingests and stores the resulting log data, processes events through a serverless alert pipeline, and presents findings on a real-time visualization dashboard.

> **In plain terms:** a honeypot is a fake system designed to look like a real target (a login page, an admin panel, a database). Attackers waste time on it while we silently log everything they do. CloudHoney builds that trap in the cloud and turns the captured data into actionable security alerts.

The project also serves as a **cross-platform study** in cloud architecture. Its pipeline structure intentionally mirrors the AWS-based IoT pipeline built in a companion senior design project — demonstrating that well-designed cloud architectures are transferable across providers and problem domains.

---

## 🏗️ System Architecture

```
Python Traffic Simulator
(Simulates port scans, brute force, SQL injection)
        │
        │  HTTP requests
        ▼
  Flask Honeypot App
  (GCP Compute Engine VM)
  Logs: IP, user agent, timestamp,
        request path, payload
        │
        │  Structured JSON logs
        ▼
   Cloud Logging  ──────────────────────────────┐
        │                                       │
        ▼                                       ▼
  Cloud Storage (GCS)                     Cloud Functions
  (Long-term log retention,           (Serverless processing:
   partitioned by date/type)           evaluate detection rules)
                                               │
                                  ┌────────────┴────────────┐
                                  ▼                         ▼
                             Pub/Sub Alert             Pub/Sub Fan-out
                             Notification           (Email alert / Dashboard flag)
                                                          │
                                                          ▼
                                                  Visualization Dashboard
                                              (Cloud Monitoring or Cloud Run)
```

### GCP Services vs. AWS Equivalents

> If you're more familiar with AWS (or have seen the companion leak detection project), this table maps each GCP service to what you may already know:

| Role | GCP Service Used | AWS Equivalent |
|---|---|---|
| Honeypot hosting | **Compute Engine (VM)** | EC2 |
| Log ingestion | **Cloud Logging** | CloudWatch Logs |
| Object storage | **Cloud Storage (GCS)** | S3 |
| Serverless processing | **Cloud Functions** | Lambda |
| Messaging / alerting | **Pub/Sub** | SNS |
| Dashboard / monitoring | **Cloud Monitoring or Cloud Run** | CloudWatch Dashboards |
| Access control | **Cloud IAM** | IAM |

---

## 🧱 System Layers Explained

CloudHoney is organized into five logical layers. Each layer handles one responsibility and passes its output to the next.

### Layer 1 — Traffic Generation
A Python script generates realistic malicious request patterns on demand — including **port scans**, **brute force login sequences**, and **SQL injection payloads** — and fires them at the honeypot endpoint. This is used instead of real internet-exposed attack traffic to keep the demo safe, legal, and reproducible in an academic setting.

### Layer 2 — Honeypot Endpoint
A lightweight **Flask web application** running on a GCP Compute Engine virtual machine. It exposes fake-looking pages (SSH login, admin panel, database query form) that don't actually do anything — but log every single request in detail. All logs are forwarded to Cloud Logging.

### Layer 3 — Log Ingestion & Storage
**Cloud Logging** receives all honeypot event data and routes it to **Cloud Storage (GCS)** for long-term retention. Logs are stored in structured JSON format, partitioned by date and event type, making them queryable for both real-time alerting and historical analysis.

### Layer 4 — Processing & Alerting
**Cloud Functions** subscribe to new log events via **Pub/Sub**, evaluate each event against configurable detection rules (e.g., more than 10 failed logins in 60 seconds, or the presence of SQL injection strings), and publish an alert when a rule is triggered. Alerts are delivered via email or dashboard flag.

### Layer 5 — Visualization Dashboard
A web dashboard built with **Cloud Monitoring** (or a custom **Cloud Run** app) displays live event counts, attack type breakdowns, simulated source geography, and active alert states. This is the primary artifact shown during the live demonstration.

---

## 🎯 Detection Rules

| Rule | Condition | Alert Level |
|---|---|---|
| Brute force | > 10 failed login attempts within 60 seconds | High |
| SQL injection | Known injection strings in request payload | High |
| Port scan | > 20 distinct path requests from single IP in 30 seconds | Medium |
| Repeated probe | Same IP hitting multiple fake endpoints | Medium |

---

## 📁 Repository Structure

```
cloudhoney/
├── traffic-generator/
│   ├── simulator.py           # Main traffic simulation script
│   ├── payloads/
│   │   ├── port_scan.py       # Port scan simulation module
│   │   ├── brute_force.py     # Brute force login sequence module
│   │   └── sql_injection.py   # SQL injection payload module
│   └── requirements.txt
│
├── honeypot/
│   ├── app.py                 # Flask honeypot application
│   ├── templates/             # Fake login/admin HTML pages
│   └── requirements.txt
│
├── cloud-functions/
│   ├── event_processor/
│   │   ├── main.py            # Cloud Function: detection rules & alert logic
│   │   └── requirements.txt
│   └── deploy.sh              # Deployment script
│
├── infrastructure/
│   ├── compute-engine/
│   │   └── startup-script.sh  # VM provisioning and Flask app setup
│   ├── pubsub/
│   │   └── topics.json        # Pub/Sub topic configuration
│   └── iam/
│       └── roles.json         # IAM role and permission definitions
│
├── dashboard/
│   └── [dashboard source or Cloud Monitoring config]
│
├── docs/
│   └── architecture.md        # Detailed architecture decision log
│
└── README.md
```

---

## ✅ Current Progress

- [x] Project proposal completed and approved
- [x] GitHub repository initialized with milestone structure
- [x] GitHub Project board with issues across 5 milestones created
- [ ] GCP account and IAM setup
- [ ] Compute Engine VM provisioned
- [ ] Flask honeypot application deployed
- [ ] Cloud Logging integration
- [ ] Cloud Storage pipeline configured
- [ ] Traffic generator v1 (port scan)
- [ ] Cloud Functions processing logic
- [ ] Pub/Sub alert pipeline
- [ ] Brute force + injection simulation added
- [ ] Visualization dashboard

---

## 📊 Evaluation Metrics

| Metric | Target |
|---|---|
| Detection accuracy | ≥ 90% of simulated attack events correctly flagged |
| Alert latency | < 10 seconds from event generation to alert delivery |
| False positive rate | < 5% of benign requests incorrectly classified |
| Pipeline reliability | Consistent log delivery during sustained traffic generation |
| Dashboard completeness | Event types, alert states, and historical trends all displayed |

---

## ⚠️ Risks & Mitigations

| Risk | Mitigation |
|---|---|
| GCP service unfamiliarity | Map GCP services to known AWS equivalents; use GCP free tier and documentation from Week 1 |
| Unrealistic attack patterns | Research OWASP attack signatures; refine payloads iteratively based on detection layer feedback |
| GCP billing overrun | Set billing alerts and budget caps from Day 1; use smallest viable VM and free-tier services |
| Team coordination gaps | Weekly check-ins, GitHub Project board, and clear milestone ownership per role |
| Dashboard complexity underestimated | Build minimum viable version first (Cloud Monitoring built-in); upgrade to custom UI only if time allows |

---

## 🔗 Related Resources

- [Project Wiki](../../wiki) — Full technical report, architecture decisions, and results
- [GitHub Project Board](../../projects) — Milestone tracking and task assignments
- [CloudHoney Proposal](./docs/CloudHoney_Proposal.docx) — Original project proposal document
- [Companion Project: Leak Detection System](../practicum-leak-detection/) — AWS-based IoT pipeline (CSEC 4390)

---

*Spring 2026 — Cloud Computing | CIS 4355*
