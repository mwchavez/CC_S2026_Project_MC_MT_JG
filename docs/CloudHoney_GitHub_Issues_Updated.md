# CloudHoney — GitHub Issues (Full Sprint Plan)

> **Project:** CloudHoney: A GCP-Based Financial Sector Honeypot & Security Event Monitoring Platform
> **Class:** CIS 4355 — Cloud Computing | Spring 2026
> **Team:** Moses (Project Leader) | Marissa Turner (Developer) | Juliana Garza (Scribe)
> **GCP Services (12):** Compute Engine · VPC Network · Cloud Logging · Cloud Storage · Cloud Functions · Pub/Sub · Cloud Monitoring · Cloud IAM · Cloud Run · Secret Manager · Firestore · Cloud Scheduler

---

## Label Definitions

| Label | Description |
|---|---|
| `infrastructure` | Work involving GCP cloud services being provisioned or configured — creating VMs, VPC networks, storage buckets, Pub/Sub topics, and anything that lives in the GCP Console rather than in code. If you're clicking around in GCP or running `gcloud` commands to set something up, it's infrastructure. |
| `backend` | Code that runs on the server side and isn't directly seen by a user. For CloudHoney this covers the Flask honeypot app, the Python traffic generator, Cloud Functions processing logic, and Firestore writes. Basically anything Python that handles data, logic, or communication between services. |
| `frontend` | Code that produces a visual interface for a human to look at. In CloudHoney's case this is the visualization dashboard hosted on Cloud Run. |
| `devops` | Work that keeps the project organized and running smoothly rather than building features directly. This includes setting up the GitHub repo, project board, deployment scripts, billing alerts, and anything that bridges development work with the cloud environment. |
| `documentation` | Writing, research, and record-keeping tasks. This covers GitHub Wiki pages, README files, architecture decision notes, meeting logs, and the final project report. The Scribe role will carry most of these, but any issue that produces written artifacts rather than code or cloud resources gets this label. |
| `security` | Work specifically related to securing the CloudHoney platform itself — firewall rules, IAM least-privilege enforcement, Secret Manager usage, VPC isolation, and service account hardening. Distinct from detection rules (which are feature logic), this label covers the security posture of the project's own infrastructure. |
| `compliance` | Research, documentation, and design decisions tied to financial sector regulatory frameworks — PCI DSS, GLBA, and FFIEC guidance. Includes mapping detection rules to compliance requirements and documenting how CloudHoney's architecture aligns with financial institution security standards. |

---

## Agile Planning Fields

Per the CIS 4355 Kickoff Guide (Appendix C), every issue includes the following planning attributes to support sprint capacity planning and progress tracking:

| Field | Scale | Description |
|---|---|---|
| **Priority** | P0 – P3 | P0 = critical/blocking, P1 = high, P2 = medium, P3 = low |
| **Size** | XS – XL | Relative effort: XS (quick fix), S (few hours), M (1–2 days), L (3–5 days), XL (multi-day complex) |
| **Story Points** | 1, 2, 3, 5, 8 | Fibonacci scale for sprint capacity planning |

---

## Issue #1 — GCP Project Setup, VPC Network & IAM Configuration
**Label:** `infrastructure` `devops` `security`
**Milestone:** Week 1–2
**Assignee:** Moses (Project Leader)
**Priority:** P0 (Critical — blocks all other work)
**Size:** L
**Story Points:** 5

### Description
Establish the foundational GCP environment that all other work depends on — including the project, billing controls, a custom VPC Network for network isolation, and IAM roles for all team members. This is the very first task and must be completed before any services can be provisioned.

### Background
GCP (Google Cloud Platform) is organized around **projects** — think of a project as a container that holds all your cloud resources, billing, and access controls in one place. IAM (Identity and Access Management) is GCP's system for controlling *who* can do *what* within that project.

A **VPC (Virtual Private Cloud) Network** is a logically isolated network within GCP. Think of it like your own private section of Google's global network — you control the IP ranges, firewall rules, and which resources can talk to each other. In AWS terms, this is equivalent to an AWS VPC. CloudHoney's honeypot VM will live inside this VPC, with firewall rules restricting inbound traffic to only expected sources. This network isolation is a fundamental security requirement for any financial sector application.

Setting this up correctly from day one prevents billing surprises, security gaps, and network misconfigurations later.

### Tasks
- [ ] Create a new GCP project named `cloudhoney-sp26` (or similar)
- [ ] Enable billing and set a **budget alert** at $10 and a hard cap appropriate for the free tier
- [ ] Create a **custom VPC Network** named `cloudhoney-vpc`:
  - Create a subnet in `us-central1` (or closest to team) with a defined CIDR range (e.g., `10.0.1.0/24`)
  - Disable the default network or ensure CloudHoney resources use only the custom VPC
  - Configure basic **firewall rules**: deny all ingress by default, allow SSH (port 22) from team IPs only, allow HTTP on port 5000 from traffic generator source only
- [ ] Create a dedicated **Service Account** for CloudHoney application services (do not use personal credentials in code)
  - Name: `cloudhoney-app-sa`
  - Grant only the minimum roles needed: `Logs Writer`, `Firestore User`, `Pub/Sub Publisher`
- [ ] Assign only the minimum necessary IAM roles to each team member:
  - Moses (Project Leader): `Owner`
  - Marissa (Developer): `Editor`
  - Juliana (Scribe): `Viewer`
- [ ] Enable all 12 required GCP APIs: Compute Engine, VPC Network (enabled by default with Compute), Cloud Logging, Cloud Storage, Cloud Functions, Pub/Sub, Cloud Monitoring, Cloud Run, Secret Manager, Firestore, Cloud Scheduler, Cloud IAM
- [ ] Document all IAM decisions and VPC design in the GitHub Wiki under `Architecture > IAM` and `Architecture > Networking`

### Acceptance Criteria
- All three team members can log into GCP Console with appropriate permissions
- Budget alerts are active and visible in Billing
- Custom VPC Network exists with at least one subnet and firewall rules configured
- Required APIs are enabled and visible in the GCP Console API dashboard
- Service Account is created with least-privilege roles documented

### Compliance Note
> Financial institutions operating under **PCI DSS Requirement 1** must install and maintain network security controls. Our custom VPC with deny-all-ingress firewall rules and explicit allow-listing mirrors this requirement. Document this mapping in the Wiki under `Architecture > Compliance`.

---

## Issue #2 — GitHub Repository & Project Board Initialization
**Label:** `devops` `documentation`
**Milestone:** Week 1–2
**Assignee:** Moses (Project Leader) + Juliana (Scribe)
**Priority:** P0 (Critical — blocks all team coordination)
**Size:** M
**Story Points:** 3

