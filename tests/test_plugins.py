import pytest
import click
from pkg.plugins import Plugin, PluginManager


class MockPlugin(Plugin):
    @property
    def name(self) -> str:
        return "mock"

    def __init__(self):
        self.loaded = False
        self.pre_commands = []
        self.post_commands = []

    def on_load(self, config):
        self.loaded = True

    def on_pre_command(self, command: str):
        self.pre_commands.append(command)

    def on_post_command(self, command: str, exit_code: int):
        self.post_commands.append((command, exit_code))


def test_plugin_manager_init():
    pm = PluginManager()
    assert pm.plugins == []


def test_plugin_manager_on_pre_command():
    pm = PluginManager()
    plugin = MockPlugin()
    pm.plugins.append(plugin)
    pm.on_pre_command("build")
    assert plugin.pre_commands == ["build"]


def test_plugin_manager_on_post_command():
    pm = PluginManager()
    plugin = MockPlugin()
    pm.plugins.append(plugin)
    pm.on_post_command("build", 0)
    assert plugin.post_commands == [("build", 0)]


def test_plugin_manager_register_commands():
    pm = PluginManager()
    plugin = MockPlugin()
    pm.plugins.append(plugin)
    cli = click.Group()
    pm.register_commands(cli)  # Should not raise


def test_plugin_default_methods():
    class MinimalPlugin(Plugin):
        @property
        def name(self) -> str:
            return "minimal"

    p = MinimalPlugin()
    p.on_load(None)  # Should not raise
    p.register_commands(click.Group())  # Should not raise
    p.on_pre_command("build")  # Should not raise
    p.on_post_command("build", 0)  # Should not raise


def test_plugin_manager_load_plugins_empty():
    pm = PluginManager()
    pm.load_plugins([], None)
    assert pm.plugins == []


def test_plugin_manager_discover_returns_dict():
    pm = PluginManager()
    result = pm.discover_plugins()
    assert isinstance(result, dict)
