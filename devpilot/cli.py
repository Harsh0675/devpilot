import argparse
import json
import os
import subprocess
import urllib.error
import urllib.request
from pathlib import Path

IGNORE = {'.git', '.gradle', '.idea', 'build', '.devpilot', '__pycache__', '.venv', 'node_modules'}
TEXT_EXTENSIONS = {'.py', '.js', '.ts', '.tsx', '.jsx', '.java', '.kt', '.kts', '.xml', '.json', '.md', '.txt', '.gradle', '.properties', '.yml', '.yaml', '.toml', '.sh', '.c', '.cpp', '.h', '.hpp'}
MAX_FILE_CHARS = 12000


def project_root():
    return Path.cwd()


def iter_files(root):
    for path in root.rglob('*'):
        if path.is_file() and not any(part in IGNORE for part in path.parts):
            yield path


def load_config():
    path = project_root() / '.devpilot' / 'config.json'
    if path.exists():
        try:
            return json.loads(path.read_text(encoding='utf-8'))
        except Exception:
            pass
    return {'version': 2, 'provider': 'openai-compatible', 'model': 'gpt-4o-mini', 'base_url': 'https://api.openai.com/v1'}


def cmd_init(_args):
    d = project_root() / '.devpilot'
    d.mkdir(exist_ok=True)
    state = d / 'config.json'
    if not state.exists():
        state.write_text(json.dumps({
            'version': 2,
            'provider': 'openai-compatible',
            'model': 'gpt-4o-mini',
            'base_url': 'https://api.openai.com/v1',
            'permissions': {'write_files': False, 'run_commands': False}
        }, indent=2) + '\n', encoding='utf-8')
    print(f'DevPilot initialized: {d}')
    print('Set DEVPILOT_API_KEY to enable online AI.')


def cmd_scan(_args):
    files = list(iter_files(project_root()))
    print(f'Project: {project_root()}')
    print(f'Files: {len(files)}')
    by_ext = {}
    for f in files:
        ext = f.suffix.lower() or '[no extension]'
        by_ext[ext] = by_ext.get(ext, 0) + 1
    for ext, count in sorted(by_ext.items(), key=lambda x: (-x[1], x[0])):
        print(f'  {ext}: {count}')


def make_context(question, limit=6):
    words = {w.lower() for w in question.replace('/', ' ').replace('.', ' ').split() if len(w) > 2}
    candidates = []
    for path in iter_files(project_root()):
        if path.suffix.lower() not in TEXT_EXTENSIONS:
            continue
        try:
            text = path.read_text(encoding='utf-8', errors='ignore')
        except Exception:
            continue
        score = sum(text.lower().count(w) for w in words)
        if score or path.name.lower() in question.lower():
            candidates.append((score, path, text))
    candidates.sort(key=lambda x: (-x[0], str(x[1])))
    if not candidates:
        candidates = [(0, p, p.read_text(encoding='utf-8', errors='ignore')) for p in list(iter_files(project_root()))[:limit] if p.suffix.lower() in TEXT_EXTENSIONS]
    chunks = []
    for _, path, text in candidates[:limit]:
        chunks.append(f'FILE: {path.relative_to(project_root())}\n{text[:MAX_FILE_CHARS]}')
    return '\n\n---\n\n'.join(chunks)


def online_chat(question):
    api_key = os.getenv('DEVPILOT_API_KEY') or os.getenv('OPENAI_API_KEY')
    if not api_key:
        return None, 'DEVPILOT_API_KEY is not set. Run: export DEVPILOT_API_KEY="your-key"'
    config = load_config()
    base = os.getenv('DEVPILOT_BASE_URL', config.get('base_url', 'https://api.openai.com/v1')).rstrip('/')
    model = os.getenv('DEVPILOT_MODEL', config.get('model', 'gpt-4o-mini'))
    context = make_context(question)
    payload = {
        'model': model,
        'messages': [
            {'role': 'system', 'content': 'You are DevPilot, a careful software engineering agent. Analyze the supplied project context. Give practical, concise answers. Never claim to have changed files unless explicitly asked and a change was actually performed.'},
            {'role': 'user', 'content': f'Project context:\n{context}\n\nDeveloper request:\n{question}'}
        ],
        'temperature': 0.2
    }
    req = urllib.request.Request(base + '/chat/completions', data=json.dumps(payload).encode(), headers={'Authorization': f'Bearer {api_key}', 'Content-Type': 'application/json'}, method='POST')
    try:
        with urllib.request.urlopen(req, timeout=90) as response:
            data = json.loads(response.read().decode())
        return data['choices'][0]['message']['content'], None
    except urllib.error.HTTPError as e:
        detail = e.read().decode(errors='ignore')
        return None, f'AI API error {e.code}: {detail[:500]}'
    except Exception as e:
        return None, f'Connection error: {e}'


