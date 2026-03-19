# Cloud Functions

Serverless processing logic deployed on GCP Cloud Functions. Subscribes to honeypot log events via Pub/Sub, classifies events against detection rules, writes results to Firestore, and publishes alerts.

## Functions

| Function | Trigger | Purpose |
|----------|---------|---------|
| `classify_event` | Pub/Sub (`cloudhoney-events`) | Evaluates events against detection rules, writes to Firestore |
| `deliver_alert` | Pub/Sub (`cloudhoney-alerts`) | Sends email notifications via SendGrid |

## Detection Rules

- **Brute force:** >10 POST requests to `/login` from same IP within 60 seconds
- **SQL injection:** Known injection strings detected in request payload
- **Port scan:** >8 distinct paths from same IP within 30 seconds
