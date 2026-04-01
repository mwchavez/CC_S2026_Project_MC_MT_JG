"""
CloudHoney — Honeypot Flask Application
========================================
A lightweight decoy financial institution portal that silently logs
every incoming request as structured JSON and forwards it to GCP
Cloud Logging.

Endpoints:
    /login    — Fake online banking portal login page
    /transfer — Fake wire transfer submission interface
    /payment  — Fake payment API endpoint
    /admin    — Fake back-office administrative panel
    /account  — Fake customer account lookup interface
    /query    — Fake database query interface (bonus SQL injection bait)

IMPORTANT:
    This application NEVER processes, stores, or echoes back any real
    financial data. All form fields are captured as log entries only.
    No real authentication or financial operations are performed.

    PCI DSS Requirement 3 Compliance Note:
    This system does not store sensitive authentication data after
    authorization because it never performs authorization at all.
    All captured payloads are treated as honeypot telemetry, not
    cardholder data.
"""

import json
import logging
import os
from datetime import datetime, timezone

from flask import Flask, request, render_template, render_template_string, jsonify

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

# Toggle GCP Cloud Logging integration.  Set to "true" when deployed on
# Compute Engine with the cloudhoney-app-sa service account attached.
# When running locally for development, leave as "false" to log to stdout.
ENABLE_GCP_LOGGING = os.environ.get("ENABLE_GCP_LOGGING", "false").lower() == "true"

# Custom log name used in Cloud Logging — this is what the Log Sink in
# Issue #5 will filter on to route events to Cloud Storage and Pub/Sub.
GCP_LOG_NAME = os.environ.get("GCP_LOG_NAME", "cloudhoney-events")

# ---------------------------------------------------------------------------
# Logging Setup
# ---------------------------------------------------------------------------

app = Flask(__name__)

# Silence default Flask/Werkzeug request logs so they don't pollute our
# structured event stream.
logging.getLogger("werkzeug").setLevel(logging.WARNING)

# Local structured logger (always active — useful for development)
logger = logging.getLogger("cloudhoney")
logger.setLevel(logging.INFO)

_stream_handler = logging.StreamHandler()
_stream_handler.setFormatter(logging.Formatter("%(message)s"))
logger.addHandler(_stream_handler)

# GCP Cloud Logging client (conditionally initialized)
_gcp_logger = None

if ENABLE_GCP_LOGGING:
    try:
        from google.cloud import logging as gcp_logging

        _gcp_client = gcp_logging.Client()
        _gcp_logger = _gcp_client.logger(GCP_LOG_NAME)
        logger.info(
            json.dumps({
                "event": "gcp_logging_initialized",
                "log_name": GCP_LOG_NAME,
                "message": "GCP Cloud Logging is active."
            })
        )
    except Exception as exc:
        logger.warning(
            json.dumps({
                "event": "gcp_logging_init_failed",
                "error": str(exc),
                "message": "Falling back to local logging only."
            })
        )

# ---------------------------------------------------------------------------
# Core Logging Function
# ---------------------------------------------------------------------------

# Security-relevant headers worth capturing for threat analysis.
# These are used by the Cloud Functions detection rules in Issue #8
# to identify patterns like rotating user agents during credential
# stuffing or suspicious origin headers.
SECURITY_HEADERS = [
    "User-Agent",
    "X-Forwarded-For",
    "X-Real-IP",
    "Referer",
    "Origin",
    "Authorization",
    "Content-Type",
    "Accept",
    "Cookie",
    "Host",
]


def log_honeypot_event(endpoint_name: str, attack_context: str = "") -> dict:
    """Capture every detail of the incoming request and emit a structured
    JSON log entry to both local stdout and GCP Cloud Logging (if enabled).

    This is the core function of the honeypot. Every single request
    that hits any endpoint gets recorded with:
    - timestamp:       when it happened (UTC, ISO 8601)
    - source_ip:       where it came from
    - method:          GET, POST, etc.
    - path:            which URL they hit (/login, /transfer, /payment, etc.)
    - endpoint:        our internal label for which decoy they triggered
    - user_agent:      what tool or browser they claim to be using
    - payload:         whatever data they sent (form fields, JSON, raw body)
    - headers:         security-relevant HTTP headers
    - query_params:    URL query string parameters
    - attack_context:  our label for what type of activity this looks like

    The structured JSON format is critical because downstream services
    (Cloud Functions in Issue #8) will parse these fields to run
    detection rules.

    Args:
        endpoint_name:  Human-readable label for the triggered endpoint
                        (e.g., "login", "transfer").
        attack_context: Descriptive label for the suspected attack type
                        (e.g., "brute_force_attempt", "sql_injection_attempt").
                        Used for enriching Firestore documents in Issue #8.

    Returns:
        The structured event dict (useful for unit testing).
    """
    # Build the payload — try form data first, then JSON, then raw body.
    payload = {}
    if request.form:
        payload = {k: v for k, v in request.form.items()}
    elif request.is_json:
        payload = request.get_json(silent=True) or {}
    else:
        raw = request.get_data(as_text=True)
        if raw:
            payload = {"raw_body": raw}

    # Capture selected security-relevant headers.
    captured_headers = {
        h: request.headers.get(h)
        for h in SECURITY_HEADERS
        if request.headers.get(h)
    }

    event = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "source_ip": request.remote_addr,
        "method": request.method,
        "path": request.path,
        "endpoint": endpoint_name,
        "user_agent": request.headers.get("User-Agent", "unknown"),
        "payload": payload,
        "headers": captured_headers,
        "query_params": dict(request.args) if request.args else {},
        "attack_context": attack_context,
    }

    # --- Emit to local logger (always) ---
    logger.info(json.dumps(event, default=str))

    # --- Emit to GCP Cloud Logging (if enabled) ---
    if _gcp_logger:
        try:
            _gcp_logger.log_struct(
                event,
                severity="INFO",
            )
        except Exception as exc:
            logger.error(
                json.dumps({
                    "event": "gcp_log_write_failed",
                    "error": str(exc),
                })
            )

    return event


