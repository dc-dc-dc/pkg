import sys
from pathlib import Path

import click
from rich.console import Console

from . import __version__
from .config import Config, find_project_root
from .hooks import run_pre_hooks, run_post_hooks
from .init import create_pkg_config
from .init_hooks import run_init_hooks
from .plugins import PluginManager
from .tools import get_tool

console = Console()


class PkgContext:
    def __init__(self):
        self.project_dir = find_project_root()
        self.config = Config.load(self.project_dir)
        self.tool = get_tool(self.config.tool)(self.project_dir)
        self.plugin_manager = PluginManager()
        self.plugin_manager.load_plugins(self.config.plugins, self.config)


pass_context = click.make_pass_decorator(PkgContext, ensure=True)


def run_with_hooks(ctx: PkgContext, command: str, action: callable) -> int:
    hooks = ctx.config.get_hooks(command)

    ctx.plugin_manager.on_pre_command(command)
    if not run_pre_hooks(hooks, command, ctx.project_dir):
        return 1

    exit_code = action()

    if exit_code == 0:
        run_post_hooks(hooks, command, ctx.project_dir)

    ctx.plugin_manager.on_post_command(command, exit_code)
    return exit_code


@click.group()
@click.version_option(version=__version__)
@click.pass_context
def main(ctx):
    ctx.ensure_object(PkgContext)


@main.command()
@click.argument("name")
@click.option("--git/--no-git", default=True, help="Initialize git repository")
@click.option("--tool", required=True, help="Build tool to use")
@pass_context
def init(ctx: PkgContext, name: str, git: bool, tool: str):
    create_pkg_config(ctx.project_dir, tool)
    exit_code = ctx.tool.init(name=name)
    if exit_code != 0:
        sys.exit(exit_code)

    disabled = set() if git else {"git"}
    exit_code = run_init_hooks(ctx.project_dir, name, disabled=disabled)
    sys.exit(exit_code)


@main.command()
@pass_context
def build(ctx: PkgContext):
    exit_code = run_with_hooks(ctx, "build", ctx.tool.build)
    sys.exit(exit_code)


@main.command()
@pass_context
def test(ctx: PkgContext):
    exit_code = run_with_hooks(ctx, "test", ctx.tool.test)
    sys.exit(exit_code)


@main.command()
@pass_context
def install(ctx: PkgContext):
    exit_code = run_with_hooks(ctx, "install", ctx.tool.install)
    sys.exit(exit_code)


@main.command()
@pass_context
def clean(ctx: PkgContext):
    exit_code = run_with_hooks(ctx, "clean", ctx.tool.clean)
    sys.exit(exit_code)


@main.command()
@click.argument("script")
@click.argument("args", nargs=-1)
@pass_context
def run(ctx: PkgContext, script: str, args: tuple):
    def action():
        return ctx.tool.run(script, list(args) if args else None)

    exit_code = run_with_hooks(ctx, "run", action)
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
