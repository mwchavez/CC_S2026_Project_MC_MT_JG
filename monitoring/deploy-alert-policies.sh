#!/bin/bash
# =============================================================================
# CloudHoney — Issue #11 Alerting Policies Deploy Script
# =============================================================================
# Creates 3 alerting policies in Cloud Monitoring:
#   1. Honeypot VM down (uptime metric absent)
#   2. Cloud Function error rate > 10%
#   3. Pub/Sub subscription backlog > 100 messages
#
# Notification channel is hardcoded to the team email channel.
# Runbooks are embedded in each policy's documentation field for compliance.
# =============================================================================

set -euo pipefail

CHANNEL="projects/cloudhoney-sp26/notificationChannels/82361167047082583"

echo "==> Creating Policy 1/3: Honeypot VM Down"
cat > /tmp/policy-vm-down.json <<'EOF'
{
  "displayName": "CloudHoney — Honeypot VM Down (CRITICAL)",
  "documentation": {
    "content": "The honeypot VM is no longer reporting uptime metrics, indicating it has crashed, been stopped, or lost network connectivity. The CloudHoney pipeline is offline.\n\n## Runbook\n1. Check Compute Engine console for VM status\n2. SSH via IAP: `gcloud compute ssh honeypot-vm --zone=us-east1-d --tunnel-through-iap`\n3. If unreachable, restart: `gcloud compute instances reset honeypot-vm --zone=us-east1-d`\n4. Verify Flask service after boot: `sudo systemctl status cloudhoney.service`\n5. Confirm logs flowing: `gcloud logging read 'logName=\"projects/cloudhoney-sp26/logs/cloudhoney-events\"' --limit=5`\n\n## Compliance\nMaps to PCI DSS 10.6 (timely review of security events) and FFIEC operational resilience guidance.",
    "mimeType": "text/markdown"
  },
  "userLabels": {
    "issue": "11",
    "severity": "critical",
    "compliance": "pci-dss-10-6"
  },
  "conditions": [{
    "displayName": "VM uptime metric absent for 5 minutes",
    "conditionAbsent": {
      "filter": "metric.type=\"compute.googleapis.com/instance/uptime\" resource.type=\"gce_instance\"",
      "aggregations": [{
        "alignmentPeriod": "60s",
        "perSeriesAligner": "ALIGN_RATE"
      }],
      "duration": "300s",
      "trigger": {"count": 1}
    }
  }],
  "combiner": "OR",
  "enabled": true,
  "alertStrategy": {
    "autoClose": "1800s"
  }
}
EOF
gcloud alpha monitoring policies create \
  --policy-from-file=/tmp/policy-vm-down.json \
  --notification-channels="$CHANNEL"

