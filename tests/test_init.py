import pytest
from pkg.init import create_pkg_config, DEFAULT_CONFIG


def test_create_pkg_config(tmp_path):
    create_pkg_config(tmp_path)
    config = tmp_path / "pkg.toml"
    assert config.exists()
    assert 'tool = "uv"' in config.read_text()


def test_create_pkg_config_custom_tool(tmp_path):
    create_pkg_config(tmp_path, tool="npm")
    config = tmp_path / "pkg.toml"
    assert 'tool = "npm"' in config.read_text()


def test_create_pkg_config_already_exists(tmp_path):
    (tmp_path / "pkg.toml").write_text("existing")
    create_pkg_config(tmp_path)
    assert (tmp_path / "pkg.toml").read_text() == "existing"
