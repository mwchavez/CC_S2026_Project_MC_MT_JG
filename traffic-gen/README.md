# Traffic Generator

Python-based attack traffic simulator that generates realistic malicious request patterns against the CloudHoney honeypot endpoint.

## Scenarios

| Scenario | Flag | Description |
|----------|------|-------------|
| Port Scan | `--scenario port_scan` | Probes multiple endpoints mimicking reconnaissance tools |
| Brute Force | `--scenario brute_force` | Rapid POST requests to `/login` with common credential pairs |
| SQL Injection | `--scenario sql_injection` | POST requests to `/query` with OWASP-referenced injection payloads |

## Usage

```bash
python simulator.py --target http://<HONEYPOT_IP>:5000 --scenario port_scan
python simulator.py --target http://<HONEYPOT_IP>:5000 --scenario brute_force
python simulator.py --target http://<HONEYPOT_IP>:5000 --scenario sql_injection
```

## Configuration

Set the `target` to the Compute Engine VM's external IP address running the honeypot application.
