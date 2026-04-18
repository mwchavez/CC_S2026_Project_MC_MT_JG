"""
CloudHoney — classify_event Cloud Function
CIS 4355 Cloud Computing | Spring 2026

Triggered by Pub/Sub messages from Cloud Logging (via the cloudhoney-pubsub-sink).
Each message contains a single honeypot log entry.

This function:
  1. Parses the log entry from the Pub/Sub message
  2. Classifies the event against 5 financial sector detection rules
  3. Writes every classified event to Firestore (events collection)
  4. Checks thresholds for count-based rules (credential stuffing, port scan)
  5. Publishes an alert to cloudhoney-alerts Pub/Sub topic when a rule fires

Detection Rules (modeled on PCI DSS 10.6 / 11.4 and FFIEC guidance):
  - Credential stuffing: >10 POST /login from same IP within 60 seconds   → HIGH
  - Wire fraud probe:   /transfer or /payment with manipulated patterns   → HIGH
  - SQL injection:      injection strings in any payload                  → HIGH
  - Port scan:          >8 distinct paths from same IP within 30 seconds  → MEDIUM
  - Account takeover:   /account with sequential IDs or token probing     → MEDIUM
"""

import base64
import json
import os
import re
from datetime import datetime, timedelta, timezone

import functions_framework
from google.cloud import firestore
from google.cloud import pubsub_v1


# =============================================================================
# CONFIGURATION
# =============================================================================

PROJECT_ID = os.environ.get("GCP_PROJECT", "cloudhoney-sp26")
ALERTS_TOPIC = f"projects/{PROJECT_ID}/topics/cloudhoney-alerts"

# Threshold settings — tuned to match simulator behavior
CREDENTIAL_STUFFING_THRESHOLD = 10   # attempts in window
CREDENTIAL_STUFFING_WINDOW_SEC = 60  # seconds

PORT_SCAN_THRESHOLD = 8              # distinct paths in window
PORT_SCAN_WINDOW_SEC = 30            # seconds


# =============================================================================
# DETECTION PATTERNS
# =============================================================================

# SQL injection strings — lowercase for case-insensitive matching
# These map directly to payloads in simulator.py's wire_transfer_probe
# and payment_api_abuse scenarios
SQL_INJECTION_PATTERNS = [
    "or 1=1",
    "or '1'='1",
    "union select",
    "drop table",
    "insert into",
    "delete from",
    "select *",
    "select username",
    "select credit_limit",
    "1=1 --",
    "'; drop",
]

# Manipulated routing/account numbers — all-zeros, all-nines, all-same-digit
# These map to simulator.py's WIRE_PROBE_PAYLOADS
MANIPULATED_NUMBER_PATTERNS = [
    "000000000",
    "999999999",
    "111111111",
    "0000000000",
]

# Fields in the honeypot's structured log that contain metadata (not payload)
# Used to separate request payload from log metadata when payload isn't nested
METADATA_FIELDS = {
    "timestamp", "source_ip", "method", "path",
    "user_agent", "headers", "remote_addr",
}


# =============================================================================
# INITIALIZE CLIENTS (created once per function instance, reused across calls)
# =============================================================================

db = firestore.Client(project=PROJECT_ID)
publisher = pubsub_v1.PublisherClient()


# =============================================================================
# ENTRY POINT — triggered by Pub/Sub via Eventarc (2nd gen)
# =============================================================================

