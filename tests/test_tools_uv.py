import pytest
from pathlib import Path
from pkg.tools.uv import UvTool, CLEAN_PATTERNS


def test_uv_tool_name(tmp_path):
    tool = UvTool(tmp_path)
    assert tool.name == "uv"


def test_uv_tool_project_dir(tmp_path):
    tool = UvTool(tmp_path)
    assert tool.project_dir == tmp_path


def test_clean_patterns_exist():
    assert ".venv" in CLEAN_PATTERNS
    assert "__pycache__" in CLEAN_PATTERNS
    assert "dist" in CLEAN_PATTERNS


def test_uv_tool_clean_empty_dir(tmp_path):
    tool = UvTool(tmp_path)
    result = tool.clean()
    assert result == 0


def test_uv_tool_clean_removes_dirs(tmp_path):
    (tmp_path / ".venv").mkdir()
    (tmp_path / "__pycache__").mkdir()
    tool = UvTool(tmp_path)
    result = tool.clean()
    assert result == 0
    assert not (tmp_path / ".venv").exists()
    assert not (tmp_path / "__pycache__").exists()


def test_uv_tool_create_gitignore(tmp_path):
    tool = UvTool(tmp_path)
    tool._create_gitignore()
    gitignore = tmp_path / ".gitignore"
    assert gitignore.exists()
    content = gitignore.read_text()
    assert ".venv/" in content
    assert "__pycache__/" in content


def test_build_runs_tests_first(tmp_path, mocker):
    tool = UvTool(tmp_path)
    mock_test = mocker.patch.object(tool, "test", return_value=0)
    mocker.patch("pkg.tools.uv.run_command", return_value=0)
    tool.build()
    mock_test.assert_called_once()


def test_build_aborts_on_test_failure(tmp_path, mocker):
    tool = UvTool(tmp_path)
    mocker.patch.object(tool, "test", return_value=1)
    mock_run = mocker.patch("pkg.tools.uv.run_command")
    result = tool.build()
    assert result == 1
    mock_run.assert_not_called()


def test_uv_tool_test(tmp_path, mocker):
    tool = UvTool(tmp_path)
    mock_run = mocker.patch("pkg.tools.uv.run_command", return_value=0)
    result = tool.test()
    assert result == 0
    mock_run.assert_called_once_with(["uv", "run", "pytest"], cwd=tmp_path)


def test_uv_tool_install(tmp_path, mocker):
    tool = UvTool(tmp_path)
    mock_run = mocker.patch("pkg.tools.uv.run_command", return_value=0)
    result = tool.install()
    assert result == 0
    mock_run.assert_called_once_with(["uv", "sync", "--group", "dev"], cwd=tmp_path)


def test_uv_tool_run_script(tmp_path, mocker):
    tool = UvTool(tmp_path)
    mock_run = mocker.patch("pkg.tools.uv.run_command", return_value=0)
    result = tool.run("myscript")
    assert result == 0
    mock_run.assert_called_once_with(["uv", "run", "myscript"], cwd=tmp_path)


def test_uv_tool_run_script_with_args(tmp_path, mocker):
    tool = UvTool(tmp_path)
    mock_run = mocker.patch("pkg.tools.uv.run_command", return_value=0)
    result = tool.run("myscript", ["--flag", "value"])
    assert result == 0
    mock_run.assert_called_once_with(["uv", "run", "myscript", "--flag", "value"], cwd=tmp_path)


def test_uv_tool_init(tmp_path, mocker):
    tool = UvTool(tmp_path)
    mock_run = mocker.patch("pkg.tools.uv.run_command", return_value=0)
    result = tool.init()
    assert result == 0
    mock_run.assert_called_once_with(["uv", "init"], cwd=tmp_path)
    assert (tmp_path / ".gitignore").exists()


def test_uv_tool_init_fails(tmp_path, mocker):
    tool = UvTool(tmp_path)
    mocker.patch("pkg.tools.uv.run_command", return_value=1)
    result = tool.init()
    assert result == 1


def test_uv_tool_clean_glob_patterns(tmp_path):
    (tmp_path / "foo.egg-info").mkdir()
    tool = UvTool(tmp_path)
    result = tool.clean()
    assert result == 0
    assert not (tmp_path / "foo.egg-info").exists()


def test_add_dev_dependencies(tmp_path):
    (tmp_path / "pyproject.toml").write_text('[project]\nname = "test"\n')
    tool = UvTool(tmp_path)
    tool._add_dev_dependencies()
    content = (tmp_path / "pyproject.toml").read_text()
    assert "[dependency-groups]" in content
    assert "pytest" in content
    assert "pytest-cov" in content
    assert "[tool.pytest.ini_options]" in content


def test_add_dev_dependencies_skips_if_exists(tmp_path):
    original = '[project]\nname = "test"\n\n[dependency-groups]\ndev = []\n'
    (tmp_path / "pyproject.toml").write_text(original)
    tool = UvTool(tmp_path)
    tool._add_dev_dependencies()
    assert (tmp_path / "pyproject.toml").read_text() == original


def test_add_dev_dependencies_no_pyproject(tmp_path):
    tool = UvTool(tmp_path)
    tool._add_dev_dependencies()  # Should not raise


def test_clean_patterns_include_coverage():
    assert "htmlcov" in CLEAN_PATTERNS
    assert ".coverage" in CLEAN_PATTERNS


def test_uv_tool_uplift(tmp_path):
    (tmp_path / "pyproject.toml").write_text('[project]\nname = "test"\n')
    tool = UvTool(tmp_path)
    result = tool.uplift()
    assert result == 0
    assert (tmp_path / ".gitignore").exists()
    content = (tmp_path / "pyproject.toml").read_text()
    assert "[dependency-groups]" in content


def test_uv_tool_uplift_idempotent(tmp_path):
    (tmp_path / "pyproject.toml").write_text('[project]\nname = "test"\n')
    (tmp_path / ".gitignore").write_text("existing")
    tool = UvTool(tmp_path)
    tool.uplift()
    tool.uplift()
    assert (tmp_path / ".gitignore").read_text() == "existing"
