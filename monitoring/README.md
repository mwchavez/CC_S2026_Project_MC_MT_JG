# Monitoring

Infrastructure-as-code for CloudHoney's Cloud Monitoring stack. Everything in this folder reproduces the dashboard and alerting policies from Issue #11.

## Contents

| File | Purpose |
|------|---------|
| `dashboard.json` | Custom dashboard config — 8 widgets covering VM, Cloud Functions, Pub/Sub, Firestore |
| `deploy-alert-policies.sh` | Bash script that creates 3 alerting policies (VM down, function error rate, Pub/Sub backlog) with embedded runbooks |

## Architecture

CloudHoney uses two layers of observability:

1. **Security dashboard** (Cloud Run, see `/dashboard`) — shows attack events: who hit which honeypot endpoint, what attack type, what severity. Built for the SOC operator.
2. **Pipeline health dashboard** (Cloud Monitoring, this folder) — shows infrastructure metrics: is the VM up, are functions running, is Pub/Sub draining. Built for the platform operator.

The two are intentionally separate. Security data answers *"are we under attack?"* — operations data answers *"is our detection system working?"* A financial-sector SOC needs both.

## Deploy

Both artifacts assume:
- Project: `cloudhoney-sp26`
- Region: `us-east1`
- Notification channel exists (created via `gcloud beta monitoring channels create`)

### Dashboard

```bash
gcloud monitoring dashboards create --config-from-file=dashboard.json
```

### Alerting policies

The script has the channel ID hardcoded. Update `CHANNEL=` at the top of the script if you redeploy with a different channel.

```bash
chmod +x deploy-alert-policies.sh
./deploy-alert-policies.sh
```

### Verify

```bash
gcloud monitoring dashboards list --filter='displayName:CloudHoney'
gcloud alpha monitoring policies list --filter='displayName~CloudHoney' \
  --format='table(displayName,enabled)'
```

## Prerequisite — Ops Agent on honeypot-vm

Memory utilization metrics require the Google Cloud Ops Agent installed on the VM. One-time setup:

```bash
gcloud compute ssh honeypot-vm --zone=us-east1-d --tunnel-through-iap

# On the VM:
curl -sSO https://dl.google.com/cloudagents/add-google-cloud-ops-agent-repo.sh
sudo bash add-google-cloud-ops-agent-repo.sh --also-install
sudo systemctl status google-cloud-ops-agent
```

CPU, disk, and network metrics work without the agent — only memory and process metrics require it.

## Alerting policies — overview

| Policy | Trigger | Severity | Compliance Mapping |
|--------|---------|----------|--------------------|
| Honeypot VM Down | `compute.googleapis.com/instance/uptime` absent for 5 min | CRITICAL | PCI DSS 10.6 |
| Cloud Function Error Rate | error ratio > 10% over 5 min | HIGH | PCI DSS 11.4 |
| Pub/Sub Subscription Backlog | undelivered messages > 100 for 5 min | MEDIUM | FFIEC Ops IV |

Each policy includes a documented runbook in its `documentation` field — operators can read response procedures directly from the alert.

## Design decisions

**Why metric-absence instead of HTTP uptime check for VM Down.** The honeypot VM is locked down — SSH is IAP-only, Flask port 5000 is firewall-restricted to the function subnet (`10.0.2.0/24`). A public uptime check would require either (a) opening the firewall to Google's uptime probe IPs, increasing the attack surface, or (b) running a probe from inside the VPC, which adds infrastructure. Detecting absence of the `instance/uptime` metric requires no firewall changes and is functionally equivalent.

**Why ratio condition for function errors.** A flat error count would page on every retry storm even with healthy throughput. Ratio (`errors / total executions`) only fires when the system is actually broken proportional to its load.

**Why 100 messages for Pub/Sub backlog.** CloudHoney processes at most ~50 messages per simulator run. Sustained backlog > 100 indicates the consumer (Cloud Function) is stuck, not just under temporary load.

## Cost

All Cloud Monitoring resources used here are within the free tier:
- All GCP-native metrics: free
- Custom metrics: 150 MiB/month free (Ops Agent uses ~50 KB/month)
- Dashboards: unlimited, free
- Alerting policies: unlimited, free
- Email notification channels: free
- Uptime checks: 1M executions/month free (none used)

## Compliance notes

- **PCI DSS Req 10.6** (review of logs and security events): alerts deliver actionable notifications within ~2 min of anomaly
- **PCI DSS Req 11.4** (operational intrusion detection): error-rate alert catches silent classifier failures
- **FFIEC IT Examination Handbook — Operations Booklet, Section IV**: Pub/Sub backlog alert satisfies capacity & performance monitoring requirement
- **Documented runbooks** embedded in each policy satisfy the "incident response procedures must be tested and documented" framework

## Related

- `/dashboard` — the user-facing security dashboard (Cloud Run, Issue #10)
- `/functions` — Cloud Functions monitored by Policy 2
- See the [Architecture > Monitoring Wiki page](../../../wiki/Architecture-Monitoring) for the full write-up
