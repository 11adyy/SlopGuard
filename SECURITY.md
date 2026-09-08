# Security Policy

## Reporting a Vulnerability

SlopGuard takes security seriously. If you discover a security vulnerability, please report it responsibly and discreetly.

### How to Report

**Do not** open a public GitHub issue for security vulnerabilities. Instead, please email:

📧 **github@11adyy.dev**

Include the following details in your report:

- A clear description of the vulnerability
- Steps to reproduce the issue
- The potential impact or severity
- Any suggested fixes (if you have them)

### What to Expect

- **Initial response:** You will receive an acknowledgment within 48 hours
- **Investigation:** We will work to understand and verify the vulnerability
- **Fix timeline:** Critical vulnerabilities will be prioritized; we aim to release patches promptly
- **Disclosure:** Once a fix is released, we will publicly disclose the issue with proper credit to the reporter (if desired)

### Scope

This security policy applies to:

- **Authentication & Authorization:** GitHub App token handling, webhook signature verification
- **Data Protection:** Sensitive environment variables, private keys, API credentials
- **Webhook Processing:** Input validation, GitHub signature verification, injection vulnerabilities
- **Dependencies:** Known vulnerabilities in third-party packages
- **Deployment Security:** Configuration, network exposure, default settings

### Out of Scope

- Social engineering
- Phishing attacks
- DDoS attacks
- Issues in user-managed infrastructure (unless related to SlopGuard documentation)

### Security Best Practices for Users

When deploying SlopGuard:

1. **Never** commit `.env` files or private keys to version control
2. Use a strong, non-empty `GITHUB_WEBHOOK_SECRET`
3. Keep dependencies updated by running `pip install --upgrade -e .`
4. Run SlopGuard behind a reverse proxy (nginx, Caddy) in production
5. Use HTTPS for webhook URLs
6. Rotate GitHub App private keys periodically
7. Restrict network access to the SlopGuard service
8. Review the GitHub App permissions and webhook events regularly

### Vulnerability Disclosure Timeline

We follow responsible disclosure practices:

- **Day 1:** Vulnerability reported and acknowledged
- **Day 3–30:** Investigation and patch development
- **Day 31+:** Public disclosure after patch release

We appreciate your patience and cooperation in helping keep SlopGuard secure.

---

Thank you for helping us maintain a secure project! 🙏
