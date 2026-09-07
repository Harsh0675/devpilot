"""Persistent project memory for DevPilot autonomous workflows."""
import json
from datetime import datetime, timezone
from pathlib import Path


class ProjectMemory:
    def __init__(self, root=None):
        self.root = Path(root or Path.cwd()).resolve()
        self.dir = self.root / '.devpilot'
        self.path = self.dir / 'memory.json'

    def load(self):
        try:
            return json.loads(self.path.read_text(encoding='utf-8'))
        except (OSError, ValueError):
            return {'decisions': [], 'runs': [], 'facts': []}

    def save(self, data):
        self.dir.mkdir(parents=True, exist_ok=True)
        tmp = self.path.with_suffix('.tmp')
        tmp.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding='utf-8')
        tmp.replace(self.path)

    def record_run(self, request, status, summary=''):
        data = self.load()
        data.setdefault('runs', []).append({
            'time': datetime.now(timezone.utc).isoformat(),
            'request': request,
            'status': status,
            'summary': summary[:4000],
        })
        data['runs'] = data['runs'][-50:]
        self.save(data)

    def add_fact(self, fact):
        data = self.load()
        if fact and fact not in data.setdefault('facts', []):
            data['facts'].append(fact[:1000])
            data['facts'] = data['facts'][-100:]
            self.save(data)

    def context(self, limit=12000):
        data = self.load()
        parts = []
        if data.get('facts'):
            parts.append('PROJECT FACTS:\n' + '\n'.join('- ' + x for x in data['facts'][-30:]))
        if data.get('runs'):
            parts.append('RECENT RUNS:\n' + '\n'.join(f"- {x['status']}: {x['request']}" for x in data['runs'][-10:]))
        return '\n\n'.join(parts)[:limit]
