import argparse
import logging
import random
import requests
import time

# =========================
# CONFIGURATION
# =========================
target_url = "http://YOUR_HONEYPOT_IP"  # <-- replace

CREDENTIALS = [
    ("admin", "admin123"),
    ("user", "password"),
    ("test", "123456"),
    ("john_doe", "qwerty"),
    ("jane_doe", "letmein"),
]

PORTS = [21, 22, 23, 25, 53, 80, 110, 139, 143, 443, 445, 3389, 8080]

ACCOUNT_IDS = ["1001", "1002", "1003", "2001", "9999"]
PAYMENT_IDS = ["pay_abc123", "pay_xyz789", "pay_test456"]

# =========================
# LOGGING
# =========================
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)

# =========================
# SCENARIO 1: PORT SCAN
# =========================
def simulate_port_scan(delay=0.2):
    logging.info("Starting port scan simulation...")

    for port in PORTS:
        url = f"{target_url}:{port}"
        try:
            logging.info(f"Scanning {url}")
            response = requests.get(url, timeout=2)
            logging.info(f"Response: {response.status_code}")
        except requests.exceptions.RequestException as e:
            logging.info(f"Port {port} closed/filtered ({e})")

        time.sleep(delay)

    logging.info("Port scan complete.\n")


# =========================
# SCENARIO 2: CREDENTIAL STUFFING
# =========================
def simulate_credential_stuffing(attempts=20, delay=0.1):
    logging.info("Starting credential stuffing...")

    login_endpoint = f"{target_url}/login"

    for i in range(attempts):
        username, password = random.choice(CREDENTIALS)

        try:
            logging.info(f"Attempt {i+1}: {username}/{password}")
            r = requests.post(login_endpoint, json={
                "username": username,
                "password": password
            }, timeout=2)

            logging.info(f"Response: {r.status_code}")
        except requests.exceptions.RequestException as e:
            logging.error(e)

        time.sleep(delay)

    logging.info("Credential stuffing complete.\n")


# =========================
# SCENARIO 3: WIRE TRANSFER PROBING
# =========================
def simulate_wire_transfer_probe(attempts=15, delay=0.2):
    """
    Simulates probing wire transfer endpoints for validation flaws
    """
    logging.info("Starting wire transfer probing...")

    endpoint = f"{target_url}/api/wire-transfer"

    for i in range(attempts):
        payload = {
            "from_account": random.choice(ACCOUNT_IDS),
            "to_account": random.choice(ACCOUNT_IDS),
            "amount": random.choice([0, -100, 9999999, 1.23]),
            "currency": random.choice(["USD", "EUR", "BTC"]),
        }

        try:
            logging.info(f"Probe {i+1}: {payload}")
            r = requests.post(endpoint, json=payload, timeout=2)
            logging.info(f"Response: {r.status_code}")
        except requests.exceptions.RequestException as e:
            logging.error(e)

        time.sleep(delay)

    logging.info("Wire transfer probing complete.\n")


# =========================
# SCENARIO 4: PAYMENT API ABUSE
# =========================
def simulate_payment_api_abuse(attempts=20, delay=0.1):
    """
    Simulates abuse of payment APIs (replays, invalid calls, enumeration)
    """
    logging.info("Starting payment API abuse...")

    endpoint = f"{target_url}/api/payment"

    for i in range(attempts):
        payload = {
            "payment_id": random.choice(PAYMENT_IDS),
            "amount": random.randint(1, 10000),
            "currency": "USD",
        }

        headers = {
            "Authorization": f"Bearer fake_token_{random.randint(1000,9999)}"
        }

        try:
            logging.info(f"API abuse {i+1}: {payload}")
            r = requests.post(endpoint, json=payload, headers=headers, timeout=2)
            logging.info(f"Response: {r.status_code}")
        except requests.exceptions.RequestException as e:
            logging.error(e)

        time.sleep(delay)

    logging.info("Payment API abuse complete.\n")


# =========================
# SCENARIO 5: ACCOUNT TAKEOVER RECON
# =========================
def simulate_account_takeover_recon(attempts=20, delay=0.1):
    """
    Simulates reconnaissance for account takeover (user enumeration)
    """
    logging.info("Starting account takeover reconnaissance...")

    endpoint = f"{target_url}/api/user"

    usernames = [c[0] for c in CREDENTIALS] + ["unknown_user", "guest"]

    for i in range(attempts):
        username = random.choice(usernames)

        try:
            url = f"{endpoint}/{username}"
            logging.info(f"Recon {i+1}: {url}")
            r = requests.get(url, timeout=2)

            logging.info(f"Response: {r.status_code}")
        except requests.exceptions.RequestException as e:
            logging.error(e)

        time.sleep(delay)

    logging.info("Account takeover recon complete.\n")


# =========================
# RUNNER
# =========================
def run_all():
    simulate_port_scan()
    simulate_credential_stuffing()
    simulate_wire_transfer_probe()
    simulate_payment_api_abuse()
    simulate_account_takeover_recon()


def main():
    parser = argparse.ArgumentParser(description="CloudHoney Attack Simulator")

    parser.add_argument(
        "--scenario",
        choices=[
            "port-scan",
            "credential-stuffing",
            "wire-probe",
            "payment-abuse",
            "account-recon"
        ],
        help="Run a specific scenario"
    )

    parser.add_argument(
        "--all",
        action="store_true",
        help="Run all attack scenarios"
    )

    args = parser.parse_args()

    if args.all:
        run_all()
        return

    if args.scenario == "port-scan":
        simulate_port_scan()
    elif args.scenario == "credential-stuffing":
        simulate_credential_stuffing()
    elif args.scenario == "wire-probe":
        simulate_wire_transfer_probe()
    elif args.scenario == "payment-abuse":
        simulate_payment_api_abuse()
    elif args.scenario == "account-recon":
        simulate_account_takeover_recon()
    else:
        logging.error("Please specify --scenario or use --all")


if __name__ == "__main__":
    main()