# ---------------------------------------------------------------------------
# Fake Database Query Template (inline — bonus endpoint)
# ---------------------------------------------------------------------------

QUERY_PAGE = """
<!DOCTYPE html>
<html>
<head><title>Database Query Interface</title>
<style>
    body { font-family: 'Courier New', monospace; background: #0c0c0c; color: #00ff41;
           padding: 24px; margin: 0; }
    h2 { color: #00ff41; border-bottom: 1px solid #333; padding-bottom: 8px; }
    textarea { width: 100%; height: 120px; background: #1a1a1a; color: #00ff41;
               border: 1px solid #333; padding: 12px; font-family: 'Courier New', monospace;
               font-size: 14px; border-radius: 4px; box-sizing: border-box; }
    button { padding: 10px 24px; background: #00ff41; color: #0c0c0c; border: none;
             font-family: 'Courier New', monospace; font-weight: bold; cursor: pointer;
             border-radius: 4px; margin-top: 8px; }
    .info { color: #666; font-size: 12px; margin-top: 16px; }
    .result { background: #1a1a1a; border: 1px solid #333; padding: 12px;
              margin-top: 16px; border-radius: 4px; white-space: pre-wrap; }
</style>
</head>
<body>
    <h2>$ database_query_interface v2.4.1</h2>
    <p>Connected to: prod-db-01.internal (PostgreSQL 15.2)</p>
    <form method="POST" action="/query">
        <textarea name="query" placeholder="Enter SQL query...">{{ query }}</textarea>
        <br>
        <button type="submit">Execute Query</button>
    </form>
    {% if query %}
    <div class="result">ERROR 1045: Access denied for user 'app_readonly'@'10.0.0.5'
Permission denied. This incident has been logged.</div>
    {% endif %}
    <div class="info">Read-only access. Contact DBA team for write permissions.</div>
</body>
</html>
"""


# ---------------------------------------------------------------------------
# Health Check (not a honeypot endpoint — used for operational monitoring)
# ---------------------------------------------------------------------------

@app.route("/health")
def health():
    """Simple health check for Cloud Monitoring uptime checks (Issue #11)."""
    return jsonify({"status": "ok"}), 200


# ---------------------------------------------------------------------------
# Honeypot Endpoints
# ---------------------------------------------------------------------------

# --- 1. /login — Fake Online Banking Portal ---

@app.route("/login", methods=["GET", "POST"])
def login():
    """Simulates an online banking portal login page.

    GET  → Renders a fake bank login form (reconnaissance).
    POST → Captures submitted credentials and logs the event.
           Returns a fake 'invalid credentials' response (never authenticates).
    """
    if request.method == "POST":
        log_honeypot_event("login", attack_context="brute_force_attempt")
        return render_template(
            "login.html",
            error="Invalid username or password. Please try again.",
        ), 401
    else:
        log_honeypot_event("login", attack_context="login_page_visit")
        return render_template("login.html")


# --- 2. /transfer — Fake Wire Transfer Interface ---

@app.route("/transfer", methods=["GET", "POST"])
def transfer():
    """Simulates a wire transfer submission page.

    GET  → Renders a fake wire transfer form (reconnaissance).
    POST → Captures account numbers, routing numbers, and amounts.
           Returns a fake 'transfer pending' response.
    """
    if request.method == "POST":
        log_honeypot_event("transfer", attack_context="wire_transfer_probe")
        return render_template(
            "transfer.html",
            message="Transfer submitted. Pending verification.",
        )
    else:
        log_honeypot_event("transfer", attack_context="transfer_page_visit")
        return render_template("transfer.html")


# --- 3. /payment — Fake Payment API Endpoint ---

