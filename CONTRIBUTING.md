# Contributing to CloudHoney

## Team

| Name | Role | GitHub |
|------|------|--------|
| Moses Chavez | Project Leader | [@mwchavez](https://github.com/mwchavez) |
| Marissa Turner | Developer | TBD |
| Juliana Garza | Scribe | TBD |

---

## Branching Strategy

We use a simple **feature branch** workflow. All work happens on branches — never commit directly to `main`.

```
main                ← stable, always deployable
├── feature/issue-3-honeypot-flask
├── feature/issue-6-traffic-gen-v1
├── fix/logging-json-format
└── docs/wiki-architecture-page
```

### Branch Naming Convention

Use the format: `<type>/<short-description>`

| Prefix | Use Case | Example |
|--------|----------|---------|
| `feature/` | New functionality tied to a GitHub Issue | `feature/issue-8-cloud-functions` |
| `fix/` | Bug fixes or corrections | `fix/firestore-write-error` |
| `infra/` | GCP infrastructure changes | `infra/vpc-firewall-rules` |
| `docs/` | Documentation and Wiki updates | `docs/setup-guide` |

---

## Workflow

1. **Pick an Issue** from the [Project Board](https://github.com/users/mwchavez/projects/7) and move it to `In Progress`.
2. **Create a branch** from `main`:
   ```bash
   git checkout main
   git pull origin main
   git checkout -b feature/issue-3-honeypot-flask
   ```
3. **Make your changes** with clear, focused commits (see Commit Messages below).
4. **Push your branch** and open a **Pull Request** against `main`:
   ```bash
   git push origin feature/issue-3-honeypot-flask
   ```
5. **Request a review** from at least one other team member.
6. **Merge** once approved, then delete the branch.
7. **Move the Issue** to `Done` on the Project Board.

---

## Commit Messages

Use clear, descriptive commit messages. Prefix with the type of change:

```
feat: add brute force detection rule to classify_event function
fix: correct JSON log format for Cloud Logging compatibility
infra: provision Compute Engine VM with e2-micro in us-central1
docs: add Cloud Functions architecture notes to Wiki
chore: update .gitignore to exclude service account keys
```

### Rules
- Use **present tense** ("add feature" not "added feature")
- Keep the first line under **72 characters**
- Reference the GitHub Issue number when applicable: `feat: add honeypot /login endpoint (closes #3)`

---

## What Not to Commit

The following should **never** appear in this repository:

- GCP service account key files (`.json`)
- `.env` files with real values
- API keys, passwords, or tokens (use Secret Manager)
- `.tfstate` files (if using Terraform)
- Compiled files, `__pycache__/`, or `node_modules/`

If you accidentally commit a secret, notify Moses immediately. The key must be revoked and rotated — removing it from Git history alone is not sufficient.

---

## Code Style

- **Python**: Follow PEP 8. Use meaningful variable names. Add docstrings to functions.
- **Infrastructure scripts**: Comment any `gcloud` command with what it does and why.
- **Documentation**: Use Markdown. Keep Wiki pages focused on one topic each.

---

## Questions?

If you're unsure about anything — branching, where code should go, how to structure a commit — just ask in the team chat or tag [@mwchavez](https://github.com/mwchavez) on the Issue. No question is too small.
