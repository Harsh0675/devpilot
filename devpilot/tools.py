"""Safe, auditable project tools exposed to autonomous agents."""
import subprocess
from pathlib import Path

from .permissions import PermissionPolicy


class ProjectTools:
    def __init__(self, root=None, policy=None):
        self.root = Path(root or Path.cwd()).resolve()
        self.policy = policy or PermissionPolicy()

    def read(self, path):
        self.policy.check('read')
        target = (self.root / path).resolve()
        if self.root not in target.parents and target != self.root:
            raise PermissionError('Path escapes project root.')
        return target.read_text(encoding='utf-8', errors='ignore')

    def git_status(self):
        self.policy.check('git')
        return self._git('status', '--short')

    def git_diff(self):
        self.policy.check('git')
        return self._git('diff')

    def run_tests(self, command):
        self.policy.check('tests')
        return self._shell(command)

    def shell(self, command):
        self.policy.check('shell')
        return self._shell(command)

    def _git(self, *args):
        result = subprocess.run(['git', *args], cwd=self.root, text=True, capture_output=True, timeout=60)
        return result.stdout + result.stderr

    def _shell(self, command):
        result = subprocess.run(command, cwd=self.root, shell=True, text=True, capture_output=True, timeout=300)
        return {'returncode': result.returncode, 'stdout': result.stdout[-12000:], 'stderr': result.stderr[-12000:]}
