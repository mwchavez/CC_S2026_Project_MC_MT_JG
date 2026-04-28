# CloudHoney — GCP-Based Financial Sector Honeypot & Security Event Monitoring Platform
**CIS 4355 – Cloud Computing | Spring 2026**  
**Faculty:** Dr. Parra  
**Team:** Moses (Project Leader) | Marissa Turner (Developer) | Juliana Garza (Scribe)

---

## Project Overview

**CloudHoney** is a cloud-native honeypot and security event monitoring platform deployed on **Google Cloud Platform (GCP)**, purpose-built to simulate a financial institution's internet-facing infrastructure. Financial institutions experience up to 300 times more cyberattacks than organizations in other sectors — making them the ideal context for a realistic, high-stakes security pipeline.

CloudHoney lures simulated attack traffic toward decoy banking endpoints, ingests and stores the resulting log data, processes events through a fully automated serverless alert pipeline, and presents findings on a real-time visualization dashboard.

> **In plain terms:** a honeypot is a fake system designed to look like a real target — a bank login page, a wire transfer form, a payment API. Attackers waste time on it while we silently log everything they do. CloudHoney builds that trap in the cloud, automates the attack simulation, and turns the captured data into actionable security alerts.

---

## Team Roles & Responsibilities

Per the CIS 4355 Kickoff Guide, each team member leads a distinct area while contributing across all aspects of the project. Roles are mapped to the Guide's recommended structure: Project Lead / Cloud Architect, Developer / Engineer, and Security & Documentation Lead.

**Moses — Project Leader / Cloud Architect**
Owns the overall system architecture and all GCP infrastructure decisions. Responsible for GCP project setup, VPC and IAM configuration, Compute Engine VM provisioning, Cloud Functions implementation, Pub/Sub alert pipeline, Firestore integration, Secret Manager configuration, Cloud Scheduler automation, Cloud Monitoring setup, and final system integration. Primary point of contact for all technical decisions, demo preparation, and instructor communication. Manages the GitHub Project board, tracks sprint progress, and ensures milestone deadlines are met.

**Marissa Turner — Developer / Cloud Engineer**
Owns all application-layer code across the project. Responsible for the Flask honeypot application with financial sector decoy endpoints, the full Python traffic simulator (all five attack scenarios: credential stuffing, wire transfer probing, payment API abuse, account takeover recon, and port scanning), and collaboration on the Cloud Run visualization dashboard. Works with the Project Leader on integration testing, troubleshooting, deployment, and live demo execution.

**Juliana Garza — Scribe / Security & Documentation Lead**
Owns the project's written deliverables and security documentation. Responsible for authoring and maintaining the GitHub Wiki as the formal project report, including the GCP Services Inventory page with PaaS/SaaS core service explanations. Leads research on financial sector threat patterns, PCI DSS and GLBA compliance requirements, and honeypot methodologies. Documents and reviews all security configurations — firewall rule justifications, IAM role decisions, Secret Manager access policies, and VPC isolation rationale — ensuring each decision is mapped to relevant compliance frameworks in the Wiki. Maintains meeting notes, the Implementation Log, and ensures all GitHub Issues are properly described and closed.

---

## Cloud Computing Domains Covered

CloudHoney integrates **five** of the seven core cloud computing domains defined in the CIS 4355 curriculum, well above the three-domain minimum.

| Domain | How CloudHoney Addresses It |
|---|---|
| **Cloud Architecture & Design** | Custom VPC Network with isolated subnets, deny-all-ingress firewall posture, multi-layer event pipeline designed for separation of concerns, and a six-layer architecture spanning automation through visualization. |
| **Compute & Containers** | Compute Engine VM hosts the Flask honeypot inside the VPC. Cloud Functions provides serverless event classification. Cloud Run hosts the containerized visualization dashboard with scale-to-zero configuration. |
| **Storage & Databases** | Cloud Storage provides durable, date-partitioned log retention mirroring PCI DSS audit trail requirements. Firestore serves as the real-time NoSQL event store powering the dashboard. |
| **Security & Identity** | Cloud IAM enforces least-privilege roles across team members and service accounts. Secret Manager vaults all credentials at runtime. VPC firewall rules restrict inbound traffic to explicitly allow-listed sources. Detection rules are modeled on PCI DSS and GLBA compliance frameworks. |
| **Operations & Monitoring** | Cloud Logging is the centralized ingestion point for all honeypot events. Cloud Monitoring tracks pipeline health — VM uptime, Cloud Function execution metrics, Pub/Sub throughput, and Firestore read/write rates — with alerting policies for operational anomalies. |
| **DevOps & Automation** | Cloud Scheduler triggers the traffic simulator on a recurring schedule for hands-free pipeline testing. Pub/Sub provides event-driven messaging between the logging, processing, and alerting layers. GitHub Projects tracks all sprint work with agile issue management. |

