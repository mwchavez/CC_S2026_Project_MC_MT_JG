# CloudHoney: A GCP-Based Financial Sector Honeypot & Security Event Monitoring Platform

**CIS 4355 — Cloud Computing | Spring 2026**  
**Moses (Project Leader) | Marissa Turner (Developer) | Juliana Garza (Scribe)**

---

## 1. Problem Statement

Financial institutions experience up to 300 times more cyberattacks than organizations in other sectors, with 65% reporting a ransomware attack in 2024 alone — the highest rate ever recorded. Banks, credit unions, payment processors, and fintech platforms face a constant barrage of credential stuffing attacks, fraudulent wire transfer probes, API abuse, and account takeover attempts — attacks specifically engineered to exploit the authentication flows and customer data interfaces that financial systems expose.

Despite this threat landscape, many organizations lack the early-warning visibility needed to detect reconnaissance activity before it escalates. Traditional perimeter defenses are reactive and fail to capture the behavioral fingerprints of attackers during the initial probing phase — the phase where the most actionable intelligence lives.

This project proposes the development of **CloudHoney**, a cloud-native honeypot and security event monitoring platform deployed on Google Cloud Platform (GCP), purpose-built to simulate a financial institution's internet-facing infrastructure. The system lures simulated attack traffic toward decoy banking endpoints, ingests and stores the resulting log data, processes it through an automated alert pipeline, and presents findings on a real-time visualization dashboard. By targeting financial sector attack patterns specifically — credential stuffing, wire transfer probing, and payment API abuse — CloudHoney demonstrates how cloud-native infrastructure can be applied directly to the most high-stakes cybersecurity operations in the industry.

---

## 2. Project Objectives

- Deploy a lightweight honeypot endpoint on GCP Compute Engine inside a custom VPC Network, simulating an internet-facing financial institution portal
- Simulate financial sector-specific attack patterns including credential stuffing, wire transfer probing, payment API abuse, and account takeover recon
- Build a log ingestion and storage pipeline using GCP Cloud Logging and Cloud Storage
- Implement serverless event processing using Cloud Functions to classify and triage security events against financial threat detection rules
- Automate attack simulation on a recurring schedule using Cloud Scheduler, enabling hands-free pipeline testing
- Configure alerting and notification via Pub/Sub when detection thresholds are exceeded
- Store all classified events in Firestore for fast, real-time dashboard reads
- Secure all credentials and API keys in Secret Manager — never in source code
- Develop a real-time visualization dashboard hosted on Cloud Run surfacing attack patterns, event frequency, and active alert states
- Document all architecture decisions, configurations, and findings in a GitHub Wiki serving as the formal project report

---

## 3. System Overview

CloudHoney consists of five logical layers working in sequence. Each layer is described below with its financial sector context.

### 3.1 Traffic Generation & Automation Layer

Rather than exposing the honeypot to live internet traffic — which introduces legal and operational complexity in an academic setting — CloudHoney uses a purpose-built Python-based traffic simulator. This module generates realistic financial sector attack patterns and fires them at the honeypot endpoint either on demand or on an automated schedule via Cloud Scheduler.

Simulated attack scenarios include:

- **Credential stuffing** — rapid POST requests to the banking login portal using leaked credential lists
- **Wire transfer probing** — probing the transfer API with manipulated account and routing numbers
- **Payment API abuse** — sending malformed or injected payloads to the payment processing endpoint
- **Account takeover recon** — probing session and token endpoints for authentication weaknesses
- **Port scanning** — broad HTTP reconnaissance across all exposed paths

### 3.2 Honeypot Endpoint

A lightweight Flask web application deployed on a GCP Compute Engine VM inside a custom VPC Network acts as the decoy financial institution. The honeypot exposes endpoints that mirror real banking infrastructure:

| Endpoint | Description |
|---|---|
| `/login` | Fake online banking portal login page |
| `/transfer` | Fake wire transfer submission interface |
| `/payment` | Fake payment API endpoint |
| `/admin` | Fake back-office administrative panel |
| `/account` | Fake customer account lookup interface |

