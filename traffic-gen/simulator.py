"""
CloudHoney — Attack Traffic Simulator
CIS 4355 Cloud Computing | Spring 2026

Generates realistic financial sector attack traffic against the CloudHoney
honeypot. Designed to trigger detection rules in the classify_event Cloud
Function (Issue #8).

Usage:
    python simulator.py --target http://<HONEYPOT_IP>:5000 --scenario port_scan
    python simulator.py --target http://<HONEYPOT_IP>:5000 --scenario credential_stuffing
    python simulator.py --target http://<HONEYPOT_IP>:5000 --scenario wire_transfer_probe
    python simulator.py --target http://<HONEYPOT_IP>:5000 --scenario payment_api_abuse
    python simulator.py --target http://<HONEYPOT_IP>:5000 --scenario account_takeover_recon
    python simulator.py --target http://<HONEYPOT_IP>:5000 --all
"""

import argparse
import logging
import random
import requests
import time

# =============================================================================
# LOGGING SETUP
# =============================================================================
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)
logger = logging.getLogger("cloudhoney-simulator")

# =============================================================================
# SIMULATED DATA — designed to trigger specific detection rules
# =============================================================================

# Credential stuffing: leaked credential pairs (financial sector patterns)
LEAKED_CREDENTIALS = [
    ("jsmith", "Summer2024!"),
    ("admin", "admin"),
    ("mturner", "Welcome1"),
    ("jgarza", "Password123"),
    ("teller01", "Bank2024!"),
    ("admin", "admin123"),
    ("root", "toor"),
    ("sysadmin", "changeme"),
    ("finance_user", "money2024"),
    ("branch_mgr", "Branch#1"),
    ("auditor", "AuditPass1"),
    ("test", "test123"),
    ("demo", "demo"),
    ("csr_agent", "Customer1!"),
    ("loan_officer", "Approve$$"),
    ("it_support", "HelpDesk1"),
    ("compliance", "RegCheck1"),
    ("hr_admin", "PeopleOps!"),
    ("treasury", "FundsMove1"),
    ("wire_ops", "Transfer$"),
]

# Port scan: paths that mimic what a real attacker would probe on a banking app
SCAN_PATHS = [
    "/login",
    "/admin",
    "/transfer",
    "/payment",
    "/account",
    "/query",
    "/api",
    "/config",
    "/debug",
    "/status",
    "/health",
    "/swagger",
    "/api/v1",
    "/dashboard",
    "/reset-password",
    "/.env",
    "/wp-admin",
    "/phpmyadmin",
]

# Wire transfer probe: manipulated routing and account numbers
WIRE_PROBE_PAYLOADS = [
    {"routing_number": "000000000", "account_number": "1234567890", "amount": 50000.00},
    {"routing_number": "999999999", "account_number": "0000000000", "amount": 100000.00},
    {"routing_number": "111111111", "account_number": "9876543210", "amount": 999999.99},
    {"routing_number": "021000021", "account_number": "' OR 1=1 --", "amount": 1.00},
    {"routing_number": "' UNION SELECT * FROM accounts --", "account_number": "5555555555", "amount": 75000.00},
    {"routing_number": "021000021", "account_number": "1111111111", "amount": -500.00},
    {"routing_number": "000000000", "account_number": "DROP TABLE transactions;", "amount": 0},
    {"routing_number": "021000021", "account_number": "9999999999", "amount": 9999999.99},
    {"routing_number": "' OR '1'='1", "account_number": "8888888888", "amount": 10000.00},
    {"routing_number": "999999999", "account_number": "UNION SELECT username, password FROM users --", "amount": 500.00},
    {"routing_number": "000000000", "account_number": "000000000", "amount": 50000.00},
    {"routing_number": "021000021", "account_number": "7777777777", "amount": 0.01},
]

# Payment API abuse: malformed payloads with injection strings
PAYMENT_ABUSE_PAYLOADS = [
    {"card_number": "' OR 1=1 --", "merchant": "Test Store", "amount": 100.00},
    {"card_number": "4111111111111111", "merchant": "UNION SELECT * FROM cards --", "amount": 500.00},
    {"card_number": "0000000000000000", "merchant": "Legit Shop", "amount": -100.00},
    {"card_number": "4111111111111111", "merchant": "DROP TABLE payments;", "amount": 99.99},
    {"card_number": "9999999999999999", "merchant": "Test", "amount": 0},
    {"card_number": "4111111111111111", "merchant": "Shop", "amount": 9999999.99},
    {"card_number": "' UNION SELECT credit_limit FROM accounts --", "merchant": "X", "amount": 1.00},
    {"card_number": "4111111111111111", "merchant": "'; DROP TABLE orders; --", "amount": 50.00},
    {"card_number": "1234567890123456", "merchant": "Test", "amount": 100.00, "transaction_id": "pay_abc123"},
    {"card_number": "1234567890123456", "merchant": "Test", "amount": 100.00, "transaction_id": "pay_abc123"},  # duplicate replay
    {"card_number": "' OR '1'='1' --", "merchant": "Fraud Store", "amount": 750.00},
]