@functions_framework.cloud_event
def classify_event(cloud_event):
    """
    Main entry point. Receives a CloudEvent wrapping a Pub/Sub message
    that contains a Cloud Logging LogEntry from the honeypot.
    """

    # -----------------------------------------------------------------
    # STEP 1: Parse the Pub/Sub message to extract the log entry
    # -----------------------------------------------------------------
    try:
        pubsub_data = cloud_event.data["message"]["data"]
        raw_json = base64.b64decode(pubsub_data).decode("utf-8")
        log_entry = json.loads(raw_json)
    except (KeyError, json.JSONDecodeError) as e:
        print(f"[ERROR] Failed to parse Pub/Sub message: {e}")
        return

    # The honeypot's structured log data lives in jsonPayload
    # This is what Marissa's Flask app wrote via log_struct()
    event_data = log_entry.get("jsonPayload", {})

    if not event_data:
        print("[SKIP] No jsonPayload found in log entry — skipping.")
        return

    # -----------------------------------------------------------------
    # STEP 2: Extract fields from the honeypot log
    # -----------------------------------------------------------------
    source_ip = event_data.get("source_ip", "unknown")
    method = event_data.get("method", "unknown").upper()
    path = event_data.get("path", "unknown")
    user_agent = event_data.get("user_agent", "")
    timestamp = event_data.get("timestamp", log_entry.get("timestamp", ""))

    # Extract the request payload — might be nested under "payload" or "body",
    # or the fields might be at the top level of jsonPayload
    payload = event_data.get("payload") or event_data.get("body") or {}

    if not payload:
        # If no nested payload key, treat non-metadata fields as the payload
        payload = {
            k: v for k, v in event_data.items()
            if k not in METADATA_FIELDS
        }

    # Convert payload to lowercase string for pattern matching
    payload_str = json.dumps(payload, default=str).lower()

    print(f"[EVENT] {method} {path} from {source_ip}")

    # -----------------------------------------------------------------
    # STEP 3: Classify the event against detection rules
    # -----------------------------------------------------------------
    attack_type, severity, rule_matched = classify_attack(
        method, path, payload, payload_str, user_agent
    )

    # -----------------------------------------------------------------
    # STEP 4: Write the classified event to Firestore
    # -----------------------------------------------------------------
    now = datetime.now(timezone.utc)

    event_doc = {
        "timestamp": timestamp,
        "source_ip": source_ip,
        "attack_type": attack_type,
        "severity": severity,
        "method": method,
        "path": path,
        "user_agent": user_agent,
        "payload": payload_str[:2000],   # truncate to control doc size
        "alert_triggered": False,        # updated below if threshold met
        "rule_matched": rule_matched,
        "processed_at": now,             # used for threshold window queries
    }

    # .add() auto-generates a document ID
    _, doc_ref = db.collection("events").add(event_doc)

    print(f"[FIRESTORE] Written: {attack_type} / {severity} / {rule_matched}")

    # -----------------------------------------------------------------
    # STEP 5: Check thresholds for count-based rules
    # -----------------------------------------------------------------
    alert_triggered = False

    if attack_type == "sql_injection":
        # Single-event rule — always alert
        alert_triggered = True

    elif attack_type == "wire_transfer_probe":
        # Single-event rule — always alert
        alert_triggered = True

    elif attack_type == "credential_stuffing":
        # Threshold rule: >10 from same IP within 60 seconds
        alert_triggered = check_credential_stuffing_threshold(source_ip, now)

    elif attack_type == "port_scan":
        # Threshold rule: >8 distinct paths from same IP within 30 seconds
        alert_triggered = check_port_scan_threshold(source_ip, now)

    elif attack_type == "account_takeover_recon":
        # Semi-threshold: alert on sequential enumeration patterns
        alert_triggered = check_account_recon_threshold(source_ip, now)

    # Update the Firestore document with final alert status
    if alert_triggered:
        doc_ref.update({"alert_triggered": True})

    # -----------------------------------------------------------------
    # STEP 6: Publish alert to cloudhoney-alerts if triggered
    # -----------------------------------------------------------------
    if alert_triggered:
        publish_alert(attack_type, severity, source_ip, timestamp, path, rule_matched)
        print(f"[ALERT] Published: {attack_type} / {severity} from {source_ip}")
    else:
        print(f"[INFO] No alert — threshold not yet reached for {attack_type}")


# =============================================================================
# CLASSIFICATION LOGIC
# =============================================================================

def classify_attack(method, path, payload, payload_str, user_agent):
    """
    Evaluates a single event against financial sector detection rules.
    Returns (attack_type, severity, rule_matched).

    Rule priority:
      1. SQL injection (checked first — can appear in ANY endpoint)
      2. Wire fraud probe (manipulated routing/account on /transfer or /payment)
      3. Credential stuffing (POST to /login)
      4. Account takeover recon (/account endpoint)
      5. Port scan (catch-all for other paths)
    """

    # Rule 1 — SQL Injection (any endpoint)
    if contains_sql_injection(payload_str):
        return ("sql_injection", "HIGH", "injection_strings_detected")

    # Rule 2 — Wire fraud probe (/transfer or /payment with bad patterns)
    if path in ("/transfer", "/payment"):
        if contains_manipulated_routing(payload):
            return ("wire_transfer_probe", "HIGH", "manipulated_routing_account")
        # Even without manipulated numbers, these endpoints are sensitive
        return ("wire_transfer_probe", "HIGH", "sensitive_endpoint_probe")

    # Rule 3 — Credential stuffing (POST to /login)
    if path == "/login" and method == "POST":
        return ("credential_stuffing", "HIGH", "login_attempt")

    # Rule 4 — Account takeover recon (/account)
    if path == "/account":
        return ("account_takeover_recon", "MEDIUM", detect_recon_subtype(payload))

    # Rule 5 — Port scan (any other path = reconnaissance)
    return ("port_scan", "MEDIUM", "path_probe")


