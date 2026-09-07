import argparse
import json
import os
import re
import subprocess
import sys
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

IGNORE = {'.git', '.gradle', '.idea', 'build', '.devpilot', '__pycache__', '.venv', 'node_modules', 'dist', '.tox'}
TEXT_EXTENSIONS = {'.py', '.js', '.ts', '.tsx', '.jsx', '.java', '.kt', '.kts', '.xml', '.json', '.md', '.txt', '.gradle', '.properties', '.yml', '.yaml', '.toml', '.sh', '.c', '.cpp', '.h', '.hpp', '.rs', '.go', '.swift', '.dart', '.sql'}
MAX_FILE_CHARS = 12000
MAX_CONTEXT_CHARS = 70000
DEFAULT_CONFIG = {
    'version': 6,
    'provider': 'openai-compatible',
    'model': 'gpt-4o-mini',
    'base_url': 'https://api.openai.com/v1',
    'permissions': {'write_files': False, 'run_commands': False},
}


def project_root():
    return Path.cwd()


def devpilot_dir():
    path = project_root() / '.devpilot'
    path.mkdir(exist_ok=True)
    return path


def iter_files(root=None):
    root = root or project_root()
    for path in root.rglob('*'):
        if path.is_file() and not any(part in IGNORE for part in path.parts):
            yield path


def load_config():
    path = project_root() / '.devpilot' / 'config.json'
    if path.exists():
        try:
            config = json.loads(path.read_text(encoding='utf-8'))
            merged = dict(DEFAULT_CONFIG)
            merged.update(config)
            merged['permissions'] = {**DEFAULT_CONFIG['permissions'], **config.get('permissions', {})}
            return merged
        except (OSError, ValueError):
            pass
    return dict(DEFAULT_CONFIG)


def save_config(config):
    path = devpilot_dir() / 'config.json'
    path.write_text(json.dumps(config, indent=2) + '\n', encoding='utf-8')


def run(command, timeout=120):
    try:
        return subprocess.run(command, cwd=project_root(), capture_output=True, text=True, timeout=timeout)
    except FileNotFoundError:
        return subprocess.CompletedProcess(command, 127, '', f'Command not found: {command[0]}')
    except subprocess.TimeoutExpired as exc:
        return subprocess.CompletedProcess(command, 124, exc.stdout or '', f'Command timed out after {timeout}s')


def git(*args):
    return run(['git', *args], timeout=30)


def cmd_init(_args):
    config = load_config()
    save_config(config)
    print(f'DevPilot initialized: {devpilot_dir()}')
    print('Set DEVPILOT_API_KEY to enable online AI.')
    print('Use `devpilot doctor` to validate the environment.')


def cmd_scan(_args):
    files = list(iter_files())
    print(f'Project: {project_root()}')
    print(f'Files: {len(files)}')
    by_ext = {}
    for path in files:
        ext = path.suffix.lower() or '[no extension]'
        by_ext[ext] = by_ext.get(ext, 0) + 1
    for ext, count in sorted(by_ext.items(), key=lambda x: (-x[1], x[0])):
        print(f'  {ext}: {count}')


def make_context(question='', limit=12):
    words = {w.lower() for w in re.findall(r'[A-Za-z0-9_]{3,}', question)}
    candidates = []
    for path in iter_files():
        if path.suffix.lower() not in TEXT_EXTENSIONS:
            continue
        try:
            text = path.read_text(encoding='utf-8', errors='ignore')
        except OSError:
            continue
        lowered = text.lower()
        score = sum(lowered.count(w) for w in words)
        name_score = sum(2 for w in words if w in path.name.lower())
        if score or name_score:
            candidates.append((score + name_score, path, text))
    candidates.sort(key=lambda x: (-x[0], str(x[1])))
    if not candidates:
        candidates = [(0, p, p.read_text(encoding='utf-8', errors='ignore')) for p in list(iter_files()) if p.suffix.lower() in TEXT_EXTENSIONS][:limit]
    chunks = []
    total = 0
    for _, path, text in candidates[:limit]:
        chunk = f'FILE: {path.relative_to(project_root())}\n{text[:MAX_FILE_CHARS]}'
        if total + len(chunk) > MAX_CONTEXT_CHARS:
            break
        chunks.append(chunk)
        total += len(chunk)
    return '\n\n---\n\n'.join(chunks)