Every incoming request is captured and forwarded to GCP Cloud Logging as structured JSON. No real authentication or financial operations are performed. Firewall rules within the VPC restrict inbound traffic to only expected sources, and the VM operates with a least-privilege Service Account attached.

### 3.3 Log Ingestion and Storage

Cloud Logging receives all honeypot event data and routes it to Cloud Storage for long-term retention. Logs are stored in structured JSON format, partitioned by date and event type, making them queryable for both real-time alerting and historical analysis. This layer mirrors the function of AWS CloudWatch and S3 in a traditional pipeline.

### 3.4 Processing, Detection, and Alerting

Cloud Functions serve as the serverless processing layer. A function subscribes to new log entries via Pub/Sub, evaluates each event against financial sector detection rules, writes every classified event to Firestore, and publishes an alert to a Pub/Sub notification topic when a rule fires.

Detection rules are modeled on financial threat intelligence and relevant compliance frameworks (PCI DSS, GLBA):

- More than 10 failed login attempts from the same IP within 60 seconds → **credential stuffing alert**
- Any request to `/transfer` or `/payment` containing manipulated routing/account number patterns → **wire fraud probe alert**
- Presence of SQL injection strings in any payload → **injection attack alert**
- More than 8 distinct paths probed by the same IP within 30 seconds → **port scan alert**
- Repeated token or session endpoint probing → **account takeover recon alert**

### 3.5 Visualization Dashboard

A containerized web dashboard deployed on Cloud Run reads classified event data directly from Firestore and displays live attack counts, attack type breakdowns, simulated source metadata, and active alert states. This is the primary artifact shown during the live demonstration. Because Cloud Scheduler automates the attack simulation, the dashboard can be shown updating in real time without any manual intervention.

---

## 4. Architecture Overview

```
[Cloud Scheduler]
      │
      ▼
[Python Traffic Simulator] ──────────────────────────────────────┐
                                                                  │
                                                                  ▼
                                                    [Honeypot Flask App]
                                                    [Compute Engine — VPC]
                                                                  │
                                                                  ▼
                                                         [Cloud Logging]
                                                                  │
                                              ┌───────────────────┤
                                              ▼                   ▼
                                      [Cloud Storage]         [Pub/Sub]
                                                                  │
                                                                  ▼
                                                       [Cloud Functions]
                                                                  │
                                              ┌───────────────────┤
                                              ▼                   ▼
                                         [Firestore]     [Pub/Sub Alerts]
                                              │                   │
                                              ▼                   ▼
                                       [Cloud Run]         [Email via
                                       [Dashboard]          SendGrid]
```

---

## 5. GCP Services and Technology Stack

> **12 GCP Services Total**

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
| Dashboard & metrics | Cloud Monitoring | CloudWatch Dashboards |
| IAM & access control | Cloud IAM | IAM |
| Attack automation | Cloud Scheduler | EventBridge Scheduler |

---

## 6. Team Roles and Responsibilities

### Moses — Project Leader
Overall system architecture and GCP infrastructure design. GCP project setup, VPC and IAM configuration, Compute Engine VM provisioning, Cloud Functions implementation, Pub/Sub alert pipeline, Firestore integration, Secret Manager configuration, Cloud Scheduler automation, and final system integration. Primary point of contact for all technical decisions and demo preparation.

### TBD — Developer
Python traffic simulator development — credential stuffing, wire transfer probing, payment API abuse, account takeover recon, and port scan scenarios. Honeypot Flask application development with financial sector decoy endpoints. Collaboration with Project Leader on integration testing, troubleshooting, and live demo execution.

### TBD — Scribe
Research on financial sector threat patterns, PCI DSS/GLBA compliance requirements, honeypot methodologies, and GCP service documentation. Authoring and maintaining the GitHub Wiki as the project's formal report. Meeting notes, progress documentation, and ensuring all GitHub issues are properly described and closed.

---

## 7. Expected Deliverables

