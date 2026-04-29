# Deployment and Operations Guide

## Overview

This document provides guidance for deploying, operating, and maintaining the CloudHoney system. It focuses on how system components are run in the cloud environment, how they interact, and how to monitor and troubleshoot the system during operation.

CloudHoney is composed of multiple distributed components across Google Cloud services. Proper operation depends on verifying that each component is active and that data is flowing through the pipeline correctly.

---

## System Components

The CloudHoney system consists of the following deployed components:

- Honeypot VM (Compute Engine)
- Cloud Logging
- Cloud Storage (log retention)
- Pub/Sub topics (`cloudhoney-events`, `cloudhoney-alerts`)
- Cloud Function (`classify_event`)
- Cloud Function (`deliver_alert`)
- Firestore database
- Cloud Run dashboard
- Cloud Scheduler job
- Cloud Monitoring dashboard and alert policies

---

## Deployment Summary

### Honeypot VM

The honeypot application is deployed on a Compute Engine instance.

- Runs a Flask application
- Configured with `systemd` for persistence
- Logs are sent to Cloud Logging
- Accessible through controlled firewall rules

### Event Processing

- Logs are routed to Pub/Sub (`cloudhoney-events`)
- `classify_event` function processes events
- Processed data is written to Firestore
- Alerts are published to `cloudhoney-alerts`

### Alerting

- `deliver_alert` function processes alert messages
- Sends email notifications using SendGrid
- API key is stored in Secret Manager

### Dashboard

- Deployed on Cloud Run
- Reads data from Firestore
- Provides real-time visualization of system activity

### Automation

- Cloud Scheduler triggers the simulator
- Generates periodic attack scenarios for testing and demonstration

### Monitoring

- Cloud Monitoring dashboard tracks system health
- Alert policies notify on infrastructure issues

---

## Operational Workflow

During normal operation, the system follows this flow:

```
Traffic Generation
    ↓
Honeypot VM
    ↓
Cloud Logging
    ↓
Pub/Sub (events)
    ↓
classify_event
    ↓
Firestore
    ↓
Pub/Sub (alerts)
    ↓
deliver_alert
    ↓
Email Notifications
    ↓
Dashboard Visualization
```

Operators should verify that data is moving through each stage.

---

## Service Verification Checklist

### 1. Honeypot VM

Verify:
- VM is running
- Application service is active

Command:
```
systemctl status cloudhoney.service
```

Check:
- Service is `active (running)`
- No repeated errors in logs

---

### 2. Cloud Logging

Verify:
- Logs are being generated

Command:
```
gcloud logging read 'logName="projects/cloudhoney-sp26/logs/cloudhoney-events"' --limit=5
```

Check:
- New entries appear
- JSON payload contains request data

---

### 3. Cloud Storage (Log Retention)

Verify:
- Logs are exported to storage

Command:
```
gcloud storage ls gs://cloudhoney-logs-sp26/ --recursive
```

Check:
- Files exist in time-based directories
- New logs appear over time

---

### 4. Pub/Sub Topics

Verify:
- Topics exist and receive messages

Command:
```
gcloud pubsub topics list
```

Check:
- `cloudhoney-events`
- `cloudhoney-alerts`

---

### 5. Cloud Function: classify_event

Verify:
- Function is deployed and running

Command:
```
gcloud functions logs read classify-event --region=us-east1 --limit=10
```

Check:
- Event processing logs appear
- Rule evaluation and alerts are logged

---

### 6. Firestore

Verify:
- Events are being stored

Check:
- `events` collection contains recent entries
- Documents include expected fields:
  - attack type
  - severity
  - timestamp
  - source IP

---

### 7. Alerting Function

Verify:
- Alerts are being processed

Command:
```
gcloud functions logs read deliver_alert --region=us-east1 --limit=10
```

Check:
- Alert messages processed
- No repeated failures

---

### 8. Email Notifications

Verify:
- Alerts are received in inbox

Check:
- Email includes:
  - severity
  - attack type
  - source IP
  - timestamp
  - rule matched

---

### 9. Dashboard (Cloud Run)

Verify:
- Service is accessible via URL
- Data is updating

Check:
- Metrics reflect recent activity
- Charts display current distribution
- Event table updates

---

### 10. Cloud Scheduler

Verify:
- Job is scheduled and running

Command:
```
gcloud scheduler jobs list
```

Check:
- Job exists and is enabled

Manual test:
```
gcloud scheduler jobs run <job-name>
```

---

### 11. Monitoring and Alerts

Verify:
- Monitoring dashboard is active
- Alert policies are enabled

Check:
- VM metrics visible
- Cloud Function metrics visible
- Pub/Sub metrics visible

Confirm:
- Alert emails received when test conditions are triggered

---

## Common Operational Checks

Operators should regularly verify:

- Honeypot service is running
- Logs are being generated
- Events are reaching Firestore
- Alerts are being delivered
- Dashboard reflects recent data
- No alert policies are actively firing unexpectedly

---

## Troubleshooting

### No Logs Appearing

Possible causes:
- Honeypot application not running
- Logging misconfiguration

Check:
- VM service status
- application logs

---

### Logs Not Appearing in Storage

Possible causes:
- Log sink misconfiguration
- delay in export

Check:
- sink configuration
- wait and re-check bucket contents

---

### Events Not Processed

Possible causes:
- Pub/Sub not receiving messages
- Cloud Function failure

Check:
- Pub/Sub topics
- function logs

---

### No Alerts Generated

Possible causes:
- detection thresholds not met
- alert pipeline issue

Check:
- function logs for rule execution
- Pub/Sub alerts topic

---

### No Email Notifications

Possible causes:
- Secret Manager misconfiguration
- SendGrid API issue

Check:
- secret access permissions
- deliver_alert logs

---

### Dashboard Not Updating

Possible causes:
- Firestore not receiving data
- dashboard query issue

Check:
- Firestore collection
- Cloud Run logs

---

### Monitoring Alerts Not Triggering

Possible causes:
- alert policy misconfiguration
- incorrect thresholds

Check:
- alert policies
- notification channels

---

## Operational Best Practices

- Regularly monitor dashboard for unusual patterns
- Review alert frequency to identify tuning needs
- Validate alerting periodically using test scenarios
- Monitor system health using Cloud Monitoring
- Ensure secrets are not exposed or hardcoded
- Maintain least-privilege IAM access

---

## Summary

The CloudHoney system is designed to operate as a continuous monitoring and detection pipeline. Successful operation depends on maintaining visibility across all system components and ensuring that data flows correctly from ingestion to alerting and visualization.

This guide provides the necessary steps to verify system health, diagnose issues, and maintain consistent operation.
