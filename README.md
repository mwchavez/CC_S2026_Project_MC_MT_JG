# CloudHoney — GCP-Based Financial Sector Honeypot & Security Event Monitoring Platform
**CIS 4355 – Cloud Computing | Spring 2026**  
**Faculty:** Dr. Parra  
**Team:** Moses (Project Leader) | Marissa Turner (Developer) | Juliana Garza (Scribe)

---

## 📌 Project Overview

**CloudHoney** is a cloud-native honeypot and security event monitoring platform deployed on **Google Cloud Platform (GCP)**, purpose-built to simulate a financial institution's internet-facing infrastructure. Financial institutions experience up to 300 times more cyberattacks than organizations in other sectors — making them the ideal context for a realistic, high-stakes security pipeline.

CloudHoney lures simulated attack traffic toward decoy banking endpoints, ingests and stores the resulting log data, processes events through a fully automated serverless alert pipeline, and presents findings on a real-time visualization dashboard.

> **In plain terms:** a honeypot is a fake system designed to look like a real target — a bank login page, a wire transfer form, a payment API. Attackers waste time on it while we silently log everything they do. CloudHoney builds that trap in the cloud, automates the attack simulation, and turns the captured data into actionable security alerts.

---

## 🏗️ System Architecture

```
       [Cloud Scheduler]
             │
             │  Triggers on schedule
             ▼
  Python Traffic Simulator
  (Credential stuffing, wire transfer probing,
   payment API abuse, account takeover recon,
   port scanning)
             │
             │  HTTP requests
             ▼
     Flask Honeypot App
   (GCP Compute Engine — VPC Network)
   Decoy endpoints: /login /transfer
                    /payment /admin /account
   Logs: IP, user agent, timestamp,
         request path, payload
             │
             │  Structured JSON logs
             ▼
      Cloud Logging  ───────────────────────────┐
             │                                  │
             ▼                                  ▼
     Cloud Storage (GCS)               Cloud Functions
   (Long-term log retention,        (Serverless processing:
    partitioned by date/type)        evaluate detection rules,
                                      write to Firestore)
                                              │
                                 ┌────────────┴────────────┐
                                 ▼                         ▼
                            Firestore               Pub/Sub Alert
                       (Classified event         Notification Topic
                            store)                      │
                                 │                      ▼
                                 └──────►   Visualization Dashboard
                                            (Cloud Run) + Email Alert
                                              (SendGrid via Secret Manager)
```

---

## ☁️ GCP Services (12)

| Role | GCP Service | AWS Equivalent |
|---|---|---|
| Honeypot VM hosting | Compute Engine | EC2 |
| Network isolation & firewall | VPC Network | VPC |
| Log ingestion | Cloud Logging | CloudWatch Logs |
| Object storage | Cloud Storage (GCS) | S3 |
| Serverless processing | Cloud Functions | Lambda |
| Messaging & alerting | Pub/Sub | SNS |
| Real-time event database | Firestore | DynamoDB |
| Credential vault | Secret Manager | Secrets Manager |
| Dashboard hosting | Cloud Run | App Runner |
| Monitoring & metrics | Cloud Monitoring | CloudWatch |
| Access control | Cloud IAM | IAM |
| Attack automation | Cloud Scheduler | EventBridge Scheduler |

---

## 🧱 System Layers Explained

CloudHoney is organized into five logical layers. Each layer handles one responsibility and passes its output to the next.

### Layer 1 — Automation & Traffic Generation
**Cloud Scheduler** triggers the Python attack simulator on a configurable schedule — no manual intervention required. The simulator generates realistic financial sector attack patterns and fires them at the honeypot, including credential stuffing, wire transfer probing, payment API abuse, account takeover recon, and port scanning.

### Layer 2 — Honeypot Endpoint
A lightweight **Flask web application** running on a GCP Compute Engine VM inside a custom **VPC Network**. It exposes decoy banking pages that don't actually do anything — but log every single request in structured JSON and forward it to Cloud Logging. The VM operates with a least-privilege Service Account and VPC firewall rules restricting unexpected inbound traffic.

### Layer 3 — Log Ingestion & Storage
**Cloud Logging** receives all honeypot event data and routes it to **Cloud Storage (GCS)** for long-term retention. Logs are stored in structured JSON format, partitioned by date and event type, making them queryable for both real-time alerting and historical analysis.