# =============================================================================
# PATTERN MATCHING HELPERS
# =============================================================================

def contains_sql_injection(payload_str):
    """
    Check if payload string contains known SQL injection patterns.
    Matches against: ' OR 1=1, UNION SELECT, DROP TABLE, etc.
    """
    for pattern in SQL_INJECTION_PATTERNS:
        if pattern in payload_str:
            return True
    return False


def contains_manipulated_routing(payload):
    """
    Check for manipulated routing or account numbers in the payload.
    Looks for: all-zeros, all-nines, all-same-digit strings of 9+ chars.
    """
    if not isinstance(payload, dict):
        return False

    # Check routing_number and account_number fields specifically
    for field in ("routing_number", "account_number"):
        value = str(payload.get(field, ""))

        # Check against known bad patterns
        if value in MANIPULATED_NUMBER_PATTERNS:
            return True

        # Check for all-same-digit strings (e.g., "1111111111")
        # Must be at least 9 characters (routing number length)
        if len(value) >= 9 and len(set(value.replace("-", ""))) == 1:
            return True

    return False


def detect_recon_subtype(payload):
    """
    Determines the specific type of account takeover reconnaissance.
    Maps to simulator.py's ACCOUNT_RECON_PAYLOADS structure.
    """
    if not isinstance(payload, dict):
        return "account_probe"

    if "ssn_lookup" in payload:
        return "ssn_enumeration"
    if "session_token" in payload:
        return "session_token_probe"
    if "account_id" in payload:
        return "sequential_id_enumeration"

    return "account_probe"


# =============================================================================
# THRESHOLD CHECKS (query Firestore for recent events from same IP)
# =============================================================================

def check_credential_stuffing_threshold(source_ip, now):
    """
    Credential stuffing rule: more than 10 POST /login from the
    same IP within 60 seconds triggers a HIGH alert.

    Returns True if threshold is exceeded.
    """
    cutoff = now - timedelta(seconds=CREDENTIAL_STUFFING_WINDOW_SEC)

    recent = (
        db.collection("events")
        .where("source_ip", "==", source_ip)
        .where("attack_type", "==", "credential_stuffing")
        .where("processed_at", ">=", cutoff)
        .stream()
    )

    count = sum(1 for _ in recent)
    print(f"[THRESHOLD] Credential stuffing: {count} attempts from {source_ip} in last 60s")

    return count > CREDENTIAL_STUFFING_THRESHOLD


def check_port_scan_threshold(source_ip, now):
    """
    Port scan rule: more than 8 distinct paths from the same IP
    within 30 seconds triggers a MEDIUM alert.

    Returns True if threshold is exceeded.
    """
    cutoff = now - timedelta(seconds=PORT_SCAN_WINDOW_SEC)

    recent = (
        db.collection("events")
        .where("source_ip", "==", source_ip)
        .where("attack_type", "==", "port_scan")
        .where("processed_at", ">=", cutoff)
        .stream()
    )

    distinct_paths = set()
    for doc in recent:
        data = doc.to_dict()
        distinct_paths.add(data.get("path", ""))

    print(f"[THRESHOLD] Port scan: {len(distinct_paths)} distinct paths from {source_ip} in last 30s")

    return len(distinct_paths) > PORT_SCAN_THRESHOLD


def check_account_recon_threshold(source_ip, now):
    """
    Account takeover recon rule: 5+ requests to /account from the
    same IP within 60 seconds suggests enumeration in progress.

    Returns True if threshold is exceeded.
    """
    cutoff = now - timedelta(seconds=60)

    recent = (
        db.collection("events")
        .where("source_ip", "==", source_ip)
        .where("attack_type", "==", "account_takeover_recon")
        .where("processed_at", ">=", cutoff)
        .stream()
    )

    count = sum(1 for _ in recent)
    print(f"[THRESHOLD] Account recon: {count} probes from {source_ip} in last 60s")

    return count >= 5


# =============================================================================
# ALERT PUBLISHING
# =============================================================================

def publish_alert(attack_type, severity, source_ip, timestamp, path, rule_matched):
    """
    Publishes a structured alert message to the cloudhoney-alerts
    Pub/Sub topic. Issue #9 will subscribe to this topic and deliver
    alerts via email (SendGrid + Secret Manager).
    """
    alert_message = {
        "attack_type": attack_type,
        "severity": severity,
        "source_ip": source_ip,
        "timestamp": timestamp,
        "path": path,
        "rule_matched": rule_matched,
        "alert_time": datetime.now(timezone.utc).isoformat(),
    }

    publisher.publish(
        ALERTS_TOPIC,
        data=json.dumps(alert_message).encode("utf-8"),
    )
