# DevPilot

AI-assisted developer CLI for understanding projects, inspecting code, analyzing build errors, and preparing safe changes.

## MVP

- `devpilot init` — create `.devpilot/`
- `devpilot scan` — inspect project files
- `devpilot ask "..."` — get a structured local response
- `devpilot doctor` — detect common Android/Gradle project issues
- `devpilot build` — run a project build with confirmation

## Design

DevPilot is intentionally provider-agnostic. The MVP has no AI API dependency, so it can run offline. AI providers can be added later.

## Run

```bash
python -m devpilot --help
python -m devpilot init
python -m devpilot scan
python -m devpilot doctor
```

## License

MIT
