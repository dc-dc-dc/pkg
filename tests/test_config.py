import pytest
from pathlib import Path
from pkg.config import Config, HookConfig, find_project_root


def test_hook_config_defaults():
    hc = HookConfig()
    assert hc.pre == []
    assert hc.post == []


def test_config_defaults():
    cfg = Config()
    assert cfg.tool == "uv"
    assert cfg.hooks == {}
    assert cfg.plugins == []


def test_config_get_hooks_returns_empty_for_missing():
    cfg = Config()
    hc = cfg.get_hooks("build")
    assert hc.pre == []
    assert hc.post == []


def test_config_load_missing_file(tmp_path):
    cfg = Config.load(tmp_path)
    assert cfg.tool == "uv"


def test_config_load_valid_file(tmp_path):
    config_file = tmp_path / "pkg.toml"
    config_file.write_text("""
[pkg]
tool = "npm"

[hooks.build]
pre = ["echo pre"]
post = ["echo post"]

[plugins]
enabled = ["my_plugin"]
""")
    cfg = Config.load(tmp_path)
    assert cfg.tool == "npm"
    assert cfg.plugins == ["my_plugin"]
    assert cfg.get_hooks("build").pre == ["echo pre"]
    assert cfg.get_hooks("build").post == ["echo post"]


def test_find_project_root_with_pkg_toml(tmp_path):
    (tmp_path / "pkg.toml").touch()
    subdir = tmp_path / "src" / "pkg"
    subdir.mkdir(parents=True)
    assert find_project_root(subdir) == tmp_path


def test_find_project_root_with_pyproject(tmp_path):
    (tmp_path / "pyproject.toml").touch()
    subdir = tmp_path / "src"
    subdir.mkdir()
    assert find_project_root(subdir) == tmp_path


def test_find_project_root_fallback(tmp_path):
    subdir = tmp_path / "empty"
    subdir.mkdir()
    assert find_project_root(subdir) == subdir
