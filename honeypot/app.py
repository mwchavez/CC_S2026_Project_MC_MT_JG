"""
CloudHoney — Honeypot Flask Application

A lightweight decoy web application that exposes fake login, admin,
and database query endpoints. Every incoming request is captured as
structured JSON and forwarded to GCP Cloud Logging when running in
the cloud, or printed to the terminal when running locally.

This application does NOT perform any real authentication or database
operations. It exists solely to attract and log simulated attack traffic.
"""

import json
import logging
import os
from datetime import datetime, timezone

from flask import Flask, request, render_template_string

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

# When running on the GCP VM, set ENVIRONMENT=production to enable Cloud Logging.
# Locally, it defaults to "development" and logs to the terminal instead.
ENVIRONMENT = os.environ.get("ENVIRONMENT", "development")

app = Flask(__name__)

# ---------------------------------------------------------------------------
# Logging Setup
# ---------------------------------------------------------------------------

def setup_logging():
    """
    Configure logging based on environment.

    In production (on the GCP VM), this uses the google-cloud-logging
    library to send structured logs directly to GCP Cloud Logging.
    Think of Cloud Logging as GCP's equivalent of AWS CloudWatch Logs.

    In development (your laptop), it just prints JSON to the terminal
    so you can see what's happening without needing a GCP connection.
    """
    if ENVIRONMENT == "production":
        import google.cloud.logging
        client = google.cloud.logging.Client()
        client.setup_logging()

    logger = logging.getLogger("cloudhoney")
    logger.setLevel(logging.INFO)

    # If no handlers exist yet (development mode), add a console handler
    if not logger.handlers and ENVIRONMENT == "development":
        handler = logging.StreamHandler()
        handler.setLevel(logging.INFO)
        logger.addHandler(handler)

    return logger

logger = setup_logging()

# ---------------------------------------------------------------------------
# Request Logging (the "hidden camera" that records everything)
# ---------------------------------------------------------------------------

def log_request(attack_context=""):
    """
    Capture every detail of an incoming request as structured JSON.

    This is the core function of the honeypot. Every single request
    that hits any endpoint gets recorded with:
    - timestamp: when it happened (UTC)
    - source_ip: where it came from
    - method: GET, POST, etc.
    - path: which URL they hit (/login, /admin, /query)
    - user_agent: what tool or browser they claim to be using
    - payload: whatever data they sent (form fields, query params)
    - attack_context: our label for what type of activity this looks like

    The structured JSON format is critical because downstream services
    (Cloud Functions in Issue #8) will parse these fields to run
    detection rules.
    """
    # Get form data if it's a POST, or query parameters if it's a GET
    if request.method == "POST":
        payload = request.form.to_dict() or request.get_json(silent=True) or {}
    else:
        payload = request.args.to_dict()

    log_entry = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "source_ip": request.remote_addr,
        "method": request.method,
        "path": request.path,
        "user_agent": request.headers.get("User-Agent", "unknown"),
        "payload": payload,
        "attack_context": attack_context,
    }

    # Log as a JSON string so it stays structured end-to-end
    logger.info(json.dumps(log_entry))

    return log_entry

# ---------------------------------------------------------------------------
# HTML Templates (the "fake storefront" that looks real)
# ---------------------------------------------------------------------------
# These are intentionally simple but realistic-looking pages.
# An attacker scanning the internet would see these and think
# they found an exposed admin panel or login page.

LOGIN_PAGE = """
<!DOCTYPE html>
<html>
<head><title>System Login</title>
<style>
    body { font-family: Arial, sans-serif; background: #1a1a2e; color: #eee;
           display: flex; justify-content: center; align-items: center;
           min-height: 100vh; margin: 0; }
    .login-box { background: #16213e; padding: 40px; border-radius: 8px;
                 width: 320px; box-shadow: 0 0 20px rgba(0,0,0,0.5); }
    h2 { text-align: center; color: #0f3460; margin-bottom: 24px; }
    input { width: 100%; padding: 10px; margin: 8px 0; border: 1px solid #0f3460;
            border-radius: 4px; background: #1a1a2e; color: #eee; box-sizing: border-box; }
    button { width: 100%; padding: 12px; background: #e94560; color: white;
             border: none; border-radius: 4px; cursor: pointer; font-size: 14px;
             margin-top: 12px; }
    .footer { text-align: center; margin-top: 16px; font-size: 11px; color: #555; }
</style>
</head>
<body>
    <div class="login-box">
        <h2>SSH Gateway Login</h2>
        <form method="POST" action="/login">
            <input type="text" name="username" placeholder="Username" required>
            <input type="password" name="password" placeholder="Password" required>
            <button type="submit">Sign In</button>
        </form>
        <div class="footer">Authorized personnel only. All access is logged.</div>
    </div>
</body>
</html>
"""

