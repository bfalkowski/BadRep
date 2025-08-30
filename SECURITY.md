# Security Policy

## Supported Versions

We actively maintain and provide security updates for the following versions:

| Version | Supported          |
| ------- | ------------------ |
| 0.2.x   | :white_check_mark: |
| 0.1.x   | :white_check_mark: |
| < 0.1   | :x:                |

## Reporting a Vulnerability

We take security vulnerabilities seriously. If you discover a security vulnerability in ReviewLab, please follow these steps:

### 1. **DO NOT** create a public GitHub issue
Security vulnerabilities should be reported privately to prevent exploitation.

### 2. **DO** report via email
Send an email to: **security@reviewlab.dev**

### 3. **Include the following information:**
- **Description**: Clear description of the vulnerability
- **Impact**: What could an attacker do with this vulnerability?
- **Steps to reproduce**: Detailed steps to reproduce the issue
- **Affected versions**: Which versions are affected?
- **Suggested fix**: If you have ideas for fixing it

### 4. **What happens next:**
- We will acknowledge receipt within 48 hours
- We will investigate and provide updates
- We will work on a fix and coordinate disclosure
- We will credit you in the security advisory (unless you prefer anonymity)

## Security Best Practices

### For Users:
- Keep ReviewLab updated to the latest version
- Use GitHub integration only with repositories you control
- Regularly rotate GitHub Personal Access Tokens
- Review bug injection templates before use
- Use in isolated environments when testing

### For Contributors:
- Follow secure coding practices
- Validate all inputs
- Use parameterized queries
- Implement proper authentication checks
- Keep dependencies updated

## Security Features

ReviewLab includes several security features:

- **Input Validation**: All user inputs are validated and sanitized
- **Path Traversal Protection**: File paths are validated to prevent directory traversal
- **Template Security**: Bug injection templates are validated for safety
- **Authentication**: GitHub integration requires proper authentication
- **Isolation**: Bug injection runs in isolated sessions

## Disclosure Policy

When a security vulnerability is confirmed:

1. **Immediate**: We assess the severity and impact
2. **Within 72 hours**: We develop a fix for supported versions
3. **Coordinated disclosure**: We release the fix and security advisory
4. **Public notification**: We notify users through GitHub releases and documentation

## Security Contacts

- **Security Team**: security@reviewlab.dev
- **Lead Maintainer**: bryanfalkowski
- **Emergency**: Create a private security advisory on GitHub

## Acknowledgments

We thank security researchers and users who responsibly report vulnerabilities. Your contributions help make ReviewLab more secure for everyone.

---

*This security policy is based on best practices from the open source community and follows the GitHub Security Lab guidelines.*
