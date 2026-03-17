# Honeypot Flask Application

Lightweight Flask web application deployed on GCP Compute Engine that acts as a decoy target for simulated attacks.

## Endpoints

| Route | Method | Purpose |
|-------|--------|---------|
| `/login` | GET/POST | Fake SSH/admin login page |
| `/admin` | GET/POST | Fake admin dashboard |
| `/query` | GET/POST | Fake database query interface |

## Logging

Every incoming request is captured as structured JSON and forwarded to GCP Cloud Logging:

- Timestamp
- Source IP address
- HTTP method and path
- User-Agent header
- Full request payload/body

## Local Development

```bash
pip install -r requirements.txt
python app.py
```

The app runs on `http://localhost:5000` by default.