### Description
Set up the GitHub repository structure, project board, and Wiki skeleton that will serve as the project's home base for the entire semester.

### Background
A well-organized GitHub repo is how the team stays coordinated and how the final report gets built incrementally. GitHub Projects (the built-in kanban board) lets you track issues through stages like `To Do → In Progress → Done`. The Wiki will serve as the formal written report at the end of the semester.

### Tasks
- [ ] Create GitHub repository: `cloudhoney` (or use existing repo)
- [ ] Initialize with a `README.md` that includes project name, team members, class, financial sector framing, and architecture overview
- [ ] Create the following folder structure:
  ```
  /honeypot        → Flask honeypot application (banking decoy endpoints)
  /traffic-gen     → Python attack traffic simulator
  /functions       → Cloud Functions source code
  /dashboard       → Visualization dashboard (Cloud Run)
  /infra           → GCP setup scripts and configurations
  /docs            → Architecture docs, diagrams, and references
  /presentation    → Final presentation slides and demo materials
  ```
- [ ] Set up GitHub Project board using the **"Iterative development"** template with columns: `Backlog`, `Ready`, `In Progress`, `Done`
- [ ] Configure custom fields on the Project board: `Priority` (P0–P3), `Size` (XS–XL), `Story Points` (1, 2, 3, 5, 8)
- [ ] Create GitHub Milestones matching the proposal timeline:
  - Weeks 1–2: Foundation & Setup
  - Weeks 3–4: Honeypot Development & Deployment
  - Weeks 5–6: Logging Pipeline & Traffic Simulator v1
  - Weeks 7–8: Processing, Detection & Traffic Simulator v2
  - Weeks 9–10: Automation, Secrets, Dashboard
  - Weeks 11–12: Integration Testing & Demo Dry Run
  - Weeks 13–14: Report Writing & Refinement
  - Week 15: Final Presentation
- [ ] Initialize GitHub Wiki with the following pages: `Home`, `Architecture`, `Setup Guide`, `Implementation Log`, `Results`, `Compliance`, `GCP Services Inventory`
- [ ] Add all team members and instructor accounts (`gdparra-edu` and `cyberknowledge`) as repository collaborators
- [ ] Add a `.gitignore` that excludes `.env` files, service account keys (`*-sa-key.json`), `__pycache__/`, and any credential files
- [ ] Add issue and PR templates (optional but recommended for professional repo feel)

### Acceptance Criteria
- Repository is visible to all team members and instructor accounts
- Project board is populated with at least the first milestone's issues
- Project board has custom fields for Priority, Size, and Story Points configured
- Wiki skeleton has placeholder pages with headings (including GCP Services Inventory)
- `.gitignore` is in place and covers sensitive files
- `/presentation` directory exists in repo structure

---

## Issue #3 — Honeypot Flask Application Development (Financial Sector Endpoints)
**Label:** `backend` `compliance`
**Milestone:** Week 3–4
**Assignee:** Marissa (Developer)
**Priority:** P1 (High)
**Size:** L
**Story Points:** 5

### Description
Build the core Flask web application that acts as the decoy financial institution portal for simulated attacks. This is the "bait" at the center of CloudHoney's architecture — fake banking pages that look real but silently log every interaction.

### Background
Flask is a lightweight Python web framework — it lets you create web endpoints (URLs that respond to HTTP requests) with minimal setup. Our honeypot will expose pages that mimic a real financial institution's internet-facing infrastructure: an online banking login, a wire transfer form, a payment API, a back-office admin panel, and a customer account lookup. The key is that these pages *look* real but don't actually perform any financial operations — they just log everything they receive and forward it to GCP Cloud Logging.

The financial sector framing is important here. Real attackers target specific endpoint patterns in banking infrastructure. By naming our endpoints to match what attackers expect (`/login`, `/transfer`, `/payment`), the honeypot produces log data that maps directly to known financial threat categories — credential stuffing, wire fraud probing, and payment API abuse.

### Tasks
- [ ] Set up Python project with `flask` and `google-cloud-logging` dependencies
- [ ] Create a `requirements.txt` listing all dependencies with pinned versions
- [ ] Implement the following decoy financial sector endpoints:
  - `GET/POST /login` — fake online banking portal login page (accepts username/password POST data)
  - `GET/POST /transfer` — fake wire transfer submission interface (accepts account numbers, routing numbers, amount)
  - `GET/POST /payment` — fake payment API endpoint (accepts card data, merchant info, amount)
  - `GET/POST /admin` — fake back-office administrative panel
  - `GET/POST /account` — fake customer account lookup interface (accepts account ID or SSN-like input)
- [ ] For every incoming request, capture and log:
  - Timestamp (ISO 8601 format)
  - Source IP address
  - HTTP method and path
  - User-Agent header
  - Full request payload/body
  - Request headers (selected security-relevant headers)
- [ ] Format all log entries as structured **JSON** (important for downstream processing)
- [ ] Integrate `google-cloud-logging` library to forward logs directly to GCP Cloud Logging using a custom log name: `cloudhoney-events`
- [ ] Ensure the honeypot **never** processes, stores, or echoes back any real financial data — all form fields are captured as log entries only
- [ ] Write a basic `README.md` in `/honeypot` explaining how to run locally for testing

### Acceptance Criteria
- Flask app runs locally with `python app.py`
- Hitting each of the 5 endpoints produces a structured JSON log entry in the terminal
- Log entries include all required fields (timestamp, IP, method, path, user-agent, payload)
- No real financial processing occurs — endpoints return static decoy pages only

### Compliance Note
> Under **PCI DSS Requirement 3**, systems must not store sensitive authentication data after authorization. Our honeypot never processes real cardholder data, but this design decision should be documented explicitly in the Wiki to demonstrate awareness of the requirement.

---

## Issue #4 — VPC Network Provisioning, Compute Engine VM & Honeypot Deployment
**Label:** `infrastructure` `security`
**Milestone:** Week 3–4
**Assignee:** Moses (Project Leader)
**Priority:** P1 (High)
**Size:** L
**Story Points:** 5