def online_chat(messages, timeout=120):
    api_key = os.getenv('DEVPILOT_API_KEY') or os.getenv('OPENAI_API_KEY')
    if not api_key:
        return None, 'DEVPILOT_API_KEY is not set.'
    config = load_config()
    base = os.getenv('DEVPILOT_BASE_URL', config.get('base_url', DEFAULT_CONFIG['base_url'])).rstrip('/')
    model = os.getenv('DEVPILOT_MODEL', config.get('model', DEFAULT_CONFIG['model']))
    payload = {'model': model, 'messages': messages, 'temperature': 0.2}
    request = urllib.request.Request(
        base + '/chat/completions',
        data=json.dumps(payload).encode('utf-8'),
        headers={'Authorization': f'Bearer {api_key}', 'Content-Type': 'application/json', 'User-Agent': 'DevPilot/0.6.0'},
        method='POST',
    )
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            data = json.loads(response.read().decode('utf-8'))
        content = data['choices'][0]['message']['content']
        return content, None
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode(errors='ignore')[:800]
        return None, f'AI API error {exc.code}: {detail}'
    except (urllib.error.URLError, TimeoutError) as exc:
        return None, f'Connection error: {exc}'
    except (KeyError, IndexError, ValueError) as exc:
        return None, f'Invalid AI response: {exc}'


def cmd_ask(args):
    question = ' '.join(args.question).strip()
    context = make_context(question)
    answer, error = online_chat([
        {'role': 'system', 'content': 'You are DevPilot, a production software-engineering copilot. Use the supplied repository context. Be precise, identify assumptions, and never claim to have executed commands or edited files unless the CLI actually did so.'},
        {'role': 'user', 'content': f'REPOSITORY CONTEXT:\n{context}\n\nDEVELOPER REQUEST:\n{question}'},
    ])
    print(error if error else answer)


def cmd_chat(_args):
    print('DevPilot interactive copilot. Type `exit` to quit.')
    history = []
    while True:
        try:
            question = input('devpilot> ').strip()
        except (EOFError, KeyboardInterrupt):
            print()
            return
        if question.lower() in {'exit', 'quit'}:
            return
        if not question:
            continue
        context = make_context(question)
        messages = [{'role': 'system', 'content': 'You are DevPilot, a production coding copilot. Answer using repository context. Never pretend to execute tools.'}]
        messages.extend(history[-6:])
        messages.append({'role': 'user', 'content': f'REPOSITORY CONTEXT:\n{context}\n\nREQUEST:\n{question}'})
        answer, error = online_chat(messages)
        if error:
            print(error)
            continue
        print(answer)
        history.extend([{'role': 'user', 'content': question}, {'role': 'assistant', 'content': answer}])


def cmd_index(_args):
    files = []
    for path in iter_files():
        if path.suffix.lower() in TEXT_EXTENSIONS:
            try:
                text = path.read_text(encoding='utf-8', errors='ignore')
                files.append({'path': str(path.relative_to(project_root())), 'chars': len(text), 'lines': text.count('\n') + 1, 'extension': path.suffix.lower()})
            except OSError:
                pass
    payload = {'version': 2, 'created_at': datetime.now(timezone.utc).isoformat(), 'files': files}
    (devpilot_dir() / 'index.json').write_text(json.dumps(payload, indent=2) + '\n', encoding='utf-8')
    print(f'Indexed {len(files)} text files.')


def cmd_find(args):
    term = ' '.join(args.term).lower()
    hits = 0
    for path in iter_files():
        if path.suffix.lower() not in TEXT_EXTENSIONS:
            continue
        try:
            for number, line in enumerate(path.read_text(encoding='utf-8', errors='ignore').splitlines(), 1):
                if term in line.lower():
                    print(f'{path.relative_to(project_root())}:{number}: {line.strip()[:240]}')
                    hits += 1
        except OSError:
            pass
    print(f'\n{hits} match(es).')


def cmd_status(_args):
    result = git('status', '--short', '--branch')
    if result.returncode:
        print(result.stderr.strip() or 'Not a Git repository.')
        return
    print(result.stdout.rstrip() or 'Working tree clean.')


