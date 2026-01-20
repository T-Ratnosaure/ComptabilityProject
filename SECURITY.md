# Security Guidelines

## Secrets Management

### API Keys and Credentials

**NEVER commit secrets to the repository.** This includes:
- API keys (Anthropic, etc.)
- Database credentials
- JWT secrets
- Any passwords or tokens

### Local Development

1. Copy `.env.example` to `.env`:
   ```bash
   cp .env.example .env
   ```

2. Fill in your actual credentials in `.env`

3. **Never commit `.env`** - it's already in `.gitignore`

### Production Deployment

For production, use proper secrets management:

| Platform | Recommended Solution |
|----------|---------------------|
| AWS | AWS Secrets Manager or Parameter Store |
| GCP | Google Secret Manager |
| Azure | Azure Key Vault |
| Heroku | Config Vars |
| Docker | Docker Secrets |
| Kubernetes | Kubernetes Secrets |

### Pre-commit Hook (Recommended)

Install `detect-secrets` to prevent accidental commits:

```bash
pip install detect-secrets
detect-secrets scan > .secrets.baseline
```

Add to `.pre-commit-config.yaml`:
```yaml
repos:
  - repo: https://github.com/Yelp/detect-secrets
    rev: v1.4.0
    hooks:
      - id: detect-secrets
        args: ['--baseline', '.secrets.baseline']
```

### If You Accidentally Commit a Secret

1. **Immediately rotate the credential** - consider it compromised
2. Remove from git history:
   ```bash
   git filter-branch --force --index-filter \
     "git rm --cached --ignore-unmatch PATH_TO_FILE" \
     --prune-empty --tag-name-filter cat -- --all
   ```
3. Force push (coordinate with team)
4. Contact the service provider if necessary

## API Security

### Authentication

All API endpoints handling sensitive data require authentication:
- API key authentication for external integrations
- Session-based authentication for web UI

### Rate Limiting

Rate limits are enforced to prevent abuse:
- General endpoints: 100 requests/minute
- LLM endpoints: 10 requests/minute (due to cost)
- Authentication endpoints: 5 requests/minute

### Input Validation

All user input is validated using Pydantic models:
- Type checking
- Range validation for numeric fields
- Sanitization of string inputs

## Data Protection

### Sensitive Data Handling

- Tax data is stored encrypted at rest
- Session data uses `sessionStorage` (not `localStorage`)
- PII is sanitized before LLM processing
- Audit logs are retained for 5 years per French tax law

### GDPR Compliance

- Users can request data deletion
- Data retention policies are documented
- No data is shared with third parties without consent

## Reporting Security Issues

If you discover a security vulnerability, please:
1. **Do not** create a public GitHub issue
2. Email: [security contact to be added]
3. Include detailed steps to reproduce

We will respond within 48 hours.
