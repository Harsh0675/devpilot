# 🚀 DevPilot

**DevPilot v0.7.0** is an industry-oriented multi-agent AI software-engineering platform for **Windows, Linux, and macOS**. It combines project intelligence, safe code changes, multi-agent workflows, and a provider-neutral LLM runtime.

## ⬇️ Download

**Latest releases:** https://github.com/Harsh0675/devpilot/releases/latest

### Desktop installers

| Platform | Package |
|---|---|
| Windows x64 | `DevPilot-<version>-windows-x64-setup.exe` |
| Linux x64 | `DevPilot-<version>-linux-x64.AppImage` |
| Linux x64 | `DevPilot-<version>-linux-x64.tar.gz` |
| macOS Intel | `DevPilot-<version>-devpilot-macos-x64.dmg` |
| macOS Apple Silicon | `DevPilot-<version>-devpilot-macos-arm64.dmg` |

All release packages include both **DevPilot** and **DevPilot Agent**. SHA-256 checksum files are published with every release.

## 🤖 Multi-Agent Engineering

DevPilot includes a deterministic production pipeline:

**Planner → Coder → Reviewer → Tester**

Each agent receives bounded repository context and the outputs of previous agents. This enables architecture planning, implementation proposals, security review, regression analysis, and verification planning as one workflow.

Run it with:

```bash
devpilot-agent "Add authentication with tests and secure configuration"
```

Machine-readable output:

```bash
devpilot-agent "Review this project for production risks" --json
```

## 🧠 LLM / Provider Support

DevPilot uses a lightweight HTTP runtime with no mandatory vendor SDK dependency.

### Native adapters

- OpenAI-compatible APIs
- Anthropic Messages API
- Google Gemini API
- Ollama local models

### OpenAI-compatible ecosystem

The same interface can be used with compatible services such as OpenRouter, Groq, Together, Mistral, DeepSeek, Qwen-compatible endpoints, and self-hosted gateways by changing the base URL/model.

## ✨ Production Capabilities

- 🪟 Windows x64 installer
- 🐧 Linux x64 AppImage + tarball
- 🍎 macOS Intel DMG
- 🍎 macOS Apple Silicon DMG
- 🤖 Multi-agent engineering pipeline
- 🧠 Provider-neutral LLM runtime
- 🌐 Cloud and local model support
- 📚 Bounded project context
- 🔍 Local source indexing/search
- 💬 Interactive coding copilot
- 🧭 Implementation planning
- 🛠️ AI-generated unified diffs
- 🔐 Human approval for writes by default
- 🧪 Automated test/build workflow
- 🩺 Environment diagnostics
- 🔒 API keys kept out of project files
- 📦 Reproducible release packaging with SHA-256 checksums

## Existing copilot workflow

```bash
devpilot init
devpilot doctor
devpilot index
devpilot ask "Analyze the most important production risk"
devpilot plan "Add offline caching"
devpilot fix "Fix the login crash"
devpilot apply
devpilot test
devpilot build
```

## Installation

### Windows

Run the `DevPilot-<version>-windows-x64-setup.exe` installer. It installs both `devpilot.exe` and `devpilot-agent.exe` and creates Start Menu shortcuts.

### Linux

For AppImage:

```bash
chmod +x DevPilot-<version>-linux-x64.AppImage
./DevPilot-<version>-linux-x64.AppImage
```

The tarball contains the same standalone executables.

### macOS

Open the matching `.dmg` for Intel or Apple Silicon and copy `DevPilot.app` to Applications. The application bundle contains both DevPilot executables.

### From source

```bash
python -m pip install -e .
```

## Security model

1. Repository context is bounded before it reaches an LLM.
2. Secrets are read from environment variables.
3. Agents do not silently modify files.
4. Code changes are represented as reviewable patches.
5. Existing DevPilot command permissions remain opt-in.
6. Agent outputs are auditable and can be emitted as JSON for CI/orchestration.

## Releases

Tagged releases automatically build native Windows, Linux, and macOS packages using GitHub Actions and publish SHA-256 checksums.

## License

MIT