def cmd_diff(args):
    result = git('diff', '--', *args.path)
    print(result.stdout if result.stdout else 'No unstaged changes.')
    if result.stderr:
        print(result.stderr, file=sys.stderr)


def cmd_doctor(_args):
    root = project_root()
    checks = [
        ('Git repository', (root / '.git').exists()),
        ('Gradle wrapper', (root / 'gradlew').exists() or (root / 'gradlew.bat').exists()),
        ('Android manifest', any(root.rglob('AndroidManifest.xml'))),
        ('settings.gradle', any(root.glob('settings.gradle*'))),
        ('build.gradle', any(root.glob('build.gradle*'))),
        ('Python', sys.version_info >= (3, 9)),
        ('Online API key', bool(os.getenv('DEVPILOT_API_KEY') or os.getenv('OPENAI_API_KEY'))),
    ]
    print('DevPilot Doctor\n')
    for name, ok in checks:
        print(f"[{'OK' if ok else 'INFO'}] {name}")


def gradle_command(root):
    if os.name == 'nt' and (root / 'gradlew.bat').exists():
        return ['gradlew.bat']
    if (root / 'gradlew').exists():
        return ['./gradlew']
    return None


def command_allowed(flag_name, question):
    if load_config().get('permissions', {}).get(flag_name, False):
        return True
    return input(question).strip().lower() == 'y'


def cmd_build(args):
    command = gradle_command(project_root())
    if not command:
        print('No Gradle wrapper found. Build currently supports Gradle projects.')
        return
    if not args.yes and not command_allowed('run_commands', 'Run Gradle assembleDebug? [y/N] '):
        print('Cancelled.')
        return
    result = run(command + ['assembleDebug'], timeout=args.timeout)
    print(result.stdout, end='')
    if result.stderr:
        print(result.stderr, file=sys.stderr, end='')
    raise SystemExit(result.returncode)


def cmd_test(args):
    command = gradle_command(project_root())
    if command:
        task = args.task or 'test'
        if not args.yes and not command_allowed('run_commands', f'Run Gradle {task}? [y/N] '):
            print('Cancelled.')
            return
        result = run(command + [task], timeout=args.timeout)
    elif (project_root() / 'pyproject.toml').exists():
        if not args.yes and not command_allowed('run_commands', 'Run Python tests? [y/N] '):
            print('Cancelled.')
            return
        result = run([sys.executable, '-m', 'pytest'], timeout=args.timeout)
    else:
        print('No supported test runner detected.')
        return
    print(result.stdout, end='')
    if result.stderr:
        print(result.stderr, file=sys.stderr, end='')
    raise SystemExit(result.returncode)


def extract_patch(text):
    match = re.search(r'```diff\s*(.*?)```', text or '', flags=re.DOTALL | re.IGNORECASE)
    if match:
        return match.group(1).strip()
    if text and ('diff --git ' in text or '--- a/' in text):
        return text[text.find('diff --git ') if 'diff --git ' in text else text.find('--- a/'):].strip()
    return None


def cmd_plan(args):
    request = ' '.join(args.request).strip()
    context = make_context(request, limit=16)
    answer, error = online_chat([
        {'role': 'system', 'content': 'You are DevPilot planning mode. Produce a concise implementation plan with: goal, files to inspect/change, steps, risks, and verification commands. Do not edit files.'},
        {'role': 'user', 'content': f'PROJECT:\n{context}\n\nREQUEST:\n{request}'},
    ])
    print(error if error else answer)


def cmd_fix(args):
    request = ' '.join(args.request).strip()
    context = make_context(request, limit=16)
    system = '''You are DevPilot, a production coding agent. Return ONLY a unified git diff inside a ```diff block. Use repository-relative paths. Keep the change minimal, compatible with the existing architecture, secure, and testable. Do not invent unrelated files. Never include prose outside the diff.'''
    answer, error = online_chat([{'role': 'system', 'content': system}, {'role': 'user', 'content': f'PROJECT CONTEXT:\n{context}\n\nREQUEST:\n{request}'}])
    if error:
        print(error)
        return
    patch = extract_patch(answer)
    if not patch:
        print(answer or 'No patch returned.')
        return
    patch_path = devpilot_dir() / 'proposed.patch'
    patch_path.write_text(patch + '\n', encoding='utf-8')
    print('Proposed patch:\n')
    print(patch)
    if not args.apply:
        print(f'\nSaved to {patch_path}. Nothing was changed.')
        print('Review it, then run: devpilot apply')
        return
    apply_patch(patch_path, force=args.yes)


