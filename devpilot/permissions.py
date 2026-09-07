"""Explicit capability permissions for autonomous agents."""
from dataclasses import dataclass


@dataclass(frozen=True)
class PermissionPolicy:
    allow_read: bool = True
    allow_search: bool = True
    allow_git: bool = True
    allow_write: bool = False
    allow_shell: bool = False
    allow_tests: bool = False

    def check(self, capability):
        value = getattr(self, 'allow_' + capability, False)
        if not value:
            raise PermissionError(f"Permission denied for capability: {capability}. Enable it explicitly.")
        return True
