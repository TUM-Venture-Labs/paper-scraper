# Security Policy

## Supported Versions

| Version | Supported          |
| ------- | ------------------ |
| 1.0.x   | :white_check_mark: |

## Reporting a Vulnerability

We take the security of Paper Scraper seriously. If you discover a security vulnerability, please follow these steps:

1. **Do NOT create a public GitHub issue**
2. Email your findings to [your-email@domain.com]
3. Include:
   - Description of the vulnerability
   - Steps to reproduce
   - Potential impact
   - Suggested fix (if any)

## Security Considerations

### API Keys and Credentials
- Never commit API keys or credentials
- Use environment variables for sensitive data
- Rotate keys regularly
- Use separate API keys for development and production

### Data Protection
- Publication data is stored securely in Supabase
- Personal information is sanitized before analysis (see `src/gpt/analyzer.py`, lines 267-276)
- Access to the database is restricted and monitored

### Rate Limiting
- Implements polite scraping delays (see `src/scraper/scraper.py`, line 26)
- Respects TUM's portal rate limits
- API calls to OpenAI are rate-limited

### AWS Lambda Security
- Function runs in a VPC
- Minimal IAM permissions
- Environment variables are encrypted
- Regular security audits

### Dependencies
- Regular dependency updates
- Automated vulnerability scanning
- Only trusted packages from PyPI

## Best Practices for Contributors

1. Never commit sensitive data
2. Use `.env` files locally
3. Keep dependencies updated
4. Follow secure coding practices
5. Review code for security issues
6. Use strong authentication
7. Implement proper error handling

## Compliance

This project adheres to:
- GDPR requirements for handling academic data
- TUM's data usage policies
- AWS security best practices
- OpenAI's API usage guidelines

## Updates

Security policy updates will be communicated through:
- Repository announcements
- Release notes
- Direct communication for critical issues 