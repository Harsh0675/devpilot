import argparse
import json
import subprocess
from pathlib import Path

IGNORE = {'.git', '.gradle', '.idea', 'build', '.devpilot', '__pycache__', '.venv'}

def project_root():
    return Path.cwd()

def iter_files(root):
    for path in root.rglob('*'):
        if path.is_file() and not any(part in IGNORE for part in path.parts):
            yield path

def cmd_init(_args):
    d = project_root() / '.devpilot'
    d.mkdir(exist_ok=True)
    state = d / 'config.json'
    if not state.exists():
        state.write_text(json.dumps({'version': 1, 'provider': 'none', 'permissions': {'write_files': False, 'run_commands': False}}, indent=2) + '\n')
    print(f'DevPilot initialized: {d}')

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

def cmd_ask(args):
    question = ' '.join(args.question).strip()
    print('DevPilot MVP (offline mode)')
    print(f'Request: {question}')
    print('\nNo AI provider is configured yet. DevPilot can currently inspect the project locally.')

def cmd_doctor(_args):
    root = project_root()
    checks = [
        ('Git repository', (root / '.git').exists()),
        ('Gradle wrapper', (root / 'gradlew').exists() or (root / 'gradlew.bat').exists()),
        ('Android manifest', any(root.rglob('AndroidManifest.xml'))),
        ('settings.gradle', any(root.glob('settings.gradle*'))),
        ('build.gradle', any(root.glob('build.gradle*'))),
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
    parser = argparse.ArgumentParser(prog='devpilot', description='AI-assisted developer agent.')
    sub = parser.add_subparsers(dest='command', required=True)
    sub.add_parser('init').set_defaults(func=cmd_init)
    sub.add_parser('scan').set_defaults(func=cmd_scan)
    sub.add_parser('doctor').set_defaults(func=cmd_doctor)
    ask = sub.add_parser('ask'); ask.add_argument('question', nargs='+'); ask.set_defaults(func=cmd_ask)
    build = sub.add_parser('build'); build.add_argument('-y', '--yes', action='store_true'); build.set_defaults(func=cmd_build)
    args = parser.parse_args(); args.func(args)

if __name__ == '__main__':
    main()
