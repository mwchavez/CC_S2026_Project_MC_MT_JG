# Honeypot Flask Application

Lightweight Flask web application deployed on GCP Compute Engine inside a custom VPC Network. Acts as a decoy financial institution portal — simulating the internet-facing infrastructure of a bank to lure and log simulated attack traffic.

---

## Endpoints

| Route | Method | Purpose |
|---|---|---|
| `/login` | GET/POST | Fake online banking login portal |
| `/transfer` | GET/POST | Fake wire transfer submission interface |
| `/payment` | GET/POST | Fake payment API endpoint |
| `/admin` | GET/POST | Fake back-office administrative panel |
| `/account` | GET/POST | Fake customer account lookup interface |

> None of these endpoints perform any real authentication or financial operations. They exist solely to log attacker behavior.

---

## Logging

Every incoming request is captured as structured JSON and forwarded to GCP Cloud Logging:

- Timestamp
- Source IP address
- HTTP method and path
- User-Agent header
- Full request payload/body

Log entries use the custom log name `cloudhoney-events` so they can be filtered and routed downstream by the Cloud Logging sink.

---

## Detection Targets

This honeypot is designed to surface the following financial sector attack patterns:

- **Credential stuffing** — repeated POST attempts to `/login` with varied username/password pairs
- **Wire fraud probing** — requests to `/transfer` with manipulated routing or account number patterns
- **Payment API abuse** — malformed or injected payloads sent to `/payment`
- **Account takeover recon** — repeated probing of `/account` for session or token weaknesses
- **Port scanning** — rapid requests across all exposed paths from a single IP

---

## Local Development

```bash
pip install -r requirements.txt
python app.py
```

The app runs on `http://localhost:5000` by default.

> **Note:** When running locally, logs print to the terminal as structured JSON. Cloud Logging integration is only active when the app is running on the Compute Engine VM with the CloudHoney Service Account attached.

---

## Deployment

This application is deployed on a GCP Compute Engine `e2-micro` VM inside a custom VPC Network. See `/infra` for setup scripts and firewall configuration.

- The VM runs with a least-privilege Service Account that allows writes to Cloud Logging
- Inbound traffic is restricted by VPC firewall rules to expected sources only
- The app runs persistently via `systemd` and survives reboots
