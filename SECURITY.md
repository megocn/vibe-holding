# Security Policy

## Supported versions

| Version | Supported |
| --- | --- |
| `main` (0.x) | ✅ |

## Reporting a vulnerability

Please **do not** open a public Issue for security problems (especially anything involving credentials, crypto, or backup formats).

1. Contact the maintainer privately (GitHub Security Advisory on this repository, or the email listed in your GitHub profile / CODEOWNERS).
2. Include: affected component, reproduction steps, impact, and (if possible) a suggested fix.
3. Allow reasonable time for a fix before public disclosure.

We will acknowledge receipt as soon as practical and follow up with a fix or mitigation plan.

## Credential vault — important notice

The desktop **凭据管家** is still a **transitional** implementation relative to the full SPEC (system keychain + Argon2id / XChaCha20 + encrypted SQLite).

- Do **not** treat it as a production-grade password manager yet.
- Prefer OS keychain / a mature password manager for high-value secrets until the SPEC crypto path lands.
- Never commit vault backups, master passwords, API keys, or `.env` files to this repository.
- Web / narrow-viewport builds intentionally **omit** the credentials UI.

## Scope

In scope: crypto/vault, auth-adjacent flows, dependency supply chain issues in first-party code, XSS that could exfiltrate local data.

Out of scope (unless trivially abused): third-party SaaS outages, content accuracy in `content/`, social engineering against individual users.
