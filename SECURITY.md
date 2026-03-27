# Security Policy

## Reporting a Vulnerability

If you discover a security vulnerability in this project, please report it responsibly. **Do not open a public GitHub issue.**

Email your findings to: **security@blakebauman.com**

Please include:

- A description of the vulnerability
- Steps to reproduce
- Potential impact

We will acknowledge your report within 48 hours and work with you to understand and address the issue before any public disclosure.

## Scope

This policy covers vulnerabilities in:

- Python application code (`src/`)
- Terraform modules (`infra/`)
- GitHub Actions workflows (`.github/`)

Infrastructure deployed using these Terraform modules is the responsibility of the deployer. This project is a reference implementation — always review and harden configurations before deploying to production.

## Supported Versions

Only the latest version on the `main` branch is supported with security updates.
