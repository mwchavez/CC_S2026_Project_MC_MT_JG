# Testing and Validation Report

## Overview

This document outlines the testing process used to validate the functionality of the CloudHoney system. The goal of testing was to confirm that each component of the pipeline operates correctly, from initial data capture to final alerting and visualization.

Testing was performed incrementally across system layers, starting with local validation and progressing to full end-to-end pipeline verification in the cloud environment.

---

## Testing Objectives

The primary objectives of testing were:

- Verify honeypot endpoint behavior and logging
- Confirm successful deployment and execution in the cloud environment
- Validate log ingestion into Cloud Logging
- Ensure logs are exported to Cloud Storage
- Confirm real-time event processing through Pub/Sub
- Validate detection rule execution
- Confirm events are written to Firestore
- Verify alert generation and email delivery
- Validate dashboard visualization
- Confirm monitoring and alerting for system health

---

## Test Environment

Testing was conducted within the `cloudhoney-sp26` Google Cloud project using:

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

## Phase 1: Local Honeypot Validation

### Objective
Validate that the honeypot application functions correctly and generates structured logs.

### Test Actions
- Executed the Flask application locally using `python app.py`
- Accessed endpoints:
  - `/login`
  - `/transfer`
  - `/payment`
  - `/account`
  - `/admin`
- Observed console output for request handling and logging

### Expected Result
- Endpoints respond correctly
- Structured logs are generated with request metadata

### Actual Result
- All endpoints responded as expected
- Logs were generated in structured JSON format including:
  - path
  - method
  - user agent
  - payload
  - attack context

### Outcome
Local honeypot functionality and logging were successfully validated.

---

## Phase 2: Cloud Deployment Validation

### Objective
Confirm that the honeypot application runs correctly on a Compute Engine VM and integrates with Cloud Logging.

### Test Actions
- Deployed VM using `gcloud compute instances create`
- Configured firewall rules for SSH and application traffic
- Connected to VM via SSH
- Deployed and executed the honeypot application
- Enabled Cloud Logging integration
- Configured `systemd` service for persistence

### Expected Result
- VM is accessible and running
- Application runs continuously
- Logs are visible in Cloud Logging

### Actual Result
- VM successfully created and accessed
- Application executed correctly
- Logs appeared in Cloud Logging under `cloudhoney-events`
- Service persisted using `systemd`

### Outcome
Cloud deployment and logging integration were successfully validated.

---

## Phase 3: Log Storage Validation

### Objective
Verify that logs are exported from Cloud Logging to Cloud Storage.

### Test Actions
- Created Cloud Storage bucket
- Configured log sink to export logs
- Queried logs using CLI
- Checked storage bucket contents using recursive listing

### Expected Result
- Logs appear in Cloud Logging
- Logs are exported to Cloud Storage

### Actual Result
- Initial storage check returned no results (expected delay)
- Subsequent checks confirmed log files present in bucket
- Logs stored in time-based directory structure

### Outcome
Log export pipeline to Cloud Storage was successfully validated.

---

## Phase 4: Event Processing and Detection Validation

### Objective
Validate real-time event processing and detection logic.

### Test Actions
- Created Pub/Sub topics (`cloudhoney-events`, `cloudhoney-alerts`)
- Configured log sink to route logs to Pub/Sub
- Deployed `classify_event` Cloud Function
- Executed simulator scenarios:
  - credential stuffing
  - port scanning
  - payment API abuse
- Reviewed Cloud Logging and function logs

### Expected Result
- Events are processed by the Cloud Function
- Detection rules are triggered appropriately
- Events are classified and enriched

### Actual Result
- Events successfully delivered to Pub/Sub
- Cloud Function processed incoming events
- Logs showed:
  - event parsing
  - rule evaluation
  - threshold detection
  - alert publishing
- Detection rules triggered correctly based on scenario

### Outcome
Event processing and detection logic were successfully validated.

---

## Phase 5: Firestore Data Validation

### Objective
Confirm that processed events are stored in Firestore.

### Test Actions
- Observed Firestore database after running simulator scenarios
- Reviewed stored event documents

### Expected Result
- Events stored with structured fields

### Actual Result
- Events stored in `events` collection
- Each document included:
  - attack type
  - severity
  - rule matched
  - source IP
  - timestamp
  - payload data

### Outcome
Structured event storage was successfully validated.

---

## Phase 6: Alerting and Notification Validation

### Objective
Verify that alerts are generated and delivered.

### Test Actions
- Published test messages to `cloudhoney-alerts`
- Triggered detection scenarios via simulator
- Configured SendGrid API key using Secret Manager
- Observed email notifications

### Expected Result
- Alerts generated when rules are triggered
- Emails sent with correct event details

### Actual Result
- Alerts published to Pub/Sub
- Email notifications received containing:
  - severity
  - attack type
  - source IP
  - timestamp
  - target path
  - rule matched
- Multiple alerts received for different attack types

### Outcome
Alert generation and notification delivery were successfully validated.

---

## Phase 7: Dashboard Validation

### Objective
Confirm that processed data is visualized correctly.

### Test Actions
- Deployed dashboard using Cloud Run
- Triggered simulator to generate events
- Accessed dashboard via public URL

### Expected Result
- Dashboard displays real-time event data
- Metrics and charts reflect system activity

### Actual Result
- Dashboard displayed:
  - total events
  - alerts triggered
  - severity breakdown
- Charts showed:
  - attack type distribution
  - severity distribution
- Event table displayed recent activity with full details

### Outcome
Dashboard visualization and data integration were successfully validated.

---

## Phase 8: Monitoring and Alerting Validation

### Objective
Verify system health monitoring and infrastructure alerting.

### Test Actions
- Created monitoring notification channel
- Deployed alert policies:
  - Honeypot VM Down
  - Cloud Function Error Rate > 10%
  - Pub/Sub Backlog > 100
- Configured monitoring dashboard
- Triggered test alerts

### Expected Result
- Monitoring dashboard displays system metrics
- Alerts trigger when conditions are met
- Notifications are delivered

### Actual Result
- Monitoring dashboard displayed:
  - VM CPU utilization
  - Cloud Function metrics
  - Pub/Sub metrics
- Alert policies created successfully
- Test alerts triggered and notifications received

### Outcome
System monitoring and infrastructure alerting were successfully validated.

---

## End-to-End Validation Summary

Full system testing confirmed that all components operate together as expected.

Validated pipeline:

```
Simulator
   ↓
Honeypot VM
   ↓
Cloud Logging
   ↓
Pub/Sub
   ↓
classify_event
   ↓
Firestore
   ↓
Alert Pipeline
   ↓
Dashboard
```

Each stage of the pipeline was tested individually and as part of the full system.

---

## Conclusion

Testing confirmed that CloudHoney successfully captures, processes, and responds to simulated attack activity within a cloud environment.

The system demonstrated:

- Reliable data capture and logging
- Accurate detection of multiple attack types
- Proper event classification and storage
- Successful alert generation and delivery
- Real-time visualization of system activity
- Effective monitoring of system health

All major components were validated, and the system operates as a complete, end-to-end detection and monitoring pipeline.