@app.route("/payment", methods=["GET", "POST"])
def payment():
    """Simulates a payment processing API endpoint.

    GET  → Returns API documentation page (decoy/reconnaissance).
    POST → Captures card data, merchant info, amounts.
           Returns a fake JSON API response.
    """
    if request.method == "POST":
        log_honeypot_event("payment", attack_context="payment_api_abuse")
        return jsonify({
            "status": "processing",
            "transaction_id": "TXN-FAKE-0000000",
            "message": "Payment is being processed. Please allow 1-2 business days.",
        }), 202
    else:
        log_honeypot_event("payment", attack_context="payment_page_visit")
        return render_template("payment.html")


# --- 4. /admin — Fake Back-Office Administrative Panel ---

@app.route("/admin", methods=["GET", "POST"])
def admin():
    """Simulates a back-office admin panel.

    GET  → Renders a fake admin login form (reconnaissance).
    POST → Captures admin credentials and logs the event.
           Returns a fake 'access denied' response.
    """
    if request.method == "POST":
        log_honeypot_event("admin", attack_context="admin_exploit_attempt")
        return render_template(
            "admin.html",
            error="Access denied. This incident has been reported.",
        ), 403
    else:
        log_honeypot_event("admin", attack_context="admin_page_visit")
        return render_template("admin.html")


# --- 5. /account — Fake Customer Account Lookup ---

@app.route("/account", methods=["GET", "POST"])
def account():
    """Simulates a customer account lookup interface.

    GET  → Renders an account lookup form (reconnaissance).
    POST → Captures account ID / SSN-like input and logs the event.
           Returns a fake 'account not found' response.
    """
    if request.method == "POST":
        log_honeypot_event("account", attack_context="account_takeover_recon")
        return render_template(
            "account.html",
            error="Account not found. Please verify your information.",
        ), 404
    else:
        log_honeypot_event("account", attack_context="account_page_visit")
        return render_template("account.html")


# --- 6. /query — Fake Database Query Interface (Bonus SQL Injection Bait) ---

@app.route("/query", methods=["GET", "POST"])
def query():
    """Simulates an exposed database query interface.

    This is a bonus endpoint not in the original proposal — a page that
    looks like it accepts raw SQL.  It's the juiciest bait for attackers
    testing for SQL injection.  Cloud Functions detection rules (Issue #8)
    will scan these payloads for injection patterns.

    GET  → Shows the fake query interface (reconnaissance).
    POST → Captures the submitted query string and logs it.
    """
    submitted_query = ""
    if request.method == "POST":
        submitted_query = request.form.get("query", "")
        log_honeypot_event("query", attack_context="sql_injection_attempt")
    else:
        log_honeypot_event("query", attack_context="query_page_visit")

    return render_template_string(QUERY_PAGE, query=submitted_query)


# ---------------------------------------------------------------------------
# Catch-All Route (logs ANY other path an attacker probes)
# ---------------------------------------------------------------------------

@app.route("/", defaults={"path": ""})
@app.route("/<path:path>", methods=["GET", "POST", "PUT", "DELETE"])
def catch_all(path):
    """Catches requests to any path not explicitly defined above.

    Attackers running port scans will hit paths like /api, /config,
    /debug, /.env, /wp-admin, /ssh, etc.  Every one of those requests
    gets logged.  This is critical for the port scan detection rule
    in Issue #8 (8+ distinct paths from same IP within 30 seconds).
    """
    log_honeypot_event("catch_all", attack_context="path_probe")
    return render_template("404.html"), 404


# ---------------------------------------------------------------------------
# Entry Point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))

    print("=" * 60)
    print("  CloudHoney Honeypot")
    print(f"  Logging to: {'GCP Cloud Logging' if ENABLE_GCP_LOGGING else 'Terminal (local dev)'}")
    print(f"  Log name:   {GCP_LOG_NAME}")
    print("=" * 60)
    print()
    print("  Financial Sector Endpoints:")
    print(f"    http://localhost:{port}/login     — Fake banking portal login")
    print(f"    http://localhost:{port}/transfer  — Fake wire transfer form")
    print(f"    http://localhost:{port}/payment   — Fake payment API")
    print(f"    http://localhost:{port}/admin     — Fake admin panel")
    print(f"    http://localhost:{port}/account   — Fake account lookup")
    print(f"    http://localhost:{port}/query     — Fake DB query interface")
    print()
    print("  Utility:")
    print(f"    http://localhost:{port}/health    — Health check")
    print(f"    http://localhost:{port}/*         — Catch-all (port scan logging)")
    print()

    # host="0.0.0.0" makes the app accessible from outside the VM
    # (required for the traffic generator to reach it over the VPC).
    # debug=False ALWAYS in production — Flask debug mode exposes an
    # interactive debugger that lets anyone execute arbitrary Python.
    app.run(
        host="0.0.0.0",
        port=port,
        debug=os.environ.get("FLASK_DEBUG", "false").lower() == "true",
    )
