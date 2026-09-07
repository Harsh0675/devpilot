import argparse
import json
import re
from pathlib import Path

from .agents import AgentOrchestrator
from .llm import PROVIDERS

IGNORE = {'.git', '.gradle', '.idea', 'build', '.devpilot', '__pycache__', '.venv', 'node_modules', 'dist', '.tox'}
EXTENSIONS = {'.py', '.js', '.ts', '.tsx', '.jsx', '.java', '.kt', '.kts', '.xml', '.json', '.md', '.txt', '.gradle', '.properties', '.yml', '.yaml', '.toml', '.sh', '.c', '.cpp', '.h', '.hpp', '.rs', '.go', '.swift', '.dart', '.sql'}


def context(question, root=None, limit=18, max_chars=70000):
    root = Path(root or Path.cwd()).resolve()
    words = {w.lower() for w in re.findall(r'[A-Za-z0-9_]{3,}', question)}
    scored = []
    for p in root.rglob('*'):
        if not p.is_file() or p.suffix.lower() not in EXTENSIONS or any(x in IGNORE for x in p.parts):
            continue
        try:
            text = p.read_text(encoding='utf-8', errors='ignore')
        except OSError:
            continue
        score = sum(text.lower().count(w) for w in words) + sum(2 for w in words if w in p.name.lower())
        scored.append((score, p, text))
    scored.sort(key=lambda x: (-x[0], str(x[1])))
    chunks, total = [], 0
    for _, p, text in scored[:limit]:
        chunk = f'FILE: {p.relative_to(root)}\n{text[:12000]}'
        if total + len(chunk) > max_chars:
            break
        chunks.append(chunk)
        total += len(chunk)
    return '\n\n---\n\n'.join(chunks)


def main():
    parser = argparse.ArgumentParser(prog='devpilot-agent', description='DevPilot multi-agent software engineering pipeline.')
    parser.add_argument('request', nargs='+')
    parser.add_argument('--provider', default=None, help='openai-compatible, anthropic, gemini, ollama, or compatible provider alias')
    parser.add_argument('--model', default=None)
    parser.add_argument('--base-url', default=None)
    parser.add_argument('--json', action='store_true')
    args = parser.parse_args()
    request = ' '.join(args.request).strip()
    ctx = context(request)
    results = AgentOrchestrator().run(request, ctx, model=args.model, provider=args.provider, base_url=args.base_url)
    if args.json:
        print(json.dumps([r.__dict__ for r in results], indent=2))
    else:
        for result in results:
            print(f'\n===== {result.role.upper()} AGENT =====\n{result.output}\n')


if __name__ == '__main__':
    main()
