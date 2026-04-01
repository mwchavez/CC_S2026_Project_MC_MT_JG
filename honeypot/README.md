# CloudHoney — Honeypot Flask Application

> **Decoy financial institution portal** that silently logs every incoming request as structured JSON.  
> No real authentication or financial operations are performed.

---

## Quick Start (Local Development)

```bash
# 1. Create a virtual environment (recommended)
python3 -m venv venv
source venv/bin/activate        # Linux/Mac
# venv\Scripts\activate         # Windows

# 2. Install dependencies
pip install -r requirements.txt

# 3. Run the app
python app.py
```

The app starts on **http://localhost:5000**.  Every request to any endpoint produces a structured JSON log entry in the terminal.

---

## Endpoints

| Path        | Method    | Description                                            |
|-------------|-----------|--------------------------------------------------------|
| `/login`    | GET/POST  | Fake online banking login portal                       |
| `/transfer` | GET/POST  | Fake wire transfer submission form                     |
| `/payment`  | GET/POST  | Fake payment processing API endpoint                   |
| `/admin`    | GET/POST  | Fake back-office administrative panel                  |
| `/account`  | GET/POST  | Fake customer account lookup interface                 |
| `/query`    | GET/POST  | Fake database query interface (bonus SQL injection bait) |
| `/health`   | GET       | Operational health check (not a honeypot target)       |
| `/*`        | GET       | Catch-all — logs any other probed path (404)           |

---

## Environment Variables

| Variable             | Default              | Description                                                 |
|----------------------|----------------------|-------------------------------------------------------------|
| `ENABLE_GCP_LOGGING` | `false`              | Set to `true` on Compute Engine to forward logs to GCP      |
| `GCP_LOG_NAME`       | `cloudhoney-events`  | Custom log name used in Cloud Logging (matches Log Sink)    |
| `PORT`               | `5000`               | Port the Flask app listens on                               |
| `FLASK_DEBUG`        | `false`              | Enable Flask debug mode (local dev only — never in prod)    |

---

## Log Format

Every request produces a JSON entry like this:

```json
{
  "timestamp": "2026-02-10T14:32:05.123456+00:00",
  "source_ip": "10.0.1.50",
  "method": "POST",
  "path": "/login",
  "endpoint": "login",
  "user_agent": "Mozilla/5.0 (compatible; stuffing-tool/1.0)",
  "payload": {
    "username": "jsmith",
    "password": "Summer2024!"
  },
  "headers": {
    "User-Agent": "Mozilla/5.0 (compatible; stuffing-tool/1.0)",
    "Content-Type": "application/x-www-form-urlencoded"
  },
  "query_params": {},
  "attack_context": "brute_force_attempt"
}
```

### Attack Context Labels

Each log entry includes an `attack_context` field describing the suspected activity type. This enriches the data for downstream Cloud Functions processing (Issue #8) and Firestore queries (Issue #10).

| Context Label              | Triggered By                                      |
|----------------------------|---------------------------------------------------|
| `login_page_visit`         | GET request to `/login`                           |
| `brute_force_attempt`      | POST request to `/login` (credential submission)  |
| `transfer_page_visit`      | GET request to `/transfer`                        |
| `wire_transfer_probe`      | POST request to `/transfer` (financial data)      |
| `payment_page_visit`       | GET request to `/payment`                         |
| `payment_api_abuse`        | POST request to `/payment` (card/merchant data)   |
| `admin_page_visit`         | GET request to `/admin`                           |
| `admin_exploit_attempt`    | POST request to `/admin` (admin action attempt)   |
| `account_page_visit`       | GET request to `/account`                         |
| `account_takeover_recon`   | POST request to `/account` (account ID/SSN)       |
| `query_page_visit`         | GET request to `/query`                           |
| `sql_injection_attempt`    | POST request to `/query` (SQL query submission)   |
| `path_probe`               | Any request to an undefined path (port scanning)  |

---

## Deployment to GCP Compute Engine

See **Issue #4** in the GitHub Project board for full deployment instructions.  Summary:

1. SSH into the VM inside `cloudhoney-vpc`
2. Clone the repo, install deps
3. Set environment: `export ENABLE_GCP_LOGGING=true`
4. Run with gunicorn: `gunicorn -b 0.0.0.0:5000 app:app`
5. (Better) Configure as a `systemd` service for persistence

---

## Compliance Notes

| Framework          | Requirement | How CloudHoney Addresses It                                         |
|--------------------|-------------|----------------------------------------------------------------------|
| PCI DSS Req 3      | No storage of sensitive auth data after authorization | Honeypot never authorizes — payloads are telemetry only |
| PCI DSS Req 6.4.3  | No credentials in source code | All secrets managed via GCP Secret Manager |
| GLBA Safeguards    | Monitor access to customer financial information | All access is logged as structured JSON events |
