import pytest
from click.testing import CliRunner
from pkg.cli import main, PkgContext, run_with_hooks
from pkg.config import Config, HookConfig


@pytest.fixture
def runner():
    return CliRunner()


def test_main_version(runner):
    result = runner.invoke(main, ["--version"])
    assert result.exit_code == 0
    assert "0.1.0" in result.output


def test_main_help(runner):
    result = runner.invoke(main, ["--help"])
    assert result.exit_code == 0
    assert "build" in result.output
    assert "test" in result.output


def test_pkg_context(tmp_path, monkeypatch):
    (tmp_path / "pkg.toml").write_text('[pkg]\ntool = "uv"')
    monkeypatch.chdir(tmp_path)
    ctx = PkgContext()
    assert ctx.config.tool == "uv"
    assert ctx.tool.name == "uv"


def test_run_with_hooks_success(tmp_path, monkeypatch):
    (tmp_path / "pkg.toml").write_text('[pkg]\ntool = "uv"')
    monkeypatch.chdir(tmp_path)
    ctx = PkgContext()
    result = run_with_hooks(ctx, "test", lambda: 0)
    assert result == 0


def test_run_with_hooks_failure(tmp_path, monkeypatch):
    (tmp_path / "pkg.toml").write_text('[pkg]\ntool = "uv"')
    monkeypatch.chdir(tmp_path)
    ctx = PkgContext()
    result = run_with_hooks(ctx, "test", lambda: 1)
    assert result == 1


def test_run_with_hooks_pre_hook_fails(tmp_path, monkeypatch):
    (tmp_path / "pkg.toml").write_text('''[pkg]
tool = "uv"
[hooks.test]
pre = ["false"]
''')
    monkeypatch.chdir(tmp_path)
    ctx = PkgContext()
    result = run_with_hooks(ctx, "test", lambda: 0)
    assert result == 1


def test_build_command(runner, tmp_path, mocker):
    mocker.patch("pkg.cli.find_project_root", return_value=tmp_path)
    mocker.patch("pkg.tools.uv.run_command", return_value=0)
    (tmp_path / "pkg.toml").write_text('[pkg]\ntool = "uv"')
    result = runner.invoke(main, ["build"])
    assert result.exit_code == 0


def test_test_command(runner, tmp_path, mocker):
    mocker.patch("pkg.cli.find_project_root", return_value=tmp_path)
    mocker.patch("pkg.tools.uv.run_command", return_value=0)
    (tmp_path / "pkg.toml").write_text('[pkg]\ntool = "uv"')
    result = runner.invoke(main, ["test"])
    assert result.exit_code == 0


def test_install_command(runner, tmp_path, mocker):
    mocker.patch("pkg.cli.find_project_root", return_value=tmp_path)
    mocker.patch("pkg.tools.uv.run_command", return_value=0)
    (tmp_path / "pkg.toml").write_text('[pkg]\ntool = "uv"')
    result = runner.invoke(main, ["install"])
    assert result.exit_code == 0


def test_clean_command(runner, tmp_path, mocker):
    mocker.patch("pkg.cli.find_project_root", return_value=tmp_path)
    (tmp_path / "pkg.toml").write_text('[pkg]\ntool = "uv"')
    result = runner.invoke(main, ["clean"])
    assert result.exit_code == 0


def test_run_command(runner, tmp_path, mocker):
    mocker.patch("pkg.cli.find_project_root", return_value=tmp_path)
    mocker.patch("pkg.tools.uv.run_command", return_value=0)
    (tmp_path / "pkg.toml").write_text('[pkg]\ntool = "uv"')
    result = runner.invoke(main, ["run", "echo", "hello"])
    assert result.exit_code == 0


def test_uplift_command(runner, tmp_path, mocker):
    mocker.patch("pkg.cli.find_project_root", return_value=tmp_path)
    (tmp_path / "pkg.toml").write_text('[pkg]\ntool = "uv"')
    result = runner.invoke(main, ["uplift"])
    assert result.exit_code == 0


def test_uplift_creates_pkg_toml(runner, tmp_path, mocker):
    mocker.patch("pkg.cli.find_project_root", return_value=tmp_path)
    result = runner.invoke(main, ["uplift"])
    assert result.exit_code == 0
    assert (tmp_path / "pkg.toml").exists()


def test_uplift_idempotent(runner, tmp_path, mocker):
    mocker.patch("pkg.cli.find_project_root", return_value=tmp_path)
    (tmp_path / "pkg.toml").write_text('[pkg]\ntool = "uv"')
    (tmp_path / ".gitignore").write_text("existing")
    (tmp_path / "AGENT.md").write_text("existing")
    (tmp_path / ".git").mkdir()
    result = runner.invoke(main, ["uplift"])
    assert result.exit_code == 0
    assert (tmp_path / ".gitignore").read_text() == "existing"
    assert (tmp_path / "AGENT.md").read_text() == "existing"


def test_uplift_in_help(runner):
    result = runner.invoke(main, ["--help"])
    assert "uplift" in result.output
