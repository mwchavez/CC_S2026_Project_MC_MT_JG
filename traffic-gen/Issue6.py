import argparse
import logging
import random
import requests
import time

# =========================
# CONFIGURATION
# =========================
target_url = "http://YOUR_HONEYPOT_IP"  # <-- replace with your honeypot VM IP

# Sample credential list (simulate leaked creds)
CREDENTIALS = [
    ("admin", "admin123"),
    ("user", "password"),
    ("test", "123456"),
    ("john_doe", "qwerty"),
    ("jane_doe", "letmein"),
]

# Common ports to simulate scanning
PORTS = [21, 22, 23, 25, 53, 80, 110, 139, 143, 443, 445, 3389, 8080]

# =========================
# LOGGING SETUP
# =========================
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)

# =========================
# ATTACK SIMULATIONS
# =========================

def simulate_port_scan(delay=0.2):
    """
    Simulates a port scan by sending HTTP requests to different ports
    """
    logging.info("Starting port scan simulation...")

    for port in PORTS:
        url = f"{target_url}:{port}"

        try:
            logging.info(f"Scanning port {port} -> {url}")
            response = requests.get(url, timeout=2)
            logging.info(f"Response from port {port}: {response.status_code}")
        except requests.exceptions.RequestException as e:
            logging.info(f"Port {port} appears closed or filtered ({e})")

        time.sleep(delay)

    logging.info("Port scan simulation completed.")


def simulate_credential_stuffing(attempts=20, delay=0.1):
    """
    Simulates credential stuffing by repeatedly attempting logins
    """
    logging.info("Starting credential stuffing simulation...")

    login_endpoint = f"{target_url}/login"

    for i in range(attempts):
        username, password = random.choice(CREDENTIALS)

        payload = {
            "username": username,
            "password": password
        }

        try:
            logging.info(f"Attempt {i+1}: {username}/{password}")
            response = requests.post(login_endpoint, json=payload, timeout=2)

            logging.info(
                f"Response: {response.status_code} | {response.text[:50]}"
            )

        except requests.exceptions.RequestException as e:
            logging.error(f"Request failed: {e}")

        time.sleep(delay)

    logging.info("Credential stuffing simulation completed.")


# =========================
# CLI ENTRY POINT
# =========================

def main():
    parser = argparse.ArgumentParser(
        description="CloudHoney Attack Traffic Simulator"
    )

    parser.add_argument(
        "--scenario",
        choices=["port-scan", "credential-stuffing"],
        required=True,
        help="Attack scenario to simulate"
    )

    args = parser.parse_args()

    if args.scenario == "port-scan":
        simulate_port_scan()
    elif args.scenario == "credential-stuffing":
        simulate_credential_stuffing()


if __name__ == "__main__":
    main()