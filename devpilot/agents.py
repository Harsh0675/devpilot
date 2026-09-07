from dataclasses import dataclass
from typing import Callable, Dict, List, Optional

from .llm import chat


@dataclass
class AgentResult:
    role: str
    output: str


class Agent:
    def __init__(self, role: str, instruction: str):
        self.role = role
        self.instruction = instruction

    def run(self, request: str, context: str, model=None, provider=None, base_url=None):
        messages = [
            {'role': 'system', 'content': self.instruction},
            {'role': 'user', 'content': f'REPOSITORY CONTEXT:\n{context}\n\nDEVELOPER REQUEST:\n{request}'},
        ]
        output, error = chat(messages, model=model, provider=provider, base_url=base_url)
        if error:
            raise RuntimeError(error)
        return AgentResult(self.role, output or '')


class AgentOrchestrator:
    """Deterministic planner -> implementer -> reviewer -> verifier pipeline."""

    def __init__(self):
        self.agents = [
            Agent('planner', 'You are the planning agent. Produce an implementation plan, affected files, dependencies, risks, acceptance criteria, and verification strategy. Do not write code.'),
            Agent('coder', 'You are the senior coding agent. Produce a minimal, production-safe unified git diff in a ```diff block. Use repository-relative paths. Do not invent unrelated changes.'),
            Agent('reviewer', 'You are the security and code-review agent. Review the proposed implementation for correctness, security, regressions, maintainability, and test coverage. Return findings with severity and concrete fixes.'),
            Agent('tester', 'You are the verification agent. Define deterministic tests, build checks, static checks, and rollback criteria for the proposed implementation. Do not claim tests were executed.'),
        ]

    def run(self, request: str, context: str, model=None, provider=None, base_url=None, on_result: Optional[Callable[[AgentResult], None]] = None):
        results: List[AgentResult] = []
        working_context = context
        for agent in self.agents:
            result = agent.run(request, working_context, model=model, provider=provider, base_url=base_url)
            results.append(result)
            working_context += f'\n\n--- {result.role.upper()} OUTPUT ---\n{result.output[:30000]}'
            if on_result:
                on_result(result)
        return results