echo ""
echo "==> Creating Policy 2/3: Cloud Function Error Rate > 10%"
cat > /tmp/policy-function-errors.json <<'EOF'
{
  "displayName": "CloudHoney — Cloud Function Error Rate > 10% (HIGH)",
  "documentation": {
    "content": "One or more Cloud Functions (classify-event, deliver-alert, run-simulator) are failing more than 10% of executions over a 5-minute window. Detection or alerting may be silently broken.\n\n## Runbook\n1. Identify which function: check the alert's resource labels for `function_name`\n2. View recent errors: `gcloud functions logs read <FUNCTION_NAME> --region=us-east1 --limit=50`\n3. Common causes:\n   - IAM permission propagation (wait 60s, retry)\n   - Firestore composite index missing (check Firestore console > Indexes)\n   - SendGrid API key rotated/revoked (check Secret Manager version)\n   - Pub/Sub trigger misconfigured\n4. If transient, monitor next run; if persistent, redeploy: `gcloud functions deploy ...`\n\n## Compliance\nMaps to PCI DSS 11.4 (intrusion detection systems must be operational) — a silently failing classifier is a compliance gap.",
    "mimeType": "text/markdown"
  },
  "userLabels": {
    "issue": "11",
    "severity": "high",
    "compliance": "pci-dss-11-4"
  },
  "conditions": [{
    "displayName": "Function error ratio > 0.10 for 5 min",
    "conditionThreshold": {
      "filter": "metric.type=\"cloudfunctions.googleapis.com/function/execution_count\" resource.type=\"cloud_function\" metric.label.\"status\"!=\"ok\"",
      "aggregations": [{
        "alignmentPeriod": "60s",
        "perSeriesAligner": "ALIGN_RATE",
        "crossSeriesReducer": "REDUCE_SUM",
        "groupByFields": ["resource.label.\"function_name\""]
      }],
      "denominatorFilter": "metric.type=\"cloudfunctions.googleapis.com/function/execution_count\" resource.type=\"cloud_function\"",
      "denominatorAggregations": [{
        "alignmentPeriod": "60s",
        "perSeriesAligner": "ALIGN_RATE",
        "crossSeriesReducer": "REDUCE_SUM",
        "groupByFields": ["resource.label.\"function_name\""]
      }],
      "comparison": "COMPARISON_GT",
      "thresholdValue": 0.10,
      "duration": "300s",
      "trigger": {"count": 1}
    }
  }],
  "combiner": "OR",
  "enabled": true,
  "alertStrategy": {
    "autoClose": "1800s"
  }
}
EOF
gcloud alpha monitoring policies create \
  --policy-from-file=/tmp/policy-function-errors.json \
  --notification-channels="$CHANNEL"

echo ""
echo "==> Creating Policy 3/3: Pub/Sub Subscription Backlog > 100"
cat > /tmp/policy-pubsub-backlog.json <<'EOF'
{
  "displayName": "CloudHoney — Pub/Sub Subscription Backlog > 100 (MEDIUM)",
  "documentation": {
    "content": "A Pub/Sub subscription has more than 100 undelivered messages on average over 5 minutes. The downstream consumer (Cloud Function) is not keeping up, or has stopped processing entirely.\n\n## Runbook\n1. Identify subscription from alert labels (`subscription_id`)\n2. For `cloudhoney-events` topic subscription: check `classify-event` function health\n3. For `cloudhoney-alerts` topic subscription: check `deliver-alert` function health\n4. View function metrics in Cloud Monitoring dashboard 'CloudHoney — Pipeline Health'\n5. If consumer is unhealthy, fix per Policy 2 runbook; backlog should drain automatically\n\n## Compliance\nMaps to FFIEC IT Examination Handbook — Operations Booklet, Section IV (capacity & performance monitoring).",
    "mimeType": "text/markdown"
  },
  "userLabels": {
    "issue": "11",
    "severity": "medium",
    "compliance": "ffiec-ops-iv"
  },
  "conditions": [{
    "displayName": "Undelivered messages > 100 for 5 min",
    "conditionThreshold": {
      "filter": "metric.type=\"pubsub.googleapis.com/subscription/num_undelivered_messages\" resource.type=\"pubsub_subscription\"",
      "aggregations": [{
        "alignmentPeriod": "60s",
        "perSeriesAligner": "ALIGN_MEAN"
      }],
      "comparison": "COMPARISON_GT",
      "thresholdValue": 100,
      "duration": "300s",
      "trigger": {"count": 1}
    }
  }],
  "combiner": "OR",
  "enabled": true,
  "alertStrategy": {
    "autoClose": "1800s"
  }
}
EOF
gcloud alpha monitoring policies create \
  --policy-from-file=/tmp/policy-pubsub-backlog.json \
  --notification-channels="$CHANNEL"

echo ""
echo "============================================================"
echo "✅ All 3 alerting policies created."
echo "============================================================"
echo "Verify with:"
echo "  gcloud alpha monitoring policies list --filter='displayName~CloudHoney' --format='value(displayName,enabled)'"
echo ""
echo "View in Console:"
echo "  https://console.cloud.google.com/monitoring/alerting/policies?project=cloudhoney-sp26"
