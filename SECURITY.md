# Security Policy

## Purpose

CloudHoney is a **security research platform** simulating a financial institution's internet-facing infrastructure. Because this project handles simulated financial sector attack data and integrates with GCP security services, maintaining strong security practices within the project itself is essential — both as a matter of principle and in alignment with PCI DSS and GLBA compliance frameworks that inform our detection rules.

---

## Reporting a Vulnerability

If you discover a security vulnerability in this repository — including exposed credentials, misconfigured IAM roles, insecure infrastructure scripts, or any issue that could compromise the GCP environment — please report it responsibly.

**Do not open a public GitHub Issue for security vulnerabilities.**

Instead, contact the Project Leader directly:

- **Moses Chavez** — [GitHub: @mwchavez](https://github.com/mwchavez)

Please include:
- A description of the vulnerability
- Steps to reproduce (if applicable)
- The potential impact on the GCP project or data pipeline
- Any suggested remediation

We will acknowledge receipt within **48 hours** and work to resolve the issue promptly.

---

## Security Practices

The following practices are enforced across the CloudHoney project:

### Credential Management
- **No credentials, API keys, or service account keys are committed to this repository — ever.**
- All sensitive values are stored in **GCP Secret Manager** and retrieved at runtime.
- The `.gitignore` file explicitly excludes `.env`, `*.json` key files, and `*.pem` files.
- A `.env.example` file is provided as a safe reference template with placeholder values only.

### IAM & Access Control
- All GCP resources operate under the **principle of least privilege**.
- Team members are assigned the minimum IAM roles required for their responsibilities:
  - Project Leader: `Owner`
  - Developer: `Editor`
  - Scribe: `Viewer`
- A dedicated **Service Account** is used for all application-level GCP access — personal credentials are never used in code or deployed services.

### Network Security
- The Compute Engine honeypot VM operates inside a **custom VPC Network** with firewall rules restricting inbound traffic to expected sources only.
- Public access to the honeypot is limited to the traffic generator and authorized testing IPs.
- The Cloud Run dashboard is configured for unauthenticated access **only during live demonstrations** and should be restricted otherwise.

### Data Handling
- All honeypot log data is stored in **Cloud Storage** with uniform access control and public access blocked.
- Firestore event records contain simulated attack data only — no real PII, financial data, or customer information is processed or stored at any point.
- Log retention and storage practices follow structured JSON formatting with date-based partitioning for auditability.

### Compliance Context
- Detection rules are informed by **PCI DSS** (Payment Card Industry Data Security Standard) and **GLBA** (Gramm-Leach-Bliley Act) frameworks.
- While CloudHoney is an academic project and not subject to formal compliance audits, the architecture and security posture are designed to reflect the standards a financial institution would apply to its own monitoring infrastructure.

---

## Scope

This security policy covers:
- All source code in this repository
- GCP infrastructure configurations and deployment scripts
- Cloud Functions, Pub/Sub topics, Firestore collections, and Cloud Storage buckets provisioned under the `cloudhoney-sp26` GCP project
- Any credentials, tokens, or API keys associated with the project

---

## Acknowledgments

We take security seriously — even in an academic context. If you identify an issue, we appreciate your responsible disclosure.
