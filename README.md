# 🚀 DevPilot

**DevPilot v0.8.0** is an autonomous multi-agent AI software-engineering platform for **Windows, Linux, and macOS**. It combines project intelligence, persistent project memory, safe tool permissions, multi-agent workflows, and a provider-neutral LLM runtime.

## 🤖 Autonomous engineering

DevPilot can run a bounded engineering loop:

**Request → Architect → Planner → Implementer → Verifier**

The loop produces an auditable plan and reviewable patch proposal. File writes, shell commands, and tests remain permission-gated instead of being silently executed.

```bash
devpilot-agent --autonomous "Add authentication with tests and secure configuration"
```

Control the loop budget:

```bash
devpilot-agent --autonomous --max-steps 4 "Investigate and fix the failing build"
```

Machine-readable events:

```bash
devpilot-agent --autonomous --json "Review this project for production risks"
```

## 🧠 Persistent project memory

Autonomous runs maintain bounded project memory under `.devpilot/memory.json`. It records recent run summaries and durable project facts without placing secrets into the repository.

## 🔐 Permission model

DevPilot exposes explicit capabilities for agents:

- read project files — allowed by default
- search project — allowed by default
- inspect Git — allowed by default
- modify files — approval required
- run tests — approval required
- shell commands — approval required

Path traversal outside the project root is rejected by the tool layer. Dangerous execution should remain behind explicit user/CI policy.

## 🧩 Multi-agent pipeline

The standard pipeline includes:

**Architect → Planner → Coder → Security → Reviewer → Tester**

Each stage receives bounded repository context and prior stage output, making architecture, implementation, security review, regression analysis, and verification part of one auditable workflow.

## 🌐 LLM / Provider support

- OpenAI-compatible APIs
- Anthropic Messages API
- Google Gemini API
- Ollama local models
- OpenRouter, Groq, Together, Mistral, DeepSeek, Qwen-compatible endpoints
- Custom OpenAI-compatible gateways through `--base-url`

Example:

```bash
devpilot-agent --autonomous --provider ollama --model llama3 "Improve error handling"
```

## ✨ Production capabilities

- 🪟 Windows x64 installer + portable package
- 🐧 Linux x64 AppImage + tarball
- 🍎 macOS Apple Silicon package
- 🍎 macOS Intel package when the GitHub runner is available
- 🤖 Autonomous multi-agent engineering loop
- 🧠 Provider-neutral LLM runtime
- 📚 Bounded project context
- 💾 Persistent project memory
- 🔐 Explicit agent permissions
- 🔍 Local source indexing/search
- 🛠️ Reviewable AI-generated unified diffs
- 🧪 Test/build workflow integration
- 🩺 Environment diagnostics
- 📦 Release packaging with SHA-256 checksums

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

Download the latest native package from the GitHub Releases page, or install from source:

```bash
python -m pip install -e .
```

## Security model

1. Repository context is bounded before it reaches an LLM.
2. Secrets are read from environment variables.
3. Agent capabilities are explicitly permission-gated.
4. Code changes are represented as reviewable patches.
5. Project memory is stored under `.devpilot/` and excludes secret values.
6. Agent outputs can be emitted as JSON for CI/orchestration.

## License

MIT