---

## System Architecture

> **Note:** A formal cloud architecture diagram (created in draw.io) showing VPC boundaries, subnets, firewall rules, data flow, and service relationships is available in [`/docs/architecture_diagram.png`](./docs/architecture_diagram.png) and on the [Architecture Wiki page](https://github.com/mwchavez/CC_S2026_Project_MC_MT_JG/wiki/Architecture).

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

## GCP Services Inventory (12 Services)

### Service Table

| # | Role | GCP Service | Model | AWS Equivalent |
|---|---|---|---|---|
| 1 | Honeypot VM hosting | Compute Engine | IaaS | EC2 |
| 2 | Network isolation & firewall | VPC Network | IaaS | VPC |
| 3 | Log ingestion | Cloud Logging | PaaS | CloudWatch Logs |
| 4 | Object storage | Cloud Storage (GCS) | IaaS | S3 |
| 5 | Serverless processing | Cloud Functions | PaaS | Lambda |
| 6 | Messaging & alerting | Pub/Sub | PaaS | SNS |
| 7 | Real-time event database | Firestore | PaaS | DynamoDB |
| 8 | Credential vault | Secret Manager | PaaS | Secrets Manager |
| 9 | Dashboard hosting | Cloud Run | PaaS | App Runner |
| 10 | Monitoring & metrics | Cloud Monitoring | PaaS | CloudWatch |
| 11 | Access control | Cloud IAM | IaaS | IAM |
| 12 | Attack automation | Cloud Scheduler | PaaS | EventBridge Scheduler |

### Underlying Core Services (PaaS → IaaS Mapping)

Per the CIS 4355 Group Project Kickoff Guide, the following explains which core IaaS services underpin each PaaS service used in CloudHoney. This demonstrates our understanding of the full cloud stack — that every managed service ultimately runs on foundational infrastructure that Google operates on our behalf.

| PaaS Service | Underlying Core IaaS Services |
|---|---|
| **Cloud Functions** | Runs on GKE-managed container instances backed by **Compute Engine** VMs. Google provisions, scales, and destroys these containers automatically. Networking is handled through internal **VPC** connectivity. |
| **Cloud Run** | Runs on **GKE** (Google Kubernetes Engine), which itself uses **Compute Engine** VMs. Incoming traffic is routed through **Cloud Load Balancing** over Google's Andromeda virtual network within a **VPC**. |
| **Firestore** | A managed NoSQL database built on Google's **Spanner-derived infrastructure**, using **Compute Engine** for processing and Google's **Colossus distributed file system** for storage. Replication and consistency are handled by Google internally. |
| **Pub/Sub** | A managed messaging service running on Google's globally distributed infrastructure, backed by **Compute Engine** and Google's internal **Borg** orchestration system. Messages are durably stored and replicated across zones. |
| **Cloud Logging** | A managed log management service running on Google's **Borgmaster-orchestrated infrastructure**, using **Compute Engine** for processing and **Colossus** for durable log storage. |
| **Cloud Monitoring** | A managed observability service running on Google's **Borgmaster-orchestrated infrastructure**, backed by **Compute Engine** for metric processing and internal time-series databases for storage. |
| **Cloud Scheduler** | A managed cron service backed by Google's **internal job scheduling system**, running on **Compute Engine** infrastructure. Jobs are durably registered and executed with at-least-once delivery guarantees. |
| **Secret Manager** | A managed secrets service backed by **Cloud KMS** (Key Management Service) for encryption, running on dedicated **HSM (Hardware Security Module)** infrastructure and **Compute Engine** for API serving. |

> **IaaS services** (Compute Engine, VPC Network, Cloud Storage, Cloud IAM) are themselves the foundational layer and do not require further decomposition.

---

## System Layers Explained

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

## Detection Rules

| Rule | Condition | Alert Level |
|---|---|---|
| Credential stuffing | > 10 failed login attempts from same IP within 60 seconds | High |
| Wire fraud probe | Request to `/transfer` or `/payment` with manipulated routing/account patterns | High |
| SQL injection | Known injection strings present in any request payload | High |
| Port scan | > 8 distinct paths probed by same IP within 30 seconds | Medium |
| Account takeover recon | Repeated token or session endpoint probing | Medium |

> Detection rules are informed by **PCI DSS** and **GLBA** compliance frameworks.

---

## Repository Structure

```
/honeypot        → Flask honeypot application (banking decoy endpoints)
/traffic-gen     → Python attack traffic simulator
/functions       → Cloud Functions source code
/dashboard       → Visualization dashboard (Cloud Run)
/infra           → GCP setup scripts and configurations
/docs            → Architecture docs, diagrams, and references
/presentation    → Final presentation slides and demo materials
```

---

## Current Progress

- [x] Project proposal completed and approved
- [x] GitHub repository initialized with milestone structure
- [x] GitHub Project board with issues across 5 milestones created
- [ ] Cloud architecture diagram (draw.io)
- [x] GCP project, VPC Network, and IAM setup
- [x] Compute Engine VM provisioned inside VPC
- [x] Flask honeypot application deployed (banking endpoints)
- [x] Cloud Logging integration
- [x] Cloud Storage pipeline configured
- [x] Traffic generator v1 (port scan + credential stuffing)
- [x] Cloud Functions processing logic + Firestore integration
- [x] Pub/Sub alert pipeline + Secret Manager setup
- [x] Traffic generator v2 (wire transfer probing, payment API abuse, account takeover recon)
- [x] Cloud Scheduler automation
- [x] Visualization dashboard (Cloud Run)
- [ ] GCP Services Inventory Wiki page (PaaS/SaaS core service documentation)

---

## Evaluation Metrics

| Metric | Target |
|---|---|
| Detection accuracy | ≥ 90% of simulated attack events correctly flagged |
| Alert latency | < 10 seconds from event generation to alert delivery |
| False positive rate | < 5% of benign requests incorrectly classified |
| Automation reliability | Consistent Cloud Scheduler execution across simulation runs |
| Pipeline reliability | Consistent log delivery during sustained traffic generation |
| Dashboard completeness | All five attack types, alert states, and historical trends displayed |

---

## Risks & Mitigations

| Risk | Mitigation |
|---|---|
| GCP service unfamiliarity | Map GCP services to known AWS equivalents; use GCP free tier and documentation from Week 1 |
| Financial attack patterns too generic | Reference OWASP Top 10 and FFIEC guidance; refine simulator payloads iteratively |
| GCP billing overrun | Set billing alerts at $1 and $10; use e2-micro VM and free-tier services; cap Cloud Scheduler to 3 jobs |
| Cloud Scheduler misconfiguration | Cap frequency to once per hour during development; monitor Cloud Logging volume daily |
| Team coordination gaps | Weekly check-ins, GitHub Project board, and clear milestone ownership per role |
| Dashboard complexity underestimated | Build minimum viable version first (Cloud Monitoring); upgrade to custom Cloud Run UI only if time allows |

---

## Related Resources

- [Project Wiki](https://github.com/mwchavez/CC_S2026_Project_MC_MT_JG/wiki) — Full technical report, architecture decisions, and results
- [GitHub Project Board](https://github.com/users/mwchavez/projects/7) — Milestone tracking and task assignments
- [CloudHoney Proposal](./docs/CloudHoney_Proposal.md) — Full project proposal document

---

*Spring 2026 — Cloud Computing | CIS 4355*
