"""Permission-gated autonomous execution engine for DevPilot."""
from dataclasses import dataclass
from pathlib import Path
import re

from .memory import ProjectMemory
from .tools import ProjectTools
from .permissions import PermissionPolicy


@dataclass
class ExecutionResult:
    stage: str
    status: str
    detail: str


class AutonomousExecutor:
    """Apply a reviewed patch and optionally run tests/builds with explicit permissions."""

    def __init__(self, root=None, allow_write=False, allow_commands=False):
        self.root = Path(root or Path.cwd()).resolve()
        self.policy = PermissionPolicy(allow_write=allow_write, allow_shell=allow_commands, allow_tests=allow_commands)
        self.tools = ProjectTools(self.root, self.policy)
        self.memory = ProjectMemory(self.root)

    def _safe_patch_path(self):
        path = self.root / '.devpilot' / 'proposed.patch'
        if not path.exists():
            raise FileNotFoundError('No .devpilot/proposed.patch found.')
        return path

    def apply(self):
        self.policy.check('write')
        patch = self._safe_patch_path()
        check = self.tools._git('apply', '--check', str(patch))
        if 'error:' in check.lower() or 'fatal:' in check.lower():
            return ExecutionResult('apply', 'failed', check[-12000:])
        result = self.tools._git('apply', str(patch))
        status = 'passed' if not result.strip() else 'failed'
        return ExecutionResult('apply', status, result[-12000:] or 'Patch applied successfully.')

    def verify(self, test_command=None, build_command=None):
        results = []
        if test_command:
            results.append(('test', self.tools.run_tests(test_command)))
        if build_command:
            results.append(('build', self.tools.run_tests(build_command)))
        return [ExecutionResult(stage, 'passed' if data['returncode'] == 0 else 'failed', (data['stdout'] + '\n' + data['stderr']).strip()[-12000:]) for stage, data in results]

    def run(self, test_command=None, build_command=None):
        results = [self.apply()]
        if results[0].status != 'passed':
            self.memory.record_run('autonomous execution', 'failed', results[0].detail)
            return results
        try:
            results.extend(self.verify(test_command, build_command))
        except PermissionError as exc:
            results.append(ExecutionResult('verify', 'blocked', str(exc)))
        final = 'passed' if all(x.status == 'passed' for x in results) else 'failed'
        self.memory.record_run('autonomous execution', final, '\n'.join(x.detail for x in results)[-4000:])
        return results