ADMIN_PAGE = """
<!DOCTYPE html>
<html>
<head><title>Admin Panel</title>
<style>
    body { font-family: Arial, sans-serif; background: #0d1117; color: #c9d1d9; margin: 0; }
    .navbar { background: #161b22; padding: 12px 24px; border-bottom: 1px solid #30363d; }
    .navbar h3 { margin: 0; color: #58a6ff; }
    .content { padding: 24px; }
    .card { background: #161b22; border: 1px solid #30363d; border-radius: 6px;
            padding: 20px; margin: 12px 0; }
    .card h4 { color: #58a6ff; margin-top: 0; }
    .status { color: #3fb950; }
    form input, form select { padding: 8px; margin: 4px; background: #0d1117;
                               border: 1px solid #30363d; color: #c9d1d9; border-radius: 4px; }
    form button { padding: 8px 16px; background: #238636; color: white;
                  border: none; border-radius: 4px; cursor: pointer; }
</style>
</head>
<body>
    <div class="navbar"><h3>CloudHoney Admin Panel</h3></div>
    <div class="content">
        <div class="card">
            <h4>System Status</h4>
            <p>Server: <span class="status">ONLINE</span></p>
            <p>Database: <span class="status">CONNECTED</span></p>
            <p>Last backup: 2026-03-15 02:00 UTC</p>
        </div>
        <div class="card">
            <h4>User Management</h4>
            <form method="POST" action="/admin">
                <input type="text" name="action" placeholder="Action (create/delete/modify)">
                <input type="text" name="target_user" placeholder="Username">
                <input type="text" name="role" placeholder="Role">
                <button type="submit">Execute</button>
            </form>
        </div>
        <div class="card">
            <h4>Server Configuration</h4>
            <form method="POST" action="/admin">
                <input type="text" name="config_key" placeholder="Config key">
                <input type="text" name="config_value" placeholder="Config value">
                <button type="submit">Update</button>
            </form>
        </div>
    </div>
</body>
</html>
"""

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
# Routes (the decoy endpoints)
# ---------------------------------------------------------------------------

@app.route("/")
def index():
    """
    Root endpoint. Redirects scanners toward the login page.
    Even this visit gets logged — it tells us someone found the server.
    """
    log_request(attack_context="reconnaissance")
    return render_template_string(LOGIN_PAGE)


@app.route("/login", methods=["GET", "POST"])
def login():
    """
    Fake login page.
    GET  = someone is viewing the login form (reconnaissance)
    POST = someone is submitting credentials (potential brute force)

    The page looks like an SSH gateway login. We never actually
    authenticate anyone — every attempt gets logged and rejected.
    """
    if request.method == "POST":
        log_request(attack_context="brute_force_attempt")
        # Always return a fake "invalid credentials" message
        return render_template_string(LOGIN_PAGE + """
            <script>alert('Invalid credentials. This attempt has been recorded.');</script>
        """), 401
    else:
        log_request(attack_context="login_page_visit")
        return render_template_string(LOGIN_PAGE)


@app.route("/admin", methods=["GET", "POST"])
def admin():
    """
    Fake admin panel.
    GET  = someone found the admin page (reconnaissance)
    POST = someone is trying to execute admin actions

    This is designed to look like a real management interface.
    Attackers who find /admin pages often try to exploit them.
    """
    if request.method == "POST":
        log_request(attack_context="admin_exploit_attempt")
        return render_template_string(ADMIN_PAGE), 403
    else:
        log_request(attack_context="admin_page_visit")
        return render_template_string(ADMIN_PAGE)


@app.route("/query", methods=["GET", "POST"])
def query():
    """
    Fake database query interface.
    GET  = someone found the query page (reconnaissance)
    POST = someone is submitting a query (potential SQL injection)

    This is the juiciest target for attackers — a page that looks
    like it accepts raw SQL. The Cloud Functions detection rules
    (Issue #8) will scan these payloads for injection patterns.
    """
    submitted_query = ""
    if request.method == "POST":
        submitted_query = request.form.get("query", "")
        log_request(attack_context="sql_injection_attempt")
    else:
        log_request(attack_context="query_page_visit")

    return render_template_string(QUERY_PAGE, query=submitted_query)


# Catch-all for any other paths (attackers often probe random URLs)
@app.route("/<path:path>", methods=["GET", "POST", "PUT", "DELETE"])
def catch_all(path):
    """
    Catch any request to a path we haven't explicitly defined.
    Attackers running port scans will hit paths like /ssh, /api,
    /wp-admin, /.env, etc. We want to log all of those too.
    """
    log_request(attack_context="path_probe")
    return json.dumps({"error": "not found"}), 404, {"Content-Type": "application/json"}


# ---------------------------------------------------------------------------
# Run the app
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    print("=" * 60)
    print("  CloudHoney Honeypot")
    print(f"  Environment: {ENVIRONMENT}")
    print(f"  Logging to: {'GCP Cloud Logging' if ENVIRONMENT == 'production' else 'Terminal'}")
    print("=" * 60)
    print()
    print("  Endpoints:")
    print("    http://localhost:5000/login  — Fake SSH login")
    print("    http://localhost:5000/admin  — Fake admin panel")
    print("    http://localhost:5000/query  — Fake DB query interface")
    print()

    # host="0.0.0.0" makes the app accessible from outside the machine,
    # which is necessary when running on the GCP VM so the traffic
    # generator can reach it. debug=True gives you auto-reload during
    # development but should be False in production.
    app.run(
        host="0.0.0.0",
        port=5000,
        debug=(ENVIRONMENT == "development"),
    )
