# 🚀 DevPilot

**DevPilot v0.4.0** is an online AI-assisted autonomous developer CLI for understanding projects, searching code, proposing safe code changes, and working with Android/Gradle builds.

## ✨ Features

- 🌐 OpenAI-compatible online AI
- 🔎 Project-aware context retrieval
- 📚 Local project indexing
- 🔍 Fast code search
- 🤖 AI project analysis with `ask`
- 🛠️ AI-generated unified diffs with `fix`
- 🔐 Human approval before applying changes
- 🩺 Android/Gradle diagnostics
- 📦 Android debug build support
- 🧾 Build-log explanation with `explain`
- 📴 Local inspection commands continue to work without AI
- 📱 Designed to work well in Termux

## Install

```bash
python -m pip install -e .
```

## Online AI setup

DevPilot never stores your API key in the repository. Set it as an environment variable:

```bash
export DEVPILOT_API_KEY="your-api-key"
```

For OpenAI-compatible providers you can also configure:

```bash
export DEVPILOT_BASE_URL="https://api.openai.com/v1"
export DEVPILOT_MODEL="gpt-4o-mini"
```

## Quick start

```bash
devpilot init
devpilot index
devpilot scan
devpilot doctor
devpilot ask "Analyze this project and find the most important issue"
```

## Autonomous coding

Ask DevPilot to prepare a change:

```bash
devpilot fix "Fix the login screen crash"
```

DevPilot generates a unified diff and saves it to `.devpilot/proposed.patch`. **No files are changed by this command.** Review the diff and apply it explicitly:

```bash
devpilot apply
```

Or request the same workflow with an explicit apply flag:

```bash
devpilot fix "Fix the login screen crash" --apply
```

Before applying, DevPilot validates the patch with `git apply --check` and still asks for confirmation unless write permission has been enabled in `.devpilot/config.json`.

## Build and diagnose

```bash
devpilot build
devpilot explain build-error.txt
```

The build command requires explicit confirmation unless `--yes` is supplied.

## Commands

| Command | Purpose |
|---|---|
| `init` | Initialize DevPilot configuration |
| `scan` | Inspect project files |
| `index` | Create a lightweight local project index |
| `find` | Search source files |
| `ask` | Ask the online AI about your project |
| `fix` | Generate and optionally apply an AI patch |
| `apply` | Apply the saved reviewed patch |
| `explain` | Analyze a build/error log |
| `doctor` | Check project and AI environment |
| `build` | Build an Android/Gradle project |

## Safety

DevPilot is designed around explicit user control. AI-generated patches are saved for review, patch validation happens before application, and build execution requires confirmation by default. Never commit API keys or secrets.

## License

MIT
