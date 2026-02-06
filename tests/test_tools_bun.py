import json

import pytest
from pathlib import Path
from pkg.tools.bun import BunTool, CLEAN_PATTERNS


def test_bun_tool_name(tmp_path):
    tool = BunTool(tmp_path)
    assert tool.name == "bun"


def test_bun_tool_project_dir(tmp_path):
    tool = BunTool(tmp_path)
    assert tool.project_dir == tmp_path


def test_clean_patterns_exist():
    assert "node_modules" in CLEAN_PATTERNS
    assert "dist" in CLEAN_PATTERNS
    assert "coverage" in CLEAN_PATTERNS


def test_bun_tool_clean_empty_dir(tmp_path):
    tool = BunTool(tmp_path)
    result = tool.clean()
    assert result == 0


def test_bun_tool_clean_removes_dirs(tmp_path):
    (tmp_path / "node_modules").mkdir()
    (tmp_path / "dist").mkdir()
    tool = BunTool(tmp_path)
    result = tool.clean()
    assert result == 0
    assert not (tmp_path / "node_modules").exists()
    assert not (tmp_path / "dist").exists()


def test_bun_tool_clean_removes_file(tmp_path):
    (tmp_path / "coverage").write_text("data")
    tool = BunTool(tmp_path)
    result = tool.clean()
    assert result == 0
    assert not (tmp_path / "coverage").exists()


def test_bun_tool_create_gitignore(tmp_path):
    tool = BunTool(tmp_path)
    tool._create_gitignore()
    gitignore = tmp_path / ".gitignore"
    assert gitignore.exists()
    content = gitignore.read_text()
    assert "node_modules/" in content
    assert "dist/" in content
    assert ".DS_Store" in content


def test_bun_tool_create_gitignore_skips_existing(tmp_path):
    (tmp_path / ".gitignore").write_text("existing")
    tool = BunTool(tmp_path)
    tool._create_gitignore()
    assert (tmp_path / ".gitignore").read_text() == "existing"


def test_build_runs_tests_first(tmp_path, mocker):
    tool = BunTool(tmp_path)
    mock_test = mocker.patch.object(tool, "test", return_value=0)
    mocker.patch("pkg.tools.bun.run_command", return_value=0)
    tool.build()
    mock_test.assert_called_once()


def test_build_aborts_on_test_failure(tmp_path, mocker):
    tool = BunTool(tmp_path)
    mocker.patch.object(tool, "test", return_value=1)
    mock_run = mocker.patch("pkg.tools.bun.run_command")
    result = tool.build()
    assert result == 1
    mock_run.assert_not_called()


def test_bun_tool_test(tmp_path, mocker):
    tool = BunTool(tmp_path)
    mock_run = mocker.patch("pkg.tools.bun.run_command", return_value=0)
    result = tool.test()
    assert result == 0
    mock_run.assert_called_once_with(["bun", "test", "--coverage"], cwd=tmp_path)


def test_bun_tool_install(tmp_path, mocker):
    tool = BunTool(tmp_path)
    mock_run = mocker.patch("pkg.tools.bun.run_command", return_value=0)
    result = tool.install()
    assert result == 0
    mock_run.assert_called_once_with(["bun", "install"], cwd=tmp_path)


def test_bun_tool_run_script(tmp_path, mocker):
    tool = BunTool(tmp_path)
    mock_run = mocker.patch("pkg.tools.bun.run_command", return_value=0)
    result = tool.run("myscript")
    assert result == 0
    mock_run.assert_called_once_with(["bun", "run", "myscript"], cwd=tmp_path)


def test_bun_tool_run_script_with_args(tmp_path, mocker):
    tool = BunTool(tmp_path)
    mock_run = mocker.patch("pkg.tools.bun.run_command", return_value=0)
    result = tool.run("myscript", ["--flag", "value"])
    assert result == 0
    mock_run.assert_called_once_with(["bun", "run", "myscript", "--flag", "value"], cwd=tmp_path)


def test_bun_tool_init(tmp_path, mocker):
    tool = BunTool(tmp_path)
    mock_run = mocker.patch("pkg.tools.bun.run_command", return_value=0)
    result = tool.init()
    assert result == 0
    mock_run.assert_called_once_with(["bun", "init", "-y"], cwd=tmp_path)
    assert (tmp_path / ".gitignore").exists()


def test_bun_tool_init_fails(tmp_path, mocker):
    tool = BunTool(tmp_path)
    mocker.patch("pkg.tools.bun.run_command", return_value=1)
    result = tool.init()
    assert result == 1


def test_add_dev_dependencies(tmp_path):
    (tmp_path / "package.json").write_text('{"name": "test"}')
    tool = BunTool(tmp_path)
    tool._add_dev_dependencies()
    data = json.loads((tmp_path / "package.json").read_text())
    assert "@types/bun" in data["devDependencies"]
    assert data["scripts"]["test"] == "bun test --coverage"
    assert data["scripts"]["build"] == "bun build ./index.ts --outdir ./dist"


def test_add_dev_dependencies_skips_if_exists(tmp_path):
    original = {
        "name": "test",
        "devDependencies": {"@types/bun": "latest"},
        "scripts": {"test": "bun test --coverage", "build": "bun build ./index.ts --outdir ./dist"},
    }
    (tmp_path / "package.json").write_text(json.dumps(original, indent=2) + "\n")
    tool = BunTool(tmp_path)
    tool._add_dev_dependencies()
    data = json.loads((tmp_path / "package.json").read_text())
    assert data == original


def test_add_dev_dependencies_no_package_json(tmp_path):
    tool = BunTool(tmp_path)
    tool._add_dev_dependencies()  # Should not raise


def test_clean_patterns_include_build_dirs():
    assert ".turbo" in CLEAN_PATTERNS
    assert ".next" in CLEAN_PATTERNS
    assert ".nuxt" in CLEAN_PATTERNS
    assert ".output" in CLEAN_PATTERNS
    assert "build" in CLEAN_PATTERNS


def test_bun_tool_uplift(tmp_path):
    (tmp_path / "package.json").write_text('{"name": "test"}')
    tool = BunTool(tmp_path)
    result = tool.uplift()
    assert result == 0
    assert (tmp_path / ".gitignore").exists()
    data = json.loads((tmp_path / "package.json").read_text())
    assert "@types/bun" in data["devDependencies"]


def test_bun_tool_uplift_idempotent(tmp_path):
    (tmp_path / "package.json").write_text('{"name": "test"}')
    (tmp_path / ".gitignore").write_text("existing")
    tool = BunTool(tmp_path)
    tool.uplift()
    tool.uplift()
    assert (tmp_path / ".gitignore").read_text() == "existing"
