# Security Policy

## Supported Versions

Use this section to tell people about which versions of your project are
currently being supported with security updates.

| Version | Supported          |
| ------- | ------------------ |
| 5.1.x   | :white_check_mark: |
| 5.0.x   | :x:                |
| 4.0.x   | :white_check_mark: |
| < 4.0   | :x:                |

## Best Practices for Secure Development

1. **Environment Variables**:
   - Always use environment variables to store sensitive information, such as `SECRET_KEY`, database credentials, and API keys.
   - Avoid hardcoding sensitive information in the codebase.

2. **Dependency Management**:
   - Regularly update dependencies to their latest secure versions.
   - Use tools like `pip-audit` or `safety` to scan for known vulnerabilities in dependencies.

3. **Code Reviews**:
   - Ensure all code changes are reviewed by at least one other developer.
   - Use automated tools like `pylint` and `black` to enforce code quality and style.

4. **Secure Deployment**:
   - Disable `DEBUG` mode in production.
   - Use HTTPS for all production environments.
   - Restrict access to sensitive endpoints using IP whitelisting or authentication.

5. **Monitoring and Logging**:
   - Enable logging for all critical actions and errors.
   - Use monitoring tools to detect and respond to security incidents.

6. **Database Security**:
   - Use strong passwords for database users.
   - Restrict database access to trusted IP addresses.

## Reporting a Vulnerability

If you discover a vulnerability, please report it by emailing `security@scopewatch.com`. Include:
- A detailed description of the vulnerability.
- Steps to reproduce the issue.
- Any potential impact or exploit scenarios.

We will acknowledge receipt of your report within 48 hours and provide updates as we investigate and address the issue.
