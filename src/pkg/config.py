import tomllib
from dataclasses import dataclass, field
from pathlib import Path

CONFIG_FILENAME = "pkg.toml"


@dataclass
class HookConfig:
    pre: list[str] = field(default_factory=list)
    post: list[str] = field(default_factory=list)


@dataclass
class Config:
    tool: str = "uv"
    hooks: dict[str, HookConfig] = field(default_factory=dict)
    plugins: list[str] = field(default_factory=list)

    @classmethod
    def load(cls, project_dir: Path) -> "Config":
        config_path = project_dir / CONFIG_FILENAME
        if not config_path.exists():
            return cls()

        with open(config_path, "rb") as f:
            data = tomllib.load(f)

        pkg_config = data.get("pkg", {})
        hooks_data = data.get("hooks", {})
        plugins_data = data.get("plugins", {})

        hooks = {}
        for command, hook_data in hooks_data.items():
            hooks[command] = HookConfig(
                pre=hook_data.get("pre", []),
                post=hook_data.get("post", []),
            )

        return cls(
            tool=pkg_config.get("tool", "uv"),
            hooks=hooks,
            plugins=plugins_data.get("enabled", []),
        )

    def get_hooks(self, command: str) -> HookConfig:
        return self.hooks.get(command, HookConfig())


def find_project_root(start: Path | None = None) -> Path:
    current = start or Path.cwd()
    while current != current.parent:
        if (current / CONFIG_FILENAME).exists():
            return current
        if (current / "pyproject.toml").exists():
            return current
        current = current.parent
    return start or Path.cwd()