def cmd_ask(args):
    question = ' '.join(args.question).strip()
    answer, error = online_chat(question)
    if error:
        print(error)
        print('\nDevPilot still works locally. Configure an OpenAI-compatible API to use online AI.')
        return
    print(answer)


def cmd_index(_args):
    files = []
    for path in iter_files(project_root()):
        if path.suffix.lower() in TEXT_EXTENSIONS:
            try:
                text = path.read_text(encoding='utf-8', errors='ignore')
                files.append({'path': str(path.relative_to(project_root())), 'chars': len(text), 'lines': text.count('\n') + 1})
            except Exception:
                pass
    d = project_root() / '.devpilot'
    d.mkdir(exist_ok=True)
    (d / 'index.json').write_text(json.dumps({'version': 1, 'files': files}, indent=2) + '\n', encoding='utf-8')
    print(f'Indexed {len(files)} text files.')


def cmd_find(args):
    term = ' '.join(args.term).lower()
    hits = 0
    for path in iter_files(project_root()):
        if path.suffix.lower() not in TEXT_EXTENSIONS:
            continue
        try:
            for number, line in enumerate(path.read_text(encoding='utf-8', errors='ignore').splitlines(), 1):
                if term in line.lower():
                    print(f'{path.relative_to(project_root())}:{number}: {line.strip()[:240]}')
                    hits += 1
        except Exception:
            pass
    print(f'\n{hits} match(es).')


def cmd_doctor(_args):
    root = project_root()
    checks = [
        ('Git repository', (root / '.git').exists()),
        ('Gradle wrapper', (root / 'gradlew').exists() or (root / 'gradlew.bat').exists()),
        ('Android manifest', any(root.rglob('AndroidManifest.xml'))),
        ('settings.gradle', any(root.glob('settings.gradle*'))),
        ('build.gradle', any(root.glob('build.gradle*'))),
        ('Online API key', bool(os.getenv('DEVPILOT_API_KEY') or os.getenv('OPENAI_API_KEY'))),
    ]
    print('DevPilot Doctor\n')
    for name, ok in checks:
        print(f"[{'OK' if ok else 'INFO'}] {name}")


def cmd_build(args):
    root = project_root()
    if not (root / 'gradlew').exists():
        print('No ./gradlew found. Build command currently supports Gradle projects.')
        return
    if not args.yes and input('Run ./gradlew assembleDebug? [y/N] ').strip().lower() != 'y':
        print('Cancelled.')
        return
    raise SystemExit(subprocess.run(['./gradlew', 'assembleDebug'], cwd=root).returncode)


def main():
    parser = argparse.ArgumentParser(prog='devpilot', description='Online AI-assisted developer agent.')
    sub = parser.add_subparsers(dest='command', required=True)
    sub.add_parser('init').set_defaults(func=cmd_init)
    sub.add_parser('scan').set_defaults(func=cmd_scan)
    sub.add_parser('index').set_defaults(func=cmd_index)
    find = sub.add_parser('find'); find.add_argument('term', nargs='+'); find.set_defaults(func=cmd_find)
    sub.add_parser('doctor').set_defaults(func=cmd_doctor)
    ask = sub.add_parser('ask'); ask.add_argument('question', nargs='+'); ask.set_defaults(func=cmd_ask)
    build = sub.add_parser('build'); build.add_argument('-y', '--yes', action='store_true'); build.set_defaults(func=cmd_build)
    args = parser.parse_args(); args.func(args)


if __name__ == '__main__':
    main()
