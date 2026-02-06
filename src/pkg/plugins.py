from abc import ABC, abstractmethod
from importlib.metadata import entry_points
from typing import Any

import click


class Plugin(ABC):
    @property
    @abstractmethod
    def name(self) -> str:
        ...

    def on_load(self, config: Any) -> None:
        pass

    def register_commands(self, cli: click.Group) -> None:
        pass

    def on_pre_command(self, command: str) -> None:
        pass

    def on_post_command(self, command: str, exit_code: int) -> None:
        pass


class PluginManager:
    def __init__(self):
        self.plugins: list[Plugin] = []

    def discover_plugins(self) -> dict[str, type[Plugin]]:
        discovered = {}
        eps = entry_points(group="pkg.plugins")
        for ep in eps:
            try:
                plugin_class = ep.load()
                if issubclass(plugin_class, Plugin):
                    discovered[ep.name] = plugin_class
            except Exception:
                pass
        return discovered

    def load_plugins(self, enabled: list[str], config: Any) -> None:
        available = self.discover_plugins()
        for name in enabled:
            if name in available:
                plugin = available[name]()
                plugin.on_load(config)
                self.plugins.append(plugin)

    def register_commands(self, cli: click.Group) -> None:
        for plugin in self.plugins:
            plugin.register_commands(cli)

    def on_pre_command(self, command: str) -> None:
        for plugin in self.plugins:
            plugin.on_pre_command(command)

    def on_post_command(self, command: str, exit_code: int) -> None:
        for plugin in self.plugins:
            plugin.on_post_command(command, exit_code)