def apply_patch(patch_path, force=False):
    check = git('apply', '--check', str(patch_path))
    if check.returncode:
        print('Patch validation failed:\n' + (check.stderr or check.stdout))
        return False
    if not force and not command_allowed('write_files', 'Apply this patch to the working tree? [y/N] '):
        print('Cancelled.')
        return False
    result = git('apply', str(patch_path))
    if result.returncode:
        print('Patch application failed:\n' + result.stderr)
        return False
    print('Patch applied successfully. Review with `devpilot diff` and run tests.')
    return True


def cmd_apply(args):
    patch = devpilot_dir() / 'proposed.patch'
    if not patch.exists():
        print('No proposed patch found. Run `devpilot fix "..."` first.')
        return
    apply_patch(patch, force=args.yes)


def cmd_explain(args):
    try:
        text = Path(args.file).read_text(encoding='utf-8', errors='ignore')
    except OSError as exc:
        print(f'Cannot read log: {exc}')
        return
    answer, error = online_chat([
        {'role': 'system', 'content': 'Explain software build errors clearly. Identify root cause, evidence, likely fix, and verification steps. Do not claim to have executed commands.'},
        {'role': 'user', 'content': text[-40000:]},
    ])
    print(error if error else answer)


def cmd_config(args):
    config = load_config()
    if args.model:
        config['model'] = args.model
    if args.base_url:
        config['base_url'] = args.base_url.rstrip('/')
    if args.allow_write:
        config['permissions']['write_files'] = True
    if args.allow_commands:
        config['permissions']['run_commands'] = True
    save_config(config)
    print(json.dumps(config, indent=2))


def main():
    parser = argparse.ArgumentParser(prog='devpilot', description='Production AI coding copilot for project intelligence, safe changes, tests, and builds.')
    parser.add_argument('--version', action='version', version='DevPilot 0.6.0')
    sub = parser.add_subparsers(dest='command', required=True)

    sub.add_parser('init').set_defaults(func=cmd_init)
    sub.add_parser('scan').set_defaults(func=cmd_scan)
    sub.add_parser('index').set_defaults(func=cmd_index)
    find = sub.add_parser('find'); find.add_argument('term', nargs='+'); find.set_defaults(func=cmd_find)
    sub.add_parser('status').set_defaults(func=cmd_status)
    diff = sub.add_parser('diff'); diff.add_argument('path', nargs='*', default=[]); diff.set_defaults(func=cmd_diff)
    sub.add_parser('doctor').set_defaults(func=cmd_doctor)
    ask = sub.add_parser('ask'); ask.add_argument('question', nargs='+'); ask.set_defaults(func=cmd_ask)
    sub.add_parser('chat').set_defaults(func=cmd_chat)
    plan = sub.add_parser('plan'); plan.add_argument('request', nargs='+'); plan.set_defaults(func=cmd_plan)
    fix = sub.add_parser('fix'); fix.add_argument('request', nargs='+'); fix.add_argument('--apply', action='store_true'); fix.add_argument('-y', '--yes', action='store_true'); fix.set_defaults(func=cmd_fix)
    apply = sub.add_parser('apply'); apply.add_argument('-y', '--yes', action='store_true'); apply.set_defaults(func=cmd_apply)
    explain = sub.add_parser('explain'); explain.add_argument('file'); explain.set_defaults(func=cmd_explain)
    build = sub.add_parser('build'); build.add_argument('-y', '--yes', action='store_true'); build.add_argument('--timeout', type=int, default=900); build.set_defaults(func=cmd_build)
    test = sub.add_parser('test'); test.add_argument('task', nargs='?'); test.add_argument('-y', '--yes', action='store_true'); test.add_argument('--timeout', type=int, default=900); test.set_defaults(func=cmd_test)
    config = sub.add_parser('config'); config.add_argument('--model'); config.add_argument('--base-url'); config.add_argument('--allow-write', action='store_true'); config.add_argument('--allow-commands', action='store_true'); config.set_defaults(func=cmd_config)

    args = parser.parse_args()
    args.func(args)


if __name__ == '__main__':
    main()
