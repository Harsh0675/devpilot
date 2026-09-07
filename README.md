# 🚀 DevPilot

**DevPilot v0.6.0** is a production-oriented AI coding copilot for **Windows and Linux desktop/server environments**. It provides project intelligence, safe AI-generated changes, testing, diagnostics, and build automation from the command line.

## ✨ Production Copilot Features

- 🪟 Native Windows x64 executable release
- 🐧 Native Linux x64 executable release
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
- 🏗️ Build automation
- 🩺 Environment diagnostics with `doctor`
- 📊 Git working-tree visibility with `status` and `diff`
- 🧾 AI build-log explanation with `explain`
- ⚙️ Persistent model/provider/permission configuration
- 🔒 No API keys stored in project files

## Installation

### Windows

Download `devpilot-windows-x64.zip` from GitHub Releases, extract it, and run `devpilot.exe` from PowerShell or Command Prompt.

### Linux

Download `devpilot-linux-x64.tar.gz`, extract it, make the binary executable if required, and run:

```bash
./devpilot --version
```

### From source

Python 3.9+ is supported for source installation:

```bash
python -m pip install -e .
```

## Online AI setup

Set your API key as an environment variable. DevPilot does not write it into the repository:

### Windows PowerShell

```powershell
$env:DEVPILOT_API_KEY="your-api-key"
```

### Linux

```bash
export DEVPILOT_API_KEY="your-api-key"
```

OpenAI-compatible providers can also be configured with:

```text
DEVPILOT_BASE_URL=https://api.openai.com/v1
DEVPILOT_MODEL=gpt-4o-mini
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

## Verify changes

```bash
devpilot diff
devpilot test
devpilot build
```

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
| `build` | Build a supported project |
| `config` | Configure model, provider URL, and permissions |

## Security model

DevPilot follows a conservative local-agent model:

1. AI receives bounded project context rather than the entire filesystem.
2. API keys are read from environment variables and are never written to project files.
3. AI code changes are represented as patches rather than silent overwrites.
4. Patches are validated before application.
5. Command execution and file-write permissions require explicit approval by default.
6. Generated changes remain reviewable through normal Git tooling.

## Releases

Windows x64 and Linux x64 binaries are built automatically through GitHub Actions for tagged releases.

## License

MIT