### Description
Provision a GCP Compute Engine virtual machine inside the custom VPC Network (from Issue #1) and deploy the Flask honeypot application to it so it's accessible over the network under controlled firewall conditions.

### Background
A **virtual machine (VM)** is a computer that runs inside GCP's data center — you get to configure its operating system, memory, and CPU without owning any physical hardware. GCP Compute Engine is the service that manages these VMs, analogous to AWS EC2. We'll use a small, cost-effective VM since our Flask app is lightweight.

The critical difference from Issue #1's original version: this VM lives **inside the custom VPC Network** (`cloudhoney-vpc`), not on the default network. This means all traffic to and from the honeypot flows through our explicitly defined firewall rules. In a financial institution, no production system would ever run on a default network with default firewall rules — and neither will ours.

### Tasks
- [ ] Verify the custom VPC Network (`cloudhoney-vpc`) and subnet are active (from Issue #1)
- [ ] Provision a new Compute Engine VM with these specs:
  - Machine type: `e2-micro` (free tier eligible)
  - OS: Ubuntu 22.04 LTS
  - Region/Zone: same as the VPC subnet (e.g., `us-central1-a`)
  - **Network**: `cloudhoney-vpc` (NOT the default network)
  - **Subnet**: the subnet created in Issue #1
- [ ] Refine **VPC firewall rules** for the honeypot:
  - Allow inbound TCP on port 5000 from the traffic generator's expected source IP range
  - Allow inbound SSH (port 22) from team members' IPs only
  - Deny all other ingress (should already be the VPC default)
  - Tag the VM with a network tag (e.g., `honeypot-vm`) and scope firewall rules to this tag
- [ ] SSH into the VM and install dependencies: Python 3, pip, Flask, google-cloud-logging
- [ ] Deploy the Flask honeypot application from Issue #3
- [ ] Configure the app to run persistently using `systemd` so it survives reboots
- [ ] Attach the CloudHoney **Service Account** (`cloudhoney-app-sa` from Issue #1) to the VM so it can write to Cloud Logging without hardcoded credentials
- [ ] Note the VM's **external IP address** — this will be the target for the traffic generator
- [ ] Document the VM specs, network configuration, and firewall rules in the GitHub Wiki under `Architecture > Compute` and `Architecture > Networking`

### Acceptance Criteria
- VM is running inside `cloudhoney-vpc` and accessible via SSH from team IPs
- Flask app is reachable at `http://<VM-external-IP>:5000/login` from a browser
- A test request to the honeypot produces a log entry visible in GCP Cloud Logging console
- Firewall rules are scoped to network tags — not open to `0.0.0.0/0`

### Compliance Note
> **PCI DSS Requirement 1.3** requires restricting inbound and outbound traffic to that which is necessary. Our firewall rules explicitly allow-list only the traffic generator source and team SSH access. Document the firewall rule justification in the Wiki.

---

## Issue #5 — Cloud Logging Integration & Cloud Storage Pipeline
**Label:** `infrastructure` `backend`
**Milestone:** Week 5–6
**Assignee:** Moses (Project Leader)
**Priority:** P1 (High)
**Size:** M
**Story Points:** 3

### Description
Configure GCP Cloud Logging to receive honeypot events and route them to Cloud Storage for durable, queryable long-term storage. This is CloudHoney's data retention layer — analogous to a financial institution's requirement to retain security logs for audit purposes.

### Background
**Cloud Logging** is GCP's centralized log management service — think of it as a searchable inbox for all events your system generates. By default, logs stay in Cloud Logging for 30 days. To keep them longer (and make them available for batch analysis), we route them to **Cloud Storage (GCS)**, which is GCP's object storage — analogous to AWS S3. Logs will be stored as structured JSON files, organized by date, so we can query historical attack patterns later.

In the financial sector, log retention is not optional. **PCI DSS Requirement 10** mandates that organizations retain audit trail history for at least one year, with at least three months immediately available for analysis. While CloudHoney is an academic project, our Cloud Storage pipeline mirrors this production requirement.

### Tasks
- [ ] Verify honeypot logs are arriving in Cloud Logging (from Issue #3/4) under the `cloudhoney-events` custom log name
- [ ] Create a Cloud Storage bucket named `cloudhoney-logs` with:
  - Region: same as VM
  - Storage class: **Standard**
  - Access control: **Uniform** (not fine-grained)
  - Public access: **Blocked**
  - Optional: Enable **Object Versioning** for tamper evidence
- [ ] Create a **Log Sink** in Cloud Logging that exports honeypot log entries to the GCS bucket:
  - Filter: target only logs from the honeypot application (filter on `logName` containing `cloudhoney-events`)
  - Destination: `cloudhoney-logs` GCS bucket
- [ ] Confirm logs are being written to GCS in structured JSON format, partitioned by date (e.g., `logs/2026/02/26/`)
- [ ] Document the log schema (all fields and their types) in the GitHub Wiki under `Architecture > Logging`

### Acceptance Criteria
- Honeypot log entries appear in Cloud Logging within 5 seconds of a request
- After a Log Sink export cycle, JSON log files are visible in the GCS bucket
- Log files contain all expected fields and are parseable as valid JSON
- Bucket is private with no public access

### Compliance Note
> **PCI DSS Requirement 10.7** requires retaining audit trail history. Our Cloud Storage pipeline with date-partitioned logs satisfies this pattern. **GLBA Safeguards Rule** similarly requires monitoring and logging of access to customer financial information. Document this in the Wiki under `Architecture > Compliance`.

---

## Issue #6 — Python Traffic Generator v1 (Port Scan & Credential Stuffing)
**Label:** `backend` `compliance`
**Milestone:** Week 5–6
**Assignee:** Marissa (Developer)
**Priority:** P1 (High)
**Size:** M
**Story Points:** 3

### Description
Build the first version of the Python-based attack traffic simulator, covering two financial sector attack scenarios: port scanning (broad reconnaissance) and credential stuffing (rapid login attempts using leaked credential lists). This module "plays the role" of an attacker targeting a financial institution's internet-facing infrastructure.

### Background
- **Port scanning** is one of the earliest steps an attacker takes — probing a target's open ports and paths to map out what services are running. In a financial context, attackers scan for admin panels, API endpoints, and forgotten services.
- **Credential stuffing** is distinct from generic brute force: instead of guessing passwords, attackers use *real credentials leaked from other breaches* and try them against banking login portals. Financial institutions are prime targets because compromised banking credentials have immediate monetary value.

Since we can't expose CloudHoney to real internet traffic in an academic setting, we build a simulator that mimics these behaviors and fires them at our own honeypot. This gives us controlled, repeatable data to test the entire pipeline.

### Tasks
- [ ] Create `/traffic-gen/simulator.py` with a configurable `target_url` variable (pointing to the honeypot VM IP)
- [ ] Implement `simulate_port_scan()` function that:
  - Sends a series of HTTP GET requests to various paths on the honeypot (e.g., `/admin`, `/login`, `/transfer`, `/payment`, `/account`, `/api`, `/config`, `/debug`, `/status`)
  - Randomizes request timing slightly (to mimic real scanner behavior)
  - Includes a realistic `User-Agent` header (e.g., mimicking `nmap` or `masscan`)
  - Targets at least 10 distinct paths within 30 seconds
- [ ] Implement `simulate_credential_stuffing()` function that:
  - Sends rapid POST requests to `/login` with username/password pairs drawn from a simulated "leaked credential list"
  - Include at least 20 credential pairs (e.g., `jsmith/Summer2024!`, `admin/admin`, `mturner/Welcome1`, common banking username patterns)
  - Target rate: at least 15 attempts within 60 seconds (to trigger detection threshold)
  - Include realistic `User-Agent` strings (rotate between common browsers to mimic stuffing tool behavior)
- [ ] Add a `--scenario` CLI argument so the script can be invoked as:
  - `python simulator.py --scenario port_scan`
  - `python simulator.py --scenario credential_stuffing`
- [ ] Add logging so the simulator prints each request it sends (for debugging)
- [ ] Write a `README.md` in `/traffic-gen` explaining how to run the simulator and what each scenario does

### Acceptance Criteria
- Running `python simulator.py --scenario port_scan` sends at least 10 requests to distinct paths on the honeypot
- Running `python simulator.py --scenario credential_stuffing` sends at least 15 POST requests to `/login` within 60 seconds
- Each request appears as a log entry in GCP Cloud Logging
- Log entries from the simulator are visually distinguishable from manual test requests (via User-Agent or a custom header)

---

## Issue #7 — Python Traffic Generator v2 (Wire Transfer Probing, Payment API Abuse & Account Takeover Recon)
**Label:** `backend` `compliance`
**Milestone:** Week 7–8
**Assignee:** Marissa (Developer)
**Priority:** P2 (Medium)
**Size:** M
**Story Points:** 3

### Description
Extend the traffic simulator with three additional financial sector attack scenarios: wire transfer probing, payment API abuse, and account takeover reconnaissance. Together with Issue #6, this gives CloudHoney five distinct attack types covering the most critical threat categories in financial cybersecurity.

### Background
- **Wire transfer probing** targets the money-movement infrastructure of a financial institution. Attackers send requests to transfer endpoints with manipulated account numbers, routing numbers, or amounts — probing for validation weaknesses or authorization bypasses. A single successful wire fraud can cost millions.
- **Payment API abuse** targets payment processing endpoints with malformed or injected payloads — testing for SQL injection, parameter tampering, or authentication bypass in the payment flow.
- **Account takeover reconnaissance** is the precursor to full account takeover (ATO). Attackers probe session management endpoints, token validation, and account lookup interfaces — looking for information leaks or authentication weaknesses before launching a full ATO attack.

These three scenarios, combined with port scanning and credential stuffing from Issue #6, give CloudHoney a realistic spread of financial sector attack behaviors that map directly to **FFIEC** and **PCI DSS** threat categories.

### Tasks
- [ ] Implement `simulate_wire_transfer_probe()` function:
  - Sends POST requests to `/transfer` with manipulated financial data:
    - Invalid routing numbers (e.g., `000000000`, `999999999`)
    - Mismatched account/routing pairs
    - Extremely large transfer amounts
    - SQL injection attempts in amount and account fields
  - Include at least 10 distinct probe payloads
- [ ] Implement `simulate_payment_api_abuse()` function:
  - Sends POST requests to `/payment` with malformed payloads:
    - SQL injection strings in card number and merchant fields (reference OWASP Top 10)
    - Negative amounts, zero amounts, overflow values
    - Missing required fields
    - Duplicated transaction IDs
  - Include at least 8 distinct abuse payloads
- [ ] Implement `simulate_account_takeover_recon()` function:
  - Sends requests to `/account` probing for information leakage:
    - Sequential account IDs (enumeration attempt)
    - Common SSN patterns
    - Repeated session/token endpoint probing
  - Include at least 8 distinct recon payloads
- [ ] Wire all three into the `--scenario` CLI flag:
  - `python simulator.py --scenario wire_transfer_probe`
  - `python simulator.py --scenario payment_api_abuse`
  - `python simulator.py --scenario account_takeover_recon`
- [ ] Add an `--all` flag that runs all five scenarios in sequence:
  - `python simulator.py --all`
- [ ] Update the `/traffic-gen/README.md` with all five scenario descriptions

### Acceptance Criteria
- All five scenarios (`port_scan`, `credential_stuffing`, `wire_transfer_probe`, `payment_api_abuse`, `account_takeover_recon`) are runnable independently via `--scenario`
- `--all` flag runs all five scenarios sequentially
- Wire transfer probe payloads include manipulated routing/account patterns
- Payment API abuse payloads include SQL injection strings
- Account takeover recon payloads include sequential enumeration and session probing
- All simulator requests appear correctly in GCP Cloud Logging and GCS log files

---

## Issue #8 — Cloud Functions Processing Logic, Financial Detection Rules & Firestore Storage
**Label:** `backend` `infrastructure` `compliance`
**Milestone:** Week 7–8
**Assignee:** Moses (Project Leader)
**Priority:** P1 (High)
**Size:** XL
**Story Points:** 8

### Description
Implement the serverless Cloud Functions that subscribe to honeypot log events via Pub/Sub, evaluate each event against financial sector detection rules, write all classified events to Firestore, and publish alerts when thresholds are breached.

### Background
**Cloud Functions** is GCP's serverless compute service — you write a Python (or Node.js) function and GCP runs it automatically in response to events, without you managing any server. Think of it like a trigger: "whenever a new log entry arrives, run this function on it." In AWS terms, this is equivalent to AWS Lambda.

**Pub/Sub** (Publish/Subscribe) is GCP's messaging service. It works like a bulletin board: one service *publishes* a message, and any number of other services that are *subscribed* receive it. Our Cloud Function will subscribe to incoming log events and, if a detection rule fires, publish an alert message to a separate alert topic. In AWS terms, this is equivalent to SNS/SQS.

**Firestore** is GCP's managed NoSQL database — think of it as a fast, always-on document store (similar to a collection of JSON objects). Unlike Cloud Storage which is designed for files, Firestore is designed for structured records you want to query in real time. We'll write every classified event here so the dashboard (Issue #10) can read live data quickly without digging through log files. In AWS terms, this is equivalent to DynamoDB.

### Tasks
- [ ] Create a Pub/Sub **topic** for incoming log events: `cloudhoney-events`
- [ ] Update the Cloud Logging sink (from Issue #5) to also push to this Pub/Sub topic (you can have a sink export to both GCS and Pub/Sub, or create a second sink)
- [ ] Create a Firestore database in **Native mode** in the GCP Console (Native mode supports real-time reads, which the dashboard needs)
- [ ] Create a Cloud Function `classify_event` (Python 3.11 runtime) triggered by the `cloudhoney-events` Pub/Sub topic
- [ ] Implement the following **financial sector detection rules** inside `classify_event`:
  - **Credential stuffing:** more than 10 failed POST requests to `/login` from the same IP within 60 seconds → `HIGH` alert
  - **Wire fraud probe:** any request to `/transfer` or `/payment` containing manipulated routing/account number patterns (e.g., all zeros, all nines, SQL injection strings) → `HIGH` alert
  - **SQL injection / Payment API abuse:** presence of known injection strings (`' OR 1=1`, `UNION SELECT`, `DROP TABLE`, etc.) in any request payload → `HIGH` alert
  - **Port scan:** more than 8 distinct paths requested by the same IP within 30 seconds → `MEDIUM` alert
  - **Account takeover recon:** repeated requests to `/account` with sequential IDs or session/token probing patterns from the same IP → `MEDIUM` alert
- [ ] After classification, write every event to Firestore under the `events` collection with these fields:
  - `timestamp`, `source_ip`, `attack_type`, `severity`, `path`, `payload`, `alert_triggered` (boolean), `rule_matched`
- [ ] If a rule fires, publish a structured alert message to a new Pub/Sub topic: `cloudhoney-alerts`
- [ ] Deploy the function using `gcloud functions deploy`
- [ ] Document all detection rules and their thresholds in the GitHub Wiki under `Architecture > Detection Rules`

### Acceptance Criteria
- Cloud Function deploys successfully and appears in GCP Console under Cloud Functions
- Running the credential stuffing simulator (Issue #6) causes an alert message to appear in `cloudhoney-alerts` within 10 seconds
- Each classified event appears as a document in the Firestore `events` collection with all required fields
- Each alert message contains: event type, severity, source IP, timestamp, and rule that triggered
- All five attack types are correctly classified when their corresponding simulator scenarios are run

### Compliance Note
> Detection rules are modeled on **PCI DSS Requirements 10.6 and 11.4** (review logs and detect unauthorized activity) and informed by **FFIEC** guidance on monitoring for credential stuffing and wire fraud. The five-rule taxonomy maps directly to the top threat categories in the financial sector. Document the rule-to-compliance mapping in the Wiki.

---

## Issue #9 — Pub/Sub Alert Delivery, Secret Manager & Cloud Scheduler Automation
**Label:** `backend` `infrastructure` `security`
**Milestone:** Week 9–10
**Assignee:** Moses (Project Leader)
**Priority:** P1 (High)
**Size:** L
**Story Points:** 5

### Description
Configure Pub/Sub to deliver alert messages via email, store all credentials securely in Secret Manager, and set up Cloud Scheduler to automate attack simulation on a recurring schedule — enabling hands-free pipeline testing and a fully automated live demo.

### Background
**Pub/Sub** on its own is just a message queue — it holds messages until something picks them up. To actually *deliver* those alerts somewhere useful (like email), we need a lightweight Cloud Function to forward the message. For our demo, email delivery is sufficient and easy to demonstrate live.

**Secret Manager** is GCP's dedicated vault for storing sensitive values like API keys, passwords, and credentials. This is critically important for CloudHoney — since the project is literally a *security* platform, hardcoding a SendGrid API key inside a Python file or environment variable would be embarrassing at best. Secret Manager lets your Cloud Function retrieve the key at runtime without it ever appearing in source code. In AWS terms, this is equivalent to AWS Secrets Manager.

**Cloud Scheduler** is GCP's managed cron service — it lets you run jobs on a configurable schedule without managing any infrastructure. In AWS terms, this is equivalent to EventBridge Scheduler. For CloudHoney, Cloud Scheduler will trigger the traffic simulator on a recurring basis, which means the entire pipeline (attack → log → detect → alert → dashboard update) runs automatically. This is what makes the live demo impressive: the audience watches the dashboard update in real time without anyone manually running the simulator.

### Tasks
- [ ] **Secret Manager setup:**
  - Sign up for a free SendGrid account and generate an API key
  - Store the SendGrid API key in Secret Manager: secret name `sendgrid-api-key`
  - Grant the CloudHoney Service Account the `Secret Manager Secret Accessor` IAM role (least privilege — it can only *read* secrets, not create or delete them)
- [ ] **Alert delivery Cloud Function:**
  - Create a Pub/Sub **subscription** on `cloudhoney-alerts` topic (pull subscription for testing first)
  - Create a Cloud Function `deliver_alert` triggered by `cloudhoney-alerts`
  - The function retrieves the SendGrid API key from Secret Manager at runtime using the `google-cloud-secret-manager` Python library
  - Parses the alert message and sends an email notification containing: attack type, severity, source IP, timestamp, and rule triggered
- [ ] **Cloud Scheduler automation:**
  - Deploy the traffic simulator as a lightweight **Cloud Function** (or a script the scheduler can invoke via HTTP)
  - Create a Cloud Scheduler job named `cloudhoney-auto-sim` that triggers the simulator on a configurable schedule (e.g., every 30 minutes during development, adjusted for demo)
  - Cap the scheduler frequency to **no more than once per hour** during development to avoid runaway costs
  - Ensure the scheduler job targets the `--all` scenario flag so all five attack types are exercised
- [ ] **End-to-end test:** Cloud Scheduler triggers simulator → honeypot logs events → Cloud Function classifies → Firestore updated → alert email arrives → all within 60 seconds
- [ ] Document the Secret Manager setup, Cloud Scheduler configuration, and IAM role grants in the GitHub Wiki under `Architecture > Security` and `Architecture > Automation`

### Acceptance Criteria
- SendGrid API key is stored in Secret Manager and **not** present anywhere in source code or environment variables
- Running any attack simulator scenario results in an alert email delivered to the team inbox
- Email arrives within the 10-second latency target from the proposal
- Email body is human-readable and contains all relevant event fields including severity level
- Cloud Scheduler job is visible in GCP Console and successfully triggers the simulator on schedule
- Automated run produces Firestore documents and alert emails without manual intervention

### Compliance Note
> **PCI DSS Requirement 6.4.3** prohibits storing sensitive authentication data in production code. Secret Manager satisfies this requirement. **GLBA Safeguards Rule** requires regular testing of security controls — Cloud Scheduler's automated simulation runs serve as continuous validation. Document both in the Wiki.

---

## Issue #10 — Visualization Dashboard (Cloud Run + Firestore)
**Label:** `frontend` `infrastructure`
**Milestone:** Week 9–10
**Assignee:** Moses (Project Leader) + Marissa (Developer)
**Priority:** P1 (High)
**Size:** L
**Story Points:** 5

### Description
Build a custom real-time dashboard that reads classified event data from Firestore and displays live attack counts, event breakdowns by financial threat category, severity levels, and active alert states. Deploy it as a containerized web application on Cloud Run.

### Background
A **dashboard** is what makes the system tangible to an audience. Rather than showing raw log files, the dashboard translates CloudHoney's data into charts and counters that tell a financial security story: "Here's how many attacks we detected against our simulated banking infrastructure, here's what types they were, and here's when the alerts fired."

**Cloud Run** is GCP's managed container platform — you package your app into a container (a self-contained bundle with your code and everything it needs to run) and Cloud Run handles running it, scaling it, and exposing it to the web. You don't manage any servers. In AWS terms, this is equivalent to AWS App Runner. It's the cleanest way to host a custom web dashboard on GCP.

**Firestore** (written to in Issue #8) is what makes the dashboard *live*. Because every classified event was already stored there as a structured document, the dashboard can query Firestore directly for fast, up-to-date reads — no need to parse log files or dig through Cloud Storage.

Because Cloud Scheduler (Issue #9) automates the attack simulation, the dashboard can be shown updating in real time during the live demo without any manual intervention.

### Tasks
- [ ] Build a lightweight web dashboard (Python Flask or plain HTML/JS) that:
  - Queries the Firestore `events` collection for recent events
  - Displays a **live event counter** (total events, updated on refresh or polling)
  - Displays a **breakdown by attack type** (credential_stuffing, wire_transfer_probe, payment_api_abuse, account_takeover_recon, port_scan) as a bar or pie chart
  - Displays a **severity breakdown** (HIGH vs. MEDIUM alerts)
  - Displays a **recent events feed** showing the last 20 events with timestamp, type, severity, and source IP
  - Highlights any events where `alert_triggered = true` with a visual indicator
  - Optionally: a **timeline chart** showing event frequency over time
- [ ] Containerize the dashboard app using a `Dockerfile`
- [ ] Deploy to **Cloud Run**:
  - Use `gcloud run deploy` to push the container
  - Set the service to allow unauthenticated access (so the demo audience can view it in a browser)
  - Set `--min-instances=0` to ensure scale-to-zero (critical for $0 cost target)
  - Attach the CloudHoney Service Account for Firestore read access
- [ ] Confirm the dashboard auto-updates within 60 seconds of new events arriving in Firestore (via polling or auto-refresh)
- [ ] Share the Cloud Run public URL with the full team for review before the demo

### Acceptance Criteria
- Dashboard is accessible via a public Cloud Run URL (no login required for demo)
- All five financial sector attack types are represented in the breakdown visualization
- Severity levels (HIGH, MEDIUM) are visually distinguished
- Live event feed updates reflect new simulator runs within 60 seconds
- Dashboard is presentable for the live demo — clean, readable, no raw JSON visible
- Cloud Run service is visible in GCP Console under Cloud Run

---

## Issue #11 — Cloud Monitoring Setup & Alerting Policies
**Label:** `infrastructure` `devops`
**Milestone:** Week 9–10
**Assignee:** Moses (Project Leader)
**Priority:** P2 (Medium)
**Size:** M
**Story Points:** 3

### Description
Configure GCP Cloud Monitoring to track the health and performance of CloudHoney's infrastructure — VM uptime, Cloud Function execution metrics, Pub/Sub throughput, and Firestore read/write rates. Set up alerting policies for operational anomalies.

### Background
**Cloud Monitoring** is GCP's observability service — it collects metrics, logs, and traces from your cloud resources and lets you build dashboards and alerts around them. In AWS terms, this is equivalent to CloudWatch. While our custom dashboard (Issue #10) shows *security event data*, Cloud Monitoring tracks the *health of the pipeline itself*. If the Cloud Function starts failing or the VM goes down, Cloud Monitoring tells you before a user notices.

This is CloudHoney's 11th GCP service and is important for demonstrating that the team monitors not just security events but also the operational reliability of the platform.

### Tasks
- [ ] Create a Cloud Monitoring **workspace** for the `cloudhoney-sp26` project
- [ ] Set up a Cloud Monitoring **dashboard** showing:
  - Compute Engine VM CPU and memory utilization
  - Cloud Function invocation count, error rate, and execution latency
  - Pub/Sub message publish and delivery rates for both `cloudhoney-events` and `cloudhoney-alerts`
  - Firestore read/write operation counts
- [ ] Create **alerting policies** for:
  - VM instance down (Compute Engine uptime check fails)
  - Cloud Function error rate exceeds 10% over 5 minutes
  - Pub/Sub undelivered message count exceeds threshold
- [ ] Configure alert notification channel (email to team)
- [ ] Document the monitoring setup in the GitHub Wiki under `Architecture > Monitoring`

### Acceptance Criteria
- Cloud Monitoring dashboard is accessible and shows live metrics for all key services
- At least 3 alerting policies are active
- Alerts fire correctly when test conditions are simulated (e.g., stopping the VM)

---

## Issue #12 — System Integration Testing & End-to-End Demo Dry Run
**Label:** `devops` `documentation`
**Milestone:** Week 11–12
**Assignee:** All Team Members
**Priority:** P1 (High)
**Size:** L
**Story Points:** 5

### Description
Conduct full system integration testing to verify the entire CloudHoney pipeline works end-to-end: Cloud Scheduler triggers the simulator → honeypot logs events → Cloud Logging routes to GCS and Pub/Sub → Cloud Function classifies events and writes to Firestore → alerts publish and deliver email → dashboard updates in real time. Perform at least one full demo dry run.

### Background
Integration testing is where individual components get tested as a connected system for the first time under realistic conditions. This is the milestone where you catch timing issues, permission gaps, and data format mismatches between services. The demo dry run ensures the team can present CloudHoney confidently during the final presentation.

### Tasks
- [ ] Run all five attack scenarios via Cloud Scheduler automation and verify:
  - All events appear in Cloud Logging within 5 seconds
  - Log Sink exports to GCS are complete and parseable
  - Cloud Function classifies each event correctly (verify `attack_type` field in Firestore)
  - HIGH alerts trigger email delivery within 10 seconds
  - Dashboard reflects all events within 60 seconds
- [ ] Test failure scenarios:
  - What happens if the Cloud Function times out?
  - What happens if Firestore write fails?
  - Are alerts still delivered if one scenario produces no events?
- [ ] Measure and record **evaluation metrics** from the proposal:
  - Detection accuracy: percentage of simulated events correctly classified
  - Alert latency: time from event generation to email delivery
  - False positive rate: any benign requests incorrectly flagged
  - Automation reliability: did Cloud Scheduler trigger consistently?
  - Pipeline reliability: any dropped logs or failed writes?
  - Dashboard completeness: all five attack types visible?
- [ ] Conduct a **demo dry run** presenting the live system to the team
  - Practice the narrative: problem statement → architecture walkthrough → live demo → results
  - Time the demo to fit the final presentation slot
- [ ] Document all test results and metrics in the GitHub Wiki under `Results`

### Acceptance Criteria
- All five attack types flow through the full pipeline without manual intervention
- Evaluation metrics are recorded and documented
- At least one complete demo dry run has been performed
- Any bugs or timing issues discovered during testing are logged as new GitHub Issues and resolved

---

## Issue #13 — GitHub Wiki Final Report & Compliance Documentation
**Label:** `documentation` `compliance`
**Milestone:** Week 13–14
**Assignee:** Juliana (Scribe) + All Team Members
**Priority:** P1 (High)
**Size:** L
**Story Points:** 5

### Description
Complete the GitHub Wiki as the formal project report, including full architecture documentation, implementation details, results analysis, and a dedicated compliance section mapping CloudHoney's design to financial sector regulatory frameworks.

### Background
The GitHub Wiki serves as the team's final written report. Per the Kickoff Guide, this is one of the key deliverables alongside the live demo, the repository, and the deployed system. The compliance section is what elevates CloudHoney from a generic honeypot project to a credible financial sector security platform — it demonstrates that the team understands *why* each architectural decision matters in a regulated environment.

### Tasks
- [ ] Complete all Wiki pages with full content:
  - **Home**: Project overview, team, and navigation links
  - **Architecture**: System diagram, GCP service inventory (all 12 services with PaaS/SaaS underlying core service explanations per Kickoff Guide), VPC design, data flow
  - **GCP Services Inventory**: Dedicated page (see Issue #16) — verify content is complete and cross-linked from Architecture page
  - **Setup Guide**: Step-by-step instructions for recreating the environment
  - **Implementation Log**: Chronological record of what was built each sprint, decisions made, problems solved
  - **Results**: Evaluation metrics, detection accuracy analysis, latency measurements, screenshots of dashboard and alerts
  - **Compliance**: Dedicated page mapping CloudHoney's architecture to PCI DSS requirements, GLBA Safeguards Rule, and FFIEC guidance
- [ ] Verify the **GCP Services Inventory** Wiki page (Issue #16) includes underlying core IaaS services for every PaaS service
- [ ] Include architecture diagrams (from Issue #15) showing VPC boundaries, subnets, data flow, and service relationships
- [ ] Proofread and ensure consistent formatting across all Wiki pages

### Acceptance Criteria
- All Wiki pages contain substantive content (not just placeholders)
- PaaS/SaaS core service explanations are present for every applicable service
- Compliance section maps at least 5 specific PCI DSS/GLBA requirements to CloudHoney design decisions
- Architecture diagram shows VPC boundaries, subnets, firewall rules, and data flow between all 12 services
- Wiki is navigable and professional enough to serve as the team's formal report

---

## Issue #14 — Final Demo Preparation & Project Submission
**Label:** `devops` `documentation`
**Milestone:** Week 15
**Assignee:** All Team Members
**Priority:** P0 (Critical — final deliverable)
**Size:** M
**Story Points:** 3

### Description
Final preparation for the live presentation and project submission. Ensure all systems are running, the demo narrative is polished, and all deliverables are complete and accessible.

### Tasks
- [ ] Verify all GCP services are active and healthy:
  - Compute Engine VM running inside VPC
  - Cloud Logging receiving events
  - Cloud Storage bucket has log exports
  - Cloud Functions deployed and responding
  - Pub/Sub topics and subscriptions active
  - Firestore database populated with classified events
  - Secret Manager secrets accessible by service account
  - Cloud Scheduler job active and on schedule
  - Cloud Run dashboard accessible via public URL
  - Cloud Monitoring dashboard showing live metrics
- [ ] Perform a final **end-to-end automated demo run** — Cloud Scheduler triggers, full pipeline executes, dashboard updates live
- [ ] Prepare presentation slides in `/presentation` covering: problem statement, architecture, GCP services, financial sector framing, live demo, results, compliance mapping, lessons learned
- [ ] Ensure the GitHub repository is clean:
  - README is up to date (includes Cloud Computing Domains, GCP Services Inventory with core service explanations, and architecture diagram reference)
  - All code is committed and organized in the correct directories
  - No credentials, API keys, or `.env` files in the repo
  - All GitHub Issues from the sprint plan are closed or accounted for
  - GitHub Project board reflects final state with Priority/Size/Story Points filled in for all issues
- [ ] Submit all required deliverables per syllabus instructions

### Acceptance Criteria
- Live demo runs successfully with no manual intervention (fully automated via Cloud Scheduler)
- All 12 GCP services are demonstrably in use
- GitHub Wiki report is complete (including GCP Services Inventory page)
- Repository is clean and professional
- Presentation is rehearsed and timed

---

## Issue #15 — Cloud Architecture Diagram (draw.io)
**Label:** `documentation` `infrastructure`
**Milestone:** Week 1–2
**Assignee:** Moses (Project Leader) + Juliana (Scribe)
**Priority:** P0 (Critical — required deliverable per Kickoff Guide)
**Size:** M
**Story Points:** 3

### Description
Create a formal cloud architecture diagram using draw.io (or Lucidchart / GCP Architecture Diagramming Tool) that visually represents CloudHoney's full system architecture — including VPC boundaries, subnets, firewall rules, data flow between services, and the relationships between all 12 GCP services. This is a **required deliverable** per the CIS 4355 Group Project Kickoff Guide.

### Background
The Kickoff Guide explicitly distinguishes between a simple component list and a proper cloud architecture diagram. The ASCII text diagram in the README shows data flow, but it does not show VPC boundaries, subnet placement, firewall rule directionality, or which services live inside vs. outside the VPC. A proper architecture diagram answers questions like: "Where does the honeypot VM sit relative to the VPC boundary? Which services communicate over the public internet vs. internal Google networking? Where are the firewall rules enforced?"

Creating this diagram early (Week 1–2) serves two purposes: it gives the whole team a shared mental model of the system before building begins, and it satisfies the proposal requirement early so it's not rushed during Week 13–14 report writing.

**draw.io** is free, runs in a browser at [app.diagrams.net](https://app.diagrams.net), and has built-in GCP icon packs under `Networking > GCP`.

### Tasks
- [ ] Open draw.io and load the **GCP icon set** (available under the shape library search or via the GCP stencil pack)
- [ ] Create the diagram showing:
  - **VPC boundary** (`cloudhoney-vpc`) as a dashed rectangle enclosing internal resources
  - **Subnet** (`us-central1` subnet with CIDR range) inside the VPC
  - **Compute Engine VM** (honeypot) inside the subnet, with network tag `honeypot-vm`
  - **Firewall rules** annotated on the VPC boundary: SSH (port 22, team IPs only), HTTP (port 5000, traffic gen source only), deny-all-ingress default
  - **Cloud Logging** receiving structured JSON logs from the VM (arrow from VM → Cloud Logging)
  - **Cloud Storage** bucket receiving exports from Cloud Logging (arrow from Cloud Logging → GCS)
  - **Pub/Sub** topics (`cloudhoney-events` and `cloudhoney-alerts`) with arrows showing message flow
  - **Cloud Functions** (`classify_event` and `deliver_alert`) connected to their respective Pub/Sub triggers
  - **Firestore** receiving writes from the classify function (arrow from Cloud Function → Firestore)
  - **Cloud Run** dashboard reading from Firestore (arrow from Firestore → Cloud Run)
  - **Cloud Scheduler** triggering the traffic simulator (arrow from Scheduler → simulator)
  - **Secret Manager** providing credentials to Cloud Functions at runtime (dashed arrow)
  - **Cloud Monitoring** observing all services (optional: show as an overlay or sidebar)
  - **Cloud IAM** shown as a cross-cutting service governing access (optional: label or sidebar)
- [ ] Use **color coding** to distinguish service categories (Compute = blue, Networking = red, Storage = green, Security = orange, Operations = purple — matching GCP's own color conventions)
- [ ] Export the diagram as:
  - **PNG** → commit to `/docs/architecture_diagram.png` (for README and Wiki embedding)
  - **draw.io XML** → commit to `/docs/architecture_diagram.drawio` (for future editing)
- [ ] Embed the PNG in the GitHub Wiki **Architecture** page
- [ ] Reference the diagram in the README's System Architecture section

### Acceptance Criteria
- Diagram clearly shows VPC boundary with subnet and firewall rules
- All 12 GCP services are represented with official GCP icons (or labeled boxes)
- Data flow arrows show the direction of communication between services
- Diagram is committed to `/docs/` in both PNG and editable formats
- Diagram is embedded in the Wiki Architecture page
- README references the diagram with a link

### Compliance Note
> A proper architecture diagram showing network boundaries and data flow is not just a class requirement — it directly supports **PCI DSS Requirement 1.1.2**, which requires organizations to maintain a current network diagram identifying all connections to cardholder data. CloudHoney's diagram serves as a demonstration of this practice.

---

## Issue #16 — GCP Services Inventory Wiki Page
**Label:** `documentation` `compliance`
**Milestone:** Week 3–4
**Assignee:** Juliana (Scribe)
**Priority:** P1 (High — explicit Kickoff Guide requirement)
**Size:** S
**Story Points:** 2

### Description
Create a dedicated **GCP Services Inventory** page on the GitHub Wiki that documents all 12 GCP services used in CloudHoney, including each service's role, service model (IaaS/PaaS/SaaS), and — for every PaaS service — a detailed explanation of the underlying core IaaS services that Google manages on our behalf. This directly satisfies a core requirement from the CIS 4355 Group Project Kickoff Guide.

### Background
The Kickoff Guide states: *"If your project uses PaaS or SaaS services, you must explain what core IaaS services underpin them. For example, if you use Cloud Run (PaaS), you should describe the underlying Compute Engine VMs, VPC networking, and load balancing that Google manages on your behalf. This demonstrates your understanding of the full cloud stack."*

The README already includes a summary table with the underlying core services, but the Wiki page is where the full, detailed explanations live. This is the page Dr. Parra will check to verify the team understands the cloud stack beyond just using managed services.

### Tasks
- [ ] Create a new Wiki page titled **GCP Services Inventory**
- [ ] For each of the 12 GCP services, document:
  - **Service name** and role in CloudHoney
  - **Service model**: IaaS, PaaS, or SaaS
  - **AWS equivalent** (for cross-reference, since the team has AWS background)
  - **How CloudHoney uses it**: 2–3 sentences on the specific integration
  - **Free tier limits**: document the specific free tier quotas we rely on to stay at $0
- [ ] For each **PaaS service**, include a dedicated subsection explaining the underlying core IaaS:
  - **Cloud Functions**: GKE-managed containers on Compute Engine; internal VPC networking; automatic scaling and container lifecycle management by Google
  - **Cloud Run**: GKE cluster on Compute Engine; Cloud Load Balancing via Andromeda virtual network; VPC for network isolation; automatic TLS termination
  - **Firestore**: Spanner-derived distributed database infrastructure; Compute Engine for serving; Colossus distributed file system for storage; automatic multi-zone replication
  - **Pub/Sub**: Google's globally distributed messaging infrastructure; Compute Engine for broker nodes; Borg orchestration; durable message storage with at-least-once delivery
  - **Cloud Logging**: Borgmaster-orchestrated infrastructure; Compute Engine for log processing; Colossus for durable storage; integrated with Cloud Monitoring for metric extraction
  - **Cloud Monitoring**: Borgmaster-orchestrated infrastructure; Compute Engine for metric processing; internal time-series database (Monarch) for storage; integrates with Cloud Logging and alerting
  - **Cloud Scheduler**: Google's internal job scheduling system on Compute Engine; at-least-once job execution guarantee; integrates with Pub/Sub, HTTP, and App Engine targets
  - **Secret Manager**: Cloud KMS for envelope encryption; dedicated HSM infrastructure for key storage; Compute Engine for API serving; IAM integration for access control
- [ ] Add a **cost table** showing the free tier limit for each service and CloudHoney's expected usage (to document the $0 cost target)
- [ ] Cross-link this page from the Wiki **Home** page and the **Architecture** page
- [ ] Ensure content is consistent with the README's GCP Services Inventory section

### Acceptance Criteria
- Wiki page exists with all 12 services documented
- Every PaaS service has a detailed "Underlying Core Services" subsection
- Free tier limits are documented for each service
- Page is linked from Wiki Home and Architecture pages
- Content aligns with the README's summary table (no contradictions)

### Compliance Note
> Understanding the full cloud stack is not just an academic requirement — in a financial institution, compliance teams and auditors expect engineers to explain where data lives physically and which layers of the stack the organization controls vs. delegates to the cloud provider. This aligns with the **shared responsibility model** and supports **PCI DSS Requirement 12.8** (managing service provider relationships).
