# 🚀 DevPilot

**DevPilot v0.6.0** is a production-oriented AI coding copilot for developers who want project intelligence, safe AI-generated changes, testing, diagnostics, and build automation from the terminal.

## ✨ Production Copilot Features

- 🌐 OpenAI-compatible online AI providers
- 🧠 Project-aware context retrieval with bounded context size
- 📚 Lightweight local project indexing
- 🔍 Source search with `find`
- 💬 One-shot AI assistance with `ask`
- 🗣️ Interactive coding copilot with `chat`
- 🧭 Implementation planning with `plan`
- 🛠️ AI-generated unified diffs with `fix`
- 🔐 Explicit human approval for file writes by default
- ✅ Patch validation with `git apply --check`
- 🧪 Test runner with Gradle/Python detection
- 🏗️ Android/Gradle build automation
- 🩺 Environment diagnostics with `doctor`
- 📊 Git working-tree visibility with `status` and `diff`
- 🧾 AI build-log explanation with `explain`
- ⚙️ Persistent model/provider/permission configuration
- 📴 Local inspection works without AI
- 📱 Termux-friendly CLI
- 🪟 Windows + 🐧 Linux release binaries

## Install

From source:

```bash
python -m pip install -e .
```

Prebuilt Windows/Linux packages are published in GitHub Releases.

## Online AI setup

DevPilot never stores your API key in the repository. Set it as an environment variable:

```bash
export DEVPILOT_API_KEY="your-api-key"
```

OpenAI-compatible providers can be configured with:

```bash
export DEVPILOT_BASE_URL="https://api.openai.com/v1"
export DEVPILOT_MODEL="gpt-4o-mini"
```

Or persist non-secret configuration locally:

```bash
devpilot config --model gpt-4o-mini
devpilot config --base-url https://api.openai.com/v1
```

## Quick start

```bash
devpilot init
devpilot doctor
devpilot index
devpilot status
devpilot ask "Analyze this project and find the most important issue"
```

## Copilot workflow

Interactive mode:

```bash
devpilot chat
```

Plan before changing code:

```bash
devpilot plan "Add offline caching to the settings screen"
```

Generate a safe patch:

```bash
devpilot fix "Fix the login screen crash"
```

The patch is saved to `.devpilot/proposed.patch`; **no files are changed** until you explicitly apply it:

```bash
devpilot apply
```

DevPilot validates the patch before application. `--apply` is available when you intentionally want the fix workflow to continue to application.

## Verify changes

```bash
devpilot diff
devpilot test
devpilot build
```

Commands that execute builds/tests require confirmation by default. Use `-y` only when you intentionally want non-interactive execution.

## Commands

| Command | Purpose |
|---|---|
| `init` | Initialize local configuration |
| `scan` | Inspect project files |
| `index` | Build a lightweight local index |
| `find` | Search source files |
| `status` | Show Git working-tree status |
| `diff` | Show unstaged changes |
| `ask` | Ask the online AI about the project |
| `chat` | Interactive coding copilot |
| `plan` | Create an implementation plan |
| `fix` | Generate and optionally apply an AI patch |
| `apply` | Apply the saved reviewed patch |
| `test` | Run detected tests |
| `explain` | Analyze a build/error log |
| `doctor` | Check the development environment |
| `build` | Build an Android/Gradle project |
| `config` | Configure model, provider URL, and permissions |

## Security model

DevPilot follows a conservative local-agent model:

1. AI receives bounded project context rather than the entire filesystem.
2. API keys are read from environment variables and are never written to project files.
3. AI code changes are represented as patches rather than silent overwrites.
4. Patches are validated before application.
5. Command execution and file-write permissions require explicit approval by default.
6. Generated changes remain reviewable through normal Git tooling.

## Release

Current release: **v0.6.0**.

Windows x64 and Linux x64 binaries are produced through GitHub Actions for tagged releases.

## License

MIT