### Layer 4 — Processing, Detection & Alerting
**Cloud Functions** subscribe to new log events via **Pub/Sub**, evaluate each event against financial sector detection rules, write every classified event to **Firestore**, and publish an alert when a rule fires. Credentials are retrieved at runtime from **Secret Manager** — never hardcoded. Alerts are delivered via email through SendGrid.

### Layer 5 — Visualization Dashboard
A containerized web dashboard deployed on **Cloud Run** reads classified event data directly from Firestore and displays live attack counts, attack type breakdowns, and active alert states. Because Cloud Scheduler automates the simulation, the dashboard updates in real time during the live demo without any manual input.

---

## 🎯 Detection Rules

| Rule | Condition | Alert Level |
|---|---|---|
| Credential stuffing | > 10 failed login attempts from same IP within 60 seconds | High |
| Wire fraud probe | Request to `/transfer` or `/payment` with manipulated routing/account patterns | High |
| SQL injection | Known injection strings present in any request payload | High |
| Port scan | > 8 distinct paths probed by same IP within 30 seconds | Medium |
| Account takeover recon | Repeated token or session endpoint probing | Medium |

> Detection rules are informed by **PCI DSS** and **GLBA** compliance frameworks.

---

## 📁 Repository Structure

```
/honeypot        → Flask honeypot application (banking decoy endpoints)
/traffic-gen     → Python attack traffic simulator
/functions       → Cloud Functions source code
/dashboard       → Visualization dashboard (Cloud Run)
/infra           → GCP setup scripts and configurations
/docs            → Architecture docs and references
```

---

## ✅ Current Progress

- [x] Project proposal completed and approved
- [x] GitHub repository initialized with milestone structure
- [x] GitHub Project board with issues across 5 milestones created
- [x] GCP project, VPC Network, and IAM setup
- [ ] Compute Engine VM provisioned inside VPC
- [ ] Flask honeypot application deployed (banking endpoints)
- [ ] Cloud Logging integration
- [ ] Cloud Storage pipeline configured
- [ ] Traffic generator v1 (port scan + credential stuffing)
- [ ] Cloud Functions processing logic + Firestore integration
- [ ] Pub/Sub alert pipeline + Secret Manager setup
- [ ] Traffic generator v2 (wire transfer probing, payment API abuse, account takeover recon)
- [ ] Cloud Scheduler automation
- [ ] Visualization dashboard (Cloud Run)

---

## 📊 Evaluation Metrics

| Metric | Target |
|---|---|
| Detection accuracy | ≥ 90% of simulated attack events correctly flagged |
| Alert latency | < 10 seconds from event generation to alert delivery |
| False positive rate | < 5% of benign requests incorrectly classified |
| Automation reliability | Consistent Cloud Scheduler execution across simulation runs |
| Pipeline reliability | Consistent log delivery during sustained traffic generation |
| Dashboard completeness | All five attack types, alert states, and historical trends displayed |

---

## ⚠️ Risks & Mitigations

| Risk | Mitigation |
|---|---|
| GCP service unfamiliarity | Map GCP services to known AWS equivalents; use GCP free tier and documentation from Week 1 |
| Financial attack patterns too generic | Reference OWASP Top 10 and FFIEC guidance; refine simulator payloads iteratively |
| GCP billing overrun | Set billing alerts and budget caps from Day 1; use e2-micro VM and free-tier services |
| Cloud Scheduler misconfiguration | Cap frequency to once per hour during development; monitor Cloud Logging volume daily |
| Team coordination gaps | Weekly check-ins, GitHub Project board, and clear milestone ownership per role |
| Dashboard complexity underestimated | Build minimum viable version first (Cloud Monitoring); upgrade to custom Cloud Run UI only if time allows |

---

## 🔗 Related Resources

- [Project Wiki](https://github.com/mwchavez/CC_S2026_Project_MC_MT_JG/wiki) — Full technical report, architecture decisions, and results
- [GitHub Project Board](https://github.com/users/mwchavez/projects/7) — Milestone tracking and task assignments
- [CloudHoney Proposal](./docs/CloudHoney_Proposal.md) — Full project proposal document
- [Companion Project: Leak Detection System](https://github.com/mwchavez/cc-practicum_S2026) — AWS-based IoT pipeline (CSEC 4390)

---

*Spring 2026 — Cloud Computing | CIS 4355*
