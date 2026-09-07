# 🚀 DevPilot

**DevPilot v0.7.0** is an industry-oriented AI software-engineering platform for **Windows and Linux desktop/server environments**. It combines project intelligence, safe code changes, multi-agent workflows, and a provider-neutral LLM runtime.

## 🤖 Multi-Agent Engineering

DevPilot now includes a deterministic production pipeline:

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

Examples:

```bash
# OpenAI-compatible
$env:DEVPILOT_PROVIDER="openai-compatible"
$env:DEVPILOT_API_KEY="your-key"
$env:DEVPILOT_MODEL="your-model"
$env:DEVPILOT_BASE_URL="https://api.openai.com/v1"

# Ollama
$env:DEVPILOT_PROVIDER="ollama"
$env:DEVPILOT_MODEL="qwen3-coder"

# Anthropic
$env:DEVPILOT_PROVIDER="anthropic"
$env:ANTHROPIC_API_KEY="your-key"
$env:DEVPILOT_MODEL="your-model"

# Gemini
$env:DEVPILOT_PROVIDER="gemini"
$env:GEMINI_API_KEY="your-key"
$env:DEVPILOT_MODEL="your-model"
```

Linux uses the same variables with `export`.

## ✨ Production Capabilities

- 🪟 Windows x64 packaging
- 🐧 Linux x64 packaging
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

Download the Windows x64 release package, extract it, and run `devpilot.exe` or `devpilot-agent.exe`.

### Linux

Download the Linux x64 release package and run:

```bash
./devpilot --version
./devpilot-agent "Review this project"
```

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

Windows x64 and Linux x64 packages are built automatically by GitHub Actions for tagged releases.

## License

MIT
