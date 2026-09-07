from pathlib import Path

import pytest

from devpilot.executor import AutonomousExecutor


def test_execution_requires_write_permission(tmp_path):
    (tmp_path / '.devpilot').mkdir()
    (tmp_path / '.devpilot' / 'proposed.patch').write_text('')
    executor = AutonomousExecutor(tmp_path)
    with pytest.raises(PermissionError):
        executor.apply()


def test_executor_rejects_missing_patch(tmp_path):
    executor = AutonomousExecutor(tmp_path, allow_write=True)
    with pytest.raises(FileNotFoundError):
        executor.apply()
