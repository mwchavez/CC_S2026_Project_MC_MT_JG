# Visualization Dashboard

Real-time security event dashboard deployed on GCP Cloud Run. Reads classified event data from Firestore and displays live attack metrics.

## Features

- Live event counter (total events processed)
- Attack type breakdown (brute force, port scan, SQL injection)
- Recent events feed (last 20 events with timestamp, type, source IP)
- Alert state highlighting for triggered detection rules

## Deployment

Containerized with Docker and deployed to Cloud Run:

```bash
gcloud run deploy cloudhoney-dashboard \
  --source . \
  --region us-central1 \
  --allow-unauthenticated
```