# Account takeover recon: sequential IDs and enumeration patterns
ACCOUNT_RECON_PAYLOADS = [
    {"account_id": "10001"},
    {"account_id": "10002"},
    {"account_id": "10003"},
    {"account_id": "10004"},
    {"account_id": "10005"},
    {"account_id": "10006"},
    {"account_id": "10007"},
    {"account_id": "10008"},
    {"ssn_lookup": "123-45-6789"},
    {"ssn_lookup": "000-00-0000"},
    {"ssn_lookup": "999-99-9999"},
    {"session_token": "eyJhbGciOiJIUzI1NiJ9.test_token_probe"},
    {"session_token": "null"},
    {"session_token": "undefined"},
    {"session_token": "' OR 1=1 --"},
]

# User-Agent strings — realistic per scenario
UA_SCANNER = "Mozilla/5.0 (compatible; Nmap Scripting Engine; https://nmap.org/book/nse.html)"
UA_BROWSERS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Safari/605.1.15",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
]

# =============================================================================
# SCENARIO 1 — PORT SCAN (path-based reconnaissance)
# Detection rule: >8 distinct paths from same IP within 30 seconds
# =============================================================================
def simulate_port_scan(target: str, delay: float = 0.3):
    """
    Simulates reconnaissance by probing multiple paths on port 5000.
    Mimics an attacker mapping out a banking app's endpoint surface.
    """
    logger.info("=" * 60)
    logger.info("SCENARIO: Port Scan (Path Reconnaissance)")
    logger.info("=" * 60)

    headers = {"User-Agent": UA_SCANNER}

    for path in SCAN_PATHS:
        url = f"{target}{path}"
        try:
            response = requests.get(url, headers=headers, timeout=5)
            logger.info(f"  [SCAN] {path:25s} -> {response.status_code}")
        except requests.exceptions.RequestException as e:
            logger.warning(f"  [SCAN] {path:25s} -> FAILED ({type(e).__name__})")

        time.sleep(delay)

    logger.info(f"Port scan complete — {len(SCAN_PATHS)} paths probed.\n")


# =============================================================================
# SCENARIO 2 — CREDENTIAL STUFFING (rapid login attempts)
# Detection rule: >10 failed POST to /login from same IP within 60 seconds
# =============================================================================
def simulate_credential_stuffing(target: str, delay: float = 0.1):
    """
    Simulates credential stuffing using leaked banking credentials.
    Fires 20 login attempts in rapid succession to trigger the threshold.
    """
    logger.info("=" * 60)
    logger.info("SCENARIO: Credential Stuffing")
    logger.info("=" * 60)

    endpoint = f"{target}/login"

    for i, (username, password) in enumerate(LEAKED_CREDENTIALS, 1):
        headers = {"User-Agent": random.choice(UA_BROWSERS)}
        payload = {"username": username, "password": password}

        try:
            response = requests.post(
                endpoint, json=payload, headers=headers, timeout=5
            )
            logger.info(
                f"  [STUFF] Attempt {i:2d}/20: {username:15s} / {password:15s} -> {response.status_code}"
            )
        except requests.exceptions.RequestException as e:
            logger.warning(f"  [STUFF] Attempt {i:2d}/20: FAILED ({type(e).__name__})")

        time.sleep(delay)

    logger.info("Credential stuffing complete — 20 attempts sent.\n")


# =============================================================================
# SCENARIO 3 — WIRE TRANSFER PROBING
# Detection rule: request to /transfer with manipulated routing/account
#                 patterns OR SQL injection strings
# =============================================================================
def simulate_wire_transfer_probe(target: str, delay: float = 0.3):
    """
    Simulates probing the wire transfer endpoint with manipulated
    routing numbers, account numbers, and injection payloads.
    """
    logger.info("=" * 60)
    logger.info("SCENARIO: Wire Transfer Probing")
    logger.info("=" * 60)

    endpoint = f"{target}/transfer"
    headers = {"User-Agent": random.choice(UA_BROWSERS)}

    for i, payload in enumerate(WIRE_PROBE_PAYLOADS, 1):
        try:
            response = requests.post(
                endpoint, json=payload, headers=headers, timeout=5
            )
            logger.info(
                f"  [WIRE] Probe {i:2d}/{len(WIRE_PROBE_PAYLOADS)}: "
                f"routing={payload['routing_number'][:20]:20s} -> {response.status_code}"
            )
        except requests.exceptions.RequestException as e:
            logger.warning(f"  [WIRE] Probe {i:2d}: FAILED ({type(e).__name__})")

        time.sleep(delay)

    logger.info(f"Wire transfer probing complete — {len(WIRE_PROBE_PAYLOADS)} probes sent.\n")


