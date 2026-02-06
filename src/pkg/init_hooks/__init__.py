from pathlib import Path
from typing import Protocol

from rich.console import Console

console = Console()


class InitHook(Protocol):
    name: str
    enabled_by_default: bool

    def run(self, project_dir: Path, name: str) -> int: ...


_hooks: list[InitHook] = []


def register(hook: InitHook) -> InitHook:
    """Register an init hook."""
    _hooks.append(hook)
    return hook


def run_init_hooks(project_dir: Path, name: str, disabled: set[str] | None = None) -> int:
    """Run all registered init hooks."""
    disabled = disabled or set()

    for hook in _hooks:
        if hook.name in disabled:
            continue
        if not hook.enabled_by_default and hook.name not in disabled:
            continue

        console.print(f"[dim]Running {hook.name}...[/dim]")
        exit_code = hook.run(project_dir, name)
        if exit_code != 0:
            console.print(f"[red]Hook {hook.name} failed[/red]")
            return exit_code

    return 0


# Import hooks to trigger registration
from . import git, agent_md  # noqa: E402, F401
