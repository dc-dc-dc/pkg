import subprocess
import os
from pathlib import Path

from rich.console import Console

from .config import HookConfig

console = Console()


def run_hooks(
    hooks: list[str],
    phase: str,
    command: str,
    project_dir: Path,
    env: dict[str, str] | None = None,
) -> bool:
    if not hooks:
        return True

    hook_env = os.environ.copy()
    hook_env["PKG_COMMAND"] = command
    hook_env["PKG_PHASE"] = phase
    hook_env["PKG_PROJECT_DIR"] = str(project_dir)
    if env:
        hook_env.update(env)

    for hook in hooks:
        console.print(f"[dim]Running {phase} hook: {hook}[/dim]")
        result = subprocess.run(
            hook,
            shell=True,
            cwd=project_dir,
            env=hook_env,
        )
        if result.returncode != 0:
            console.print(f"[red]Hook failed: {hook}[/red]")
            return False

    return True


def run_pre_hooks(
    hook_config: HookConfig,
    command: str,
    project_dir: Path,
    env: dict[str, str] | None = None,
) -> bool:
    return run_hooks(hook_config.pre, "pre", command, project_dir, env)


def run_post_hooks(
    hook_config: HookConfig,
    command: str,
    project_dir: Path,
    env: dict[str, str] | None = None,
) -> bool:
    return run_hooks(hook_config.post, "post", command, project_dir, env)
