import argparse
import json
import os
import shutil
import subprocess
import urllib.error
import urllib.request
from datetime import datetime, timezone
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
    return {'version': 4, 'provider': 'openai-compatible', 'model': 'gpt-4o-mini', 'base_url': 'https://api.openai.com/v1', 'permissions': {'write_files': False, 'run_commands': False}}


def save_config(config):
    d = project_root() / '.devpilot'
    d.mkdir(exist_ok=True)
    (d / 'config.json').write_text(json.dumps(config, indent=2) + '\n', encoding='utf-8')


def cmd_init(_args):
    config = load_config()
    save_config(config)
    print(f'DevPilot initialized: {project_root() / ".devpilot"}')
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


def make_context(question='', limit=8):
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


def online_chat(messages):
    api_key = os.getenv('DEVPILOT_API_KEY') or os.getenv('OPENAI_API_KEY')
    if not api_key:
        return None, 'DEVPILOT_API_KEY is not set.'
    config = load_config()
    base = os.getenv('DEVPILOT_BASE_URL', config.get('base_url', 'https://api.openai.com/v1')).rstrip('/')
    model = os.getenv('DEVPILOT_MODEL', config.get('model', 'gpt-4o-mini'))
    payload = {'model': model, 'messages': messages, 'temperature': 0.2}
    req = urllib.request.Request(base + '/chat/completions', data=json.dumps(payload).encode(), headers={'Authorization': f'Bearer {api_key}', 'Content-Type': 'application/json'}, method='POST')
    try:
        with urllib.request.urlopen(req, timeout=120) as response:
            data = json.loads(response.read().decode())
        return data['choices'][0]['message']['content'], None
    except urllib.error.HTTPError as e:
        return None, f'AI API error {e.code}: {e.read().decode(errors="ignore")[:500]}'
    except Exception as e:
        return None, f'Connection error: {e}'


def cmd_ask(args):
    question = ' '.join(args.question).strip()
    context = make_context(question)
    answer, error = online_chat([
        {'role': 'system', 'content': 'You are DevPilot, a careful software engineering agent. Analyze project context and give practical, concise answers. Do not claim to edit files.'},
        {'role': 'user', 'content': f'Project context:\n{context}\n\nDeveloper request:\n{question}'}
    ])
    if error:
        print(error)
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
    (d / 'index.json').write_text(json.dumps({'version': 1, 'created_at': datetime.now(timezone.utc).isoformat(), 'files': files}, indent=2) + '\n', encoding='utf-8')
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


def extract_patch(text):
    start = text.find('```diff')
    if start >= 0:
        body = text[start + len('```diff'):]
        end = body.find('```')
        return body[:end if end >= 0 else len(body)].strip()
    return None


def cmd_fix(args):
    request = ' '.join(args.request).strip()
    context = make_context(request, limit=10)
    system = '''You are DevPilot, an autonomous coding agent. Return a proposed unified diff only, inside a ```diff code block. Use repository-relative paths. Never invent files unnecessarily. Keep changes minimal and safe. Do not include prose outside the diff.'''
    answer, error = online_chat([{'role': 'system', 'content': system}, {'role': 'user', 'content': f'Project context:\n{context}\n\nRequested fix:\n{request}'}])
    if error:
        print(error)
        return
    patch = extract_patch(answer or '')
    if not patch:
        print(answer or 'No patch returned.')
        return
    patch_path = project_root() / '.devpilot' / 'proposed.patch'
    patch_path.parent.mkdir(exist_ok=True)
    patch_path.write_text(patch + '\n', encoding='utf-8')
    print('Proposed patch:\n')
    print(patch)
    if not args.apply:
        print(f'\nSaved to {patch_path}. Nothing was changed.')
        print('Review it, then run: devpilot apply')
        return
    if not load_config().get('permissions', {}).get('write_files', False):
        if input('Apply this patch to the working tree? [y/N] ').strip().lower() != 'y':
            print('Cancelled.')
            return
    result = subprocess.run(['git', 'apply', '--check', str(patch_path)], cwd=project_root(), capture_output=True, text=True)
    if result.returncode != 0:
        print('Patch validation failed:\n' + result.stderr)
        return
    backup_dir = project_root() / '.devpilot' / 'backups' / datetime.now().strftime('%Y%m%d-%H%M%S')
    backup_dir.mkdir(parents=True, exist_ok=True)
    result = subprocess.run(['git', 'apply', str(patch_path)], cwd=project_root(), capture_output=True, text=True)
    if result.returncode != 0:
        print('Patch application failed:\n' + result.stderr)
        return
    print('Patch applied successfully.')
    print('Run `devpilot build` or inspect with `git diff`.')


def cmd_apply(_args):
    patch = project_root() / '.devpilot' / 'proposed.patch'
    if not patch.exists():
        print('No proposed patch found. Run `devpilot fix "..."` first.')
        return
    result = subprocess.run(['git', 'apply', '--check', str(patch)], cwd=project_root(), capture_output=True, text=True)
    if result.returncode != 0:
        print('Patch validation failed:\n' + result.stderr)
        return
    if input('Apply the saved patch? [y/N] ').strip().lower() != 'y':
        print('Cancelled.')
        return
    result = subprocess.run(['git', 'apply', str(patch)], cwd=project_root(), capture_output=True, text=True)
    if result.returncode:
        print(result.stderr)
        return
    print('Patch applied successfully. Review with `git diff`.')


def cmd_explain(args):
    text = Path(args.file).read_text(encoding='utf-8', errors='ignore') if args.file else ''
    if not text:
        print('Provide a build/error log file.')
        return
    answer, error = online_chat([{'role': 'system', 'content': 'Explain software build errors clearly. Identify root cause, evidence, and safest fix. Do not claim to have executed commands.'}, {'role': 'user', 'content': text[-30000:]}])
    print(error if error else answer)


def main():
    parser = argparse.ArgumentParser(prog='devpilot', description='Online AI-assisted autonomous developer agent.')
    sub = parser.add_subparsers(dest='command', required=True)
    sub.add_parser('init').set_defaults(func=cmd_init)
    sub.add_parser('scan').set_defaults(func=cmd_scan)
    sub.add_parser('index').set_defaults(func=cmd_index)
    find = sub.add_parser('find'); find.add_argument('term', nargs='+'); find.set_defaults(func=cmd_find)
    sub.add_parser('doctor').set_defaults(func=cmd_doctor)
    ask = sub.add_parser('ask'); ask.add_argument('question', nargs='+'); ask.set_defaults(func=cmd_ask)
    fix = sub.add_parser('fix'); fix.add_argument('request', nargs='+'); fix.add_argument('--apply', action='store_true'); fix.set_defaults(func=cmd_fix)
    sub.add_parser('apply').set_defaults(func=cmd_apply)
    explain = sub.add_parser('explain'); explain.add_argument('file'); explain.set_defaults(func=cmd_explain)
    build = sub.add_parser('build'); build.add_argument('-y', '--yes', action='store_true'); build.set_defaults(func=cmd_build)
    args = parser.parse_args(); args.func(args)


if __name__ == '__main__':
    main()
