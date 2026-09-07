from dataclasses import dataclass
from typing import Callable, List, Optional

from .llm import chat
from .memory import ProjectMemory


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
            Agent('architect', 'You are the software architect. Identify architecture, interfaces, dependencies, risks, and acceptance criteria. Do not write code.'),
            Agent('planner', 'You are the planning agent. Turn the architecture into an ordered implementation plan with affected files and verification steps. Do not write code.'),
            Agent('coder', 'You are the senior coding agent. Produce a minimal, production-safe unified git diff in a ```diff block. Use repository-relative paths. Do not invent unrelated changes.'),
            Agent('security', 'You are the security agent. Review the proposed implementation for secrets, injection, unsafe execution, path traversal, dependency, and privilege risks. Return severity and concrete fixes.'),
            Agent('reviewer', 'You are the senior code-review agent. Check correctness, regressions, maintainability, API compatibility, and test coverage. Return findings with severity and concrete fixes.'),
            Agent('tester', 'You are the verification agent. Define deterministic tests, build checks, static checks, expected outcomes, and rollback criteria. Do not claim tests were executed.'),
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


class AutonomousAgent:
    """Bounded autonomous reasoning loop. It plans and verifies; writes/execution stay permission-gated."""

    def __init__(self, root=None, max_steps=4):
        self.memory = ProjectMemory(root)
        self.max_steps = max(1, min(int(max_steps), 8))

    def run(self, request, context, model=None, provider=None, base_url=None, on_result=None):
        memory_context = self.memory.context()
        full_context = (context + '\n\n' + memory_context).strip()
        results = []
        stages = [
            ('architect', 'Design a safe architecture and acceptance criteria.'),
            ('planner', 'Create an executable plan. Identify exact files, commands, tests, and stop conditions.'),
            ('implementer', 'Propose the smallest production-safe patch as a unified diff. Never assume a command was executed.'),
            ('verifier', 'Audit the plan and patch. State what must be tested, likely failures, and whether the request is ready for human-approved execution.'),
        ][:self.max_steps]
        for role, instruction in stages:
            result = Agent(role, instruction).run(request, full_context, model=model, provider=provider, base_url=base_url)
            results.append(result)
            full_context += f'\n\n--- {role.upper()} OUTPUT ---\n{result.output[:30000]}'
            if on_result:
                on_result(result)
        self.memory.record_run(request, 'planned', results[-1].output if results else '')
        return results
