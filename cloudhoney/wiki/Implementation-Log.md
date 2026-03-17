# Implementation Log

Chronological record of progress, decisions, and issues encountered during development.

---

## Week 1–2: Foundation

### Completed
- GCP project `cloudhoney-sp26` created
- Billing enabled with $10 budget alert
- Required APIs enabled (Compute Engine, Cloud Logging, Cloud Storage, Cloud Functions, Pub/Sub, Cloud Run, Secret Manager, Firestore, Cloud Monitoring)
- Service account `cloudhoney-app` created with least-privilege roles
- GitHub repository initialized with project structure
- GitHub Project board created with milestones and sprint issues
- Wiki skeleton established

### Decisions
- Selected `e2-micro` VM type for honeypot (free tier eligible, sufficient for Flask app)
- Chose Firestore Native mode over Datastore mode for real-time dashboard reads
- Decided on SendGrid for email alerts (free tier: 100 emails/day)

### Issues Encountered
> TODO: Document any blockers or challenges

---

## Week 3–4: Core Build

> TODO: Document honeypot development and VM deployment progress

---

## Week 5–6: Data Pipeline

> TODO: Document Cloud Logging integration and traffic generator v1

---

## Week 7–8: Detection Engine

> TODO: Document Cloud Functions, detection rules, and traffic generator v2

---

## Week 9–10: Alerts & Dashboard

> TODO: Document alert delivery and dashboard development

---

## Week 11–12: Integration Testing

> TODO: Document end-to-end testing and performance evaluation

---

## Week 13–14: Final Report & Demo Prep

> TODO: Document Wiki report completion and demo preparation