# =============================================================================
# SCENARIO 4 — PAYMENT API ABUSE
# Detection rule: SQL injection strings in /payment payload, malformed
#                 amounts, duplicate transaction replays
# =============================================================================
def simulate_payment_api_abuse(target: str, delay: float = 0.2):
    """
    Simulates abuse of the payment endpoint with injection payloads,
    negative amounts, overflow values, and transaction replays.
    """
    logger.info("=" * 60)
    logger.info("SCENARIO: Payment API Abuse")
    logger.info("=" * 60)

    endpoint = f"{target}/payment"
    headers = {"User-Agent": random.choice(UA_BROWSERS)}

    for i, payload in enumerate(PAYMENT_ABUSE_PAYLOADS, 1):
        try:
            response = requests.post(
                endpoint, json=payload, headers=headers, timeout=5
            )
            logger.info(
                f"  [PAY]  Abuse {i:2d}/{len(PAYMENT_ABUSE_PAYLOADS)}: "
                f"card={str(payload['card_number'])[:20]:20s} -> {response.status_code}"
            )
        except requests.exceptions.RequestException as e:
            logger.warning(f"  [PAY]  Abuse {i:2d}: FAILED ({type(e).__name__})")

        time.sleep(delay)

    logger.info(f"Payment API abuse complete — {len(PAYMENT_ABUSE_PAYLOADS)} payloads sent.\n")


# =============================================================================
# SCENARIO 5 — ACCOUNT TAKEOVER RECON
# Detection rule: repeated requests to /account with sequential IDs,
#                 SSN patterns, or session/token probing
# =============================================================================
def simulate_account_takeover_recon(target: str, delay: float = 0.2):
    """
    Simulates account takeover reconnaissance: sequential account ID
    enumeration, SSN probing, and session token manipulation.
    """
    logger.info("=" * 60)
    logger.info("SCENARIO: Account Takeover Reconnaissance")
    logger.info("=" * 60)

    endpoint = f"{target}/account"

    for i, payload in enumerate(ACCOUNT_RECON_PAYLOADS, 1):
        headers = {"User-Agent": random.choice(UA_BROWSERS)}

        try:
            response = requests.post(
                endpoint, json=payload, headers=headers, timeout=5
            )
            # Show the key being probed for logging clarity
            probe_key = list(payload.keys())[0]
            probe_val = str(list(payload.values())[0])[:30]
            logger.info(
                f"  [RECON] Probe {i:2d}/{len(ACCOUNT_RECON_PAYLOADS)}: "
                f"{probe_key}={probe_val:30s} -> {response.status_code}"
            )
        except requests.exceptions.RequestException as e:
            logger.warning(f"  [RECON] Probe {i:2d}: FAILED ({type(e).__name__})")

        time.sleep(delay)

    logger.info(f"Account takeover recon complete — {len(ACCOUNT_RECON_PAYLOADS)} probes sent.\n")


# =============================================================================
# RUN ALL — sequential execution of all 5 scenarios
# =============================================================================
def run_all(target: str):
    """Run all five attack scenarios in sequence."""
    logger.info("*" * 60)
    logger.info("RUNNING ALL SCENARIOS")
    logger.info("*" * 60 + "\n")

    simulate_port_scan(target)
    simulate_credential_stuffing(target)
    simulate_wire_transfer_probe(target)
    simulate_payment_api_abuse(target)
    simulate_account_takeover_recon(target)

    logger.info("*" * 60)
    logger.info("ALL SCENARIOS COMPLETE")
    logger.info("*" * 60)


# =============================================================================
# CLI ENTRY POINT
# =============================================================================
def main():
    parser = argparse.ArgumentParser(
        description="CloudHoney — Financial Sector Attack Traffic Simulator"
    )

    parser.add_argument(
        "--target",
        required=True,
        help="Honeypot base URL (e.g., http://10.0.2.X:5000)"
    )

    parser.add_argument(
        "--scenario",
        choices=[
            "port_scan",
            "credential_stuffing",
            "wire_transfer_probe",
            "payment_api_abuse",
            "account_takeover_recon",
        ],
        help="Run a specific attack scenario"
    )

    parser.add_argument(
        "--all",
        action="store_true",
        help="Run all five attack scenarios in sequence"
    )

    args = parser.parse_args()

    if not args.all and not args.scenario:
        parser.error("Specify --scenario <name> or --all")

    logger.info(f"Target: {args.target}")

    if args.all:
        run_all(args.target)
    elif args.scenario == "port_scan":
        simulate_port_scan(args.target)
    elif args.scenario == "credential_stuffing":
        simulate_credential_stuffing(args.target)
    elif args.scenario == "wire_transfer_probe":
        simulate_wire_transfer_probe(args.target)
    elif args.scenario == "payment_api_abuse":
        simulate_payment_api_abuse(args.target)
    elif args.scenario == "account_takeover_recon":
        simulate_account_takeover_recon(args.target)


if __name__ == "__main__":
    main()
