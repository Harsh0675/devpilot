# Contributing to DevPilot

Thanks for contributing!

## Development

```bash
python -m pip install -e .
python -m devpilot --help
python -m devpilot scan
python -m devpilot index
```

## Guidelines

- Keep the CLI lightweight and Termux-friendly.
- Never commit API keys, tokens, or local project state.
- Prefer safe, explicit operations over destructive automation.
- Keep AI-generated changes reviewable as diffs.
- Update the README when adding user-facing commands.

## Pull requests

Describe the problem, the change, and how you tested it. Small focused pull requests are preferred.
