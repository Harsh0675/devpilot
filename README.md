# DevPilot 🚀

**Online AI developer agent for the terminal.** DevPilot understands your project, searches source files, sends relevant context to an OpenAI-compatible AI API, diagnoses development problems, and can build Android/Gradle projects safely.

## ✨ Features

- 🌐 Online AI via any OpenAI-compatible `/chat/completions` endpoint
- 🔎 Lightweight project-aware context selection
- 📚 Local source index with `devpilot index`
- 🔍 Fast source search with `devpilot find`
- 🩺 Android/Gradle project diagnostics
- 📦 Android debug builds with confirmation
- 🔐 API keys stay in environment variables — never commit secrets
- 📱 Works well in Termux and normal Linux/macOS environments
- 📴 Local commands continue to work without an API connection

## ⚡ Quick start

```bash
git clone https://github.com/Harsh0675/devpilot.git
cd devpilot
python -m pip install -e .
devpilot init
export DEVPILOT_API_KEY="YOUR_API_KEY"
devpilot index
devpilot ask "Explain this project and find likely build problems"
```

For Android projects:

```bash
devpilot doctor
devpilot scan
devpilot ask "Check this Android project for likely Gradle or manifest problems"
devpilot build
```

## 🌐 Providers

DevPilot uses an OpenAI-compatible HTTP API and does **not** hard-code a single vendor. Configure another compatible service with:

```bash
export DEVPILOT_BASE_URL="https://your-provider.example/v1"
export DEVPILOT_MODEL="your-model"
export DEVPILOT_API_KEY="your-key"
```

The default configuration targets OpenAI's compatible API endpoint. No API key is included in the repository.

## 🧠 How it works

1. DevPilot scans the current project while ignoring generated/build directories.
2. For an AI question, it selects relevant text files and creates a compact project context.
3. The context and your request are sent securely over HTTPS to the configured AI endpoint.
4. The response is printed directly in your terminal.

DevPilot does **not** automatically modify files or execute arbitrary AI-generated commands in v0.2.0.

## Commands

| Command | Purpose |
|---|---|
| `devpilot init` | Initialize project configuration |
| `devpilot scan` | Inspect project structure |
| `devpilot index` | Build a lightweight local file index |
| `devpilot find <term>` | Search source files |
| `devpilot ask <question>` | Ask the online AI about the project |
| `devpilot doctor` | Check common development/Android setup issues |
| `devpilot build` | Build an Android/Gradle project safely |

## 🔐 Security

Never put an API key in source code, `.devpilot/config.json`, README files, commits, or issues. Use `DEVPILOT_API_KEY` (or `OPENAI_API_KEY`) as an environment variable.

## Roadmap

- [x] Online AI provider
- [x] Project-aware context
- [x] Source indexing/search
- [x] Android diagnostics/build support
- [ ] Diff-based AI code edits
- [ ] Test/fix/rebuild agent loop
- [ ] Skills/plugins system
- [ ] Local model support
- [ ] Optional web dashboard

## License

MIT
