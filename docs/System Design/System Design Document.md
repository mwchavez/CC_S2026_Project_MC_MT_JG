# System Design Document

## Overview

CloudHoney is a cloud-based threat detection and monitoring system designed to simulate and identify suspicious activity within a financial services environment. The system combines a custom-built honeypot, real-time event processing, rule-based detection logic, and a visualization dashboard to provide end-to-end visibility into potential attack behavior.

The architecture is designed around three core goals:
- Capture realistic attack data through a simulated financial application
- Process and classify events in real time using defined detection rules
- Provide actionable insights through alerting and visualization

---

## High-Level Architecture

CloudHoney follows an event-driven architecture built on Google Cloud Platform services. The system is composed of multiple layers that work together to capture, process, and present security-relevant data.

**Core flow:**
```
Traffic Simulator
    ↓
Honeypot (Compute Engine VM)
    ↓
Cloud Logging
    ↓
Pub/Sub (cloudhoney-events)
    ↓
Cloud Function (classify_event)
    ↓
Firestore (events collection)
    ↓
Pub/Sub (cloudhoney-alerts)
    ↓
Cloud Function (deliver_alert)
    ↓
Email Notifications
    ↓
Cloud Run Dashboard
```

---

## Environment and Infrastructure

### GCP Project and Services

All components are deployed within the `cloudhoney-sp26` Google Cloud project. Core services used include:

- Compute Engine (honeypot VM)
- Cloud Logging
- Cloud Storage
- Pub/Sub
- Cloud Functions
- Firestore
- Cloud Run
- Secret Manager
- Cloud Scheduler
- Cloud Monitoring

---

### Network Architecture

A dedicated Virtual Private Cloud (VPC) named `cloudhoney-vpc` is used to isolate the honeypot infrastructure.

- Custom subnet configuration is used instead of default networking
- Regional routing is enabled
- Firewall rules restrict access:
  - SSH access limited to trusted IP ranges
  - Application traffic (port 5000) restricted to the traffic generator

This design ensures controlled exposure of the honeypot while limiting unnecessary access.

---

### Identity and Access Management

Access to system components is controlled using IAM roles and service accounts.

- A dedicated service account (`cloudhoney-app`) is used by system components
- Roles assigned include:
  - Logs Writer
  - Pub/Sub Publisher
  - Secret Manager Accessor
  - Storage Object Creator

User access is separated by role:
- Viewer (read-only)
- Editor (operational changes)
- Administrator (full control)

This follows a least-privilege access model.

---

## Application Layer: Honeypot

The honeypot is a Flask-based web application deployed on a Compute Engine VM. It simulates a financial system with multiple endpoints designed to attract and capture malicious activity.

### Key Endpoints

- `/login` – authentication simulation
- `/transfer` – wire transfer simulation
- `/payment` – payment API simulation
- `/account` – account lookup functionality
- `/admin` – administrative interface
- catch-all routes for unknown paths (used for reconnaissance detection)

### Logging

All incoming requests are logged as structured JSON entries containing:

- timestamp
- source IP
- HTTP method
- endpoint/path
- user agent
- payload data
- attack context

Logs are sent directly to Cloud Logging for further processing.

---

## Data Collection and Storage

### Cloud Logging

The honeypot application writes structured logs to Cloud Logging under the `cloudhoney-events` log.

These logs serve as the primary source of truth for all system activity.

---

### Cloud Storage (Audit Retention)

A log sink exports logs from Cloud Logging to a Cloud Storage bucket (`cloudhoney-logs-sp26`).

- Object versioning is enabled
- Logs are stored in time-based folders
- Provides long-term audit retention

This supports traceability and compliance-related logging requirements.

---

### Pub/Sub (Event Pipeline)

A second log sink routes events to Pub/Sub:

- Topic: `cloudhoney-events`

This enables real-time processing of events as they are generated.

---

## Event Processing and Detection

### Cloud Function: classify_event

The `classify_event` Cloud Function processes incoming events from Pub/Sub.

Its responsibilities include:
- Parsing structured log data
- Evaluating events against detection rules
- Assigning severity levels
- Writing processed events to Firestore
- Publishing alerts when conditions are met

---

### Detection Logic

The system uses rule-based detection across multiple attack scenarios:

- SQL injection detection (payload pattern matching)
- Wire fraud probing (endpoint + payload anomalies)
- Credential stuffing (threshold-based login attempts)
- Account takeover reconnaissance (repeated probing)
- Port scanning (multiple distinct endpoint requests)

Detection is implemented using both:
- Single-event triggers
- Threshold-based logic over time

---

### Firestore (Processed Data)

Processed events are stored in Firestore under the `events` collection.

Each document includes:
- attack type
- severity
- rule matched
- source IP
- timestamp
- request metadata

This structured dataset is used for analysis and visualization.

---

## Alerting and Notification

### Pub/Sub Alerts

When a detection rule is triggered, an alert is published to:

- Topic: `cloudhoney-alerts`

---

### Cloud Function: deliver_alert

The `deliver_alert` function processes alert messages and sends notifications.

- Uses SendGrid API
- API key stored securely in Secret Manager
- Generates structured email alerts including:
  - severity
  - attack type
  - source IP
  - timestamp
  - affected endpoint
  - rule triggered

---

### Automation

Cloud Scheduler is used to automate traffic simulation:

- Scheduled execution of attack scenarios
- Supports continuous testing and demonstration of system behavior

---

## Visualization Layer

### Cloud Run Dashboard

A Flask-based dashboard is deployed using Cloud Run to provide a real-time view of system activity.

### Features

- Summary metrics:
  - total events
  - alerts triggered
  - severity counts
- Visualizations:
  - attack type breakdown
  - severity distribution
- Event table:
  - recent activity with detailed fields

The dashboard reads from Firestore and updates automatically to reflect new events.

---

## Monitoring and Reliability

### Cloud Monitoring Dashboard

A dedicated monitoring dashboard tracks system health:

- VM CPU utilization
- VM memory utilization
- Cloud Function invocation metrics
- Pub/Sub throughput and backlog

---

### Alert Policies

Alerting policies are configured for:

- Honeypot VM availability
- Cloud Function error rates
- Pub/Sub subscription backlog

Notifications are sent via email when thresholds are exceeded.

---

### Incident Detection

The system can detect both:
- Security events (malicious activity)
- Operational issues (system failures)

This ensures visibility into both threats and system health.

---

## Summary

CloudHoney is designed as a modular, event-driven system that captures, processes, and visualizes security events in a simulated financial environment.

The architecture demonstrates:
- Secure infrastructure design
- Real-time event processing
- Rule-based threat detection
- Automated alerting
- Centralized data storage
- Operational monitoring
- Analyst-focused visualization

Together, these components form a complete detection and monitoring pipeline aligned with real-world security system design principles.
