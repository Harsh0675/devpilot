# Security Policy

## Reporting a vulnerability

Please do not publish secrets or exploit details in a public issue. Report security concerns privately through the repository's GitHub security reporting mechanism when available.

## Secrets

DevPilot reads API credentials from environment variables and is designed not to commit them. Never place real API keys in `.env.example`, source files, patches, or documentation.

## Safe execution

Review AI-generated patches before applying them and review `git diff` before committing changes. Treat AI output as untrusted input.
