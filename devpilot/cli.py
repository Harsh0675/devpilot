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

# ... existing implementation retained ...


def main():
    parser = argparse.ArgumentParser(prog='devpilot', description='Production AI coding copilot for project intelligence, safe changes, tests, and builds.')
    parser.add_argument('--version', action='version', version='DevPilot 0.7.0')
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