- GitHub Repository containing all source code, infrastructure scripts, and configuration files
- GitHub Project board with structured issues tracking all milestones and task assignments
- GitHub Wiki serving as the formal project report — covering problem statement, architecture, implementation, results, and compliance considerations
- Deployed honeypot endpoint running on GCP Compute Engine inside a custom VPC, simulating a financial institution portal
- Python traffic simulator capable of executing at least five distinct financial sector attack scenarios
- Cloud Scheduler configuration automating attack simulation on a recurring schedule
- Cloud Functions-based processing pipeline with financial threat detection rules
- Pub/Sub alert delivery when detection thresholds are breached
- Firestore event store powering real-time dashboard reads
- Secret Manager integration securing all credentials out of source code
- Real-time visualization dashboard on Cloud Run showing live event data and alert states
- Live demonstration showing a fully automated attack cycle triggering detection and alerting end-to-end

---

## 8. Project Timeline

| Weeks | Phase and Activities |
|---|---|
| **1–2** | Requirements definition, GCP project and VPC setup, IAM configuration, architecture finalization, GitHub repo and project board initialization, financial sector threat research |
| **3–4** | Honeypot Flask application development (banking endpoints), Compute Engine VM provisioning inside VPC, initial deployment and connectivity testing |
| **5–6** | Cloud Logging integration, Cloud Storage pipeline setup, traffic simulator v1 (port scan + credential stuffing) |
| **7–8** | Cloud Functions processing logic, Pub/Sub alert pipeline, traffic simulator v2 (wire transfer probing, payment API abuse, account takeover recon) |
| **9–10** | Cloud Scheduler automation, detection rule tuning, Firestore integration, Secret Manager setup, dashboard prototype |
| **11–12** | System integration testing, end-to-end automated demo dry run, performance and reliability evaluation |
| **13–14** | GitHub Wiki report writing (including compliance framing), system refinement, final demo preparation |
| **15** | Final presentation, live automated system demonstration, project submission |

---

## 9. Evaluation Metrics

- **Detection accuracy** — percentage of simulated financial attack events correctly identified and flagged
- **Alert latency** — time from attack event generation to alert delivery, targeting under 10 seconds
- **False positive rate** — frequency of benign requests incorrectly classified as attacks
- **Automation reliability** — Cloud Scheduler consistency in triggering simulation runs
- **Pipeline reliability** — system uptime and log delivery consistency during sustained traffic generation
- **Dashboard completeness** — coverage of all five attack types, alert states, and historical trends

---

## 10. Risks and Mitigation

| Risk | Mitigation |
|---|---|
| GCP service unfamiliarity | Leverage existing AWS architectural knowledge as a reference map; use GCP free tier and documentation extensively; begin infrastructure setup in Week 1 |
| Financial attack patterns too generic | Reference OWASP Top 10, FFIEC guidance, and known FinServ breach case studies to ground simulator payloads in real attacker behavior |
| GCP billing overrun | Set billing alerts and budget caps from Day 1; use e2-micro VM and free-tier eligible services; Cloud Scheduler keeps simulation controlled |
| Team coordination gaps | Weekly check-ins, GitHub Project board with assigned issues, and clear milestone ownership per team role |
| Dashboard complexity underestimated | Scope to minimum viable version first (Cloud Monitoring built-in); upgrade to custom Cloud Run UI only if time allows |
| Cloud Scheduler misconfiguration causing runaway costs | Cap scheduler frequency to no more than once per hour during development; monitor Cloud Logging volume daily |

---

## 11. Conclusion

CloudHoney represents a purposeful intersection of cloud computing, cybersecurity, and financial sector threat intelligence — three disciplines directly relevant to the Computer Information Systems program and to the real-world cloud security industry.

By deploying a honeypot that specifically mimics financial institution infrastructure and building a fully automated GCP security pipeline around it, the team will gain direct, hands-on experience with cloud-native infrastructure, serverless computing, event-driven architecture, automated scheduling, secrets management, and real-time data visualization in the highest-stakes cybersecurity context there is.

The project deliberately mirrors the architectural patterns established in the team lead's senior design practicum work on AWS, demonstrating that well-designed cloud security pipelines are generalizable across providers and problem domains. The financial sector focus elevates the project from a generic academic exercise to a credible, demonstrable cloud security platform tied directly to one of the most active threat landscapes in the industry.
