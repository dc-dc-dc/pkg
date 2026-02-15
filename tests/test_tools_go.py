import pytest
from pathlib import Path
from pkg.tools.go import GoTool, CLEAN_PATTERNS


def test_go_tool_name(tmp_path):
    tool = GoTool(tmp_path)
    assert tool.name == "go"


def test_go_tool_project_dir(tmp_path):
    tool = GoTool(tmp_path)
    assert tool.project_dir == tmp_path


def test_clean_patterns_exist():
    assert "bin" in CLEAN_PATTERNS
    assert "dist" in CLEAN_PATTERNS
    assert "vendor" in CLEAN_PATTERNS
    assert "coverage.out" in CLEAN_PATTERNS
    assert "*.test" in CLEAN_PATTERNS


def test_go_tool_clean_empty_dir(tmp_path):
    tool = GoTool(tmp_path)
    result = tool.clean()
    assert result == 0


def test_go_tool_clean_removes_dirs(tmp_path):
    (tmp_path / "bin").mkdir()
    (tmp_path / "dist").mkdir()
    (tmp_path / "vendor").mkdir()
    tool = GoTool(tmp_path)
    result = tool.clean()
    assert result == 0
    assert not (tmp_path / "bin").exists()
    assert not (tmp_path / "dist").exists()
    assert not (tmp_path / "vendor").exists()


def test_go_tool_clean_removes_file(tmp_path):
    (tmp_path / "coverage.out").write_text("data")
    tool = GoTool(tmp_path)
    result = tool.clean()
    assert result == 0
    assert not (tmp_path / "coverage.out").exists()


def test_go_tool_clean_removes_glob_pattern(tmp_path):
    (tmp_path / "myapp.test").write_text("binary")
    tool = GoTool(tmp_path)
    result = tool.clean()
    assert result == 0
    assert not (tmp_path / "myapp.test").exists()


def test_go_tool_create_gitignore(tmp_path):
    tool = GoTool(tmp_path)
    tool._create_gitignore()
    gitignore = tmp_path / ".gitignore"
    assert gitignore.exists()
    content = gitignore.read_text()
    assert "bin/" in content
    assert "vendor/" in content
    assert "coverage.out" in content
    assert "*.exe" in content
    assert ".DS_Store" in content


def test_go_tool_create_gitignore_skips_existing(tmp_path):
    (tmp_path / ".gitignore").write_text("existing")
    tool = GoTool(tmp_path)
    tool._create_gitignore()
    assert (tmp_path / ".gitignore").read_text() == "existing"


def test_go_tool_create_main_go(tmp_path):
    tool = GoTool(tmp_path)
    tool._create_main_go()
    main_go = tmp_path / "main.go"
    assert main_go.exists()
    content = main_go.read_text()
    assert "package main" in content
    assert 'fmt.Println("Hello, World!")' in content


def test_go_tool_create_main_go_skips_existing(tmp_path):
    (tmp_path / "main.go").write_text("existing")
    tool = GoTool(tmp_path)
    tool._create_main_go()
    assert (tmp_path / "main.go").read_text() == "existing"


def test_build_runs_tests_first(tmp_path, mocker):
    tool = GoTool(tmp_path)
    mock_test = mocker.patch.object(tool, "test", return_value=0)
    mocker.patch("pkg.tools.go.run_command", return_value=0)
    tool.build()
    mock_test.assert_called_once()


def test_build_aborts_on_test_failure(tmp_path, mocker):
    tool = GoTool(tmp_path)
    mocker.patch.object(tool, "test", return_value=1)
    mock_run = mocker.patch("pkg.tools.go.run_command")
    result = tool.build()
    assert result == 1
    mock_run.assert_not_called()


def test_go_tool_test(tmp_path, mocker):
    tool = GoTool(tmp_path)
    mock_run = mocker.patch("pkg.tools.go.run_command", return_value=0)
    result = tool.test()
    assert result == 0
    mock_run.assert_called_once_with(["go", "test", "-cover", "./..."], cwd=tmp_path)


def test_go_tool_install(tmp_path, mocker):
    tool = GoTool(tmp_path)
    mock_run = mocker.patch("pkg.tools.go.run_command", return_value=0)
    result = tool.install()
    assert result == 0
    mock_run.assert_called_once_with(["go", "mod", "tidy"], cwd=tmp_path)


def test_go_tool_run_script(tmp_path, mocker):
    tool = GoTool(tmp_path)
    mock_run = mocker.patch("pkg.tools.go.run_command", return_value=0)
    result = tool.run("main.go")
    assert result == 0
    mock_run.assert_called_once_with(["go", "run", "main.go"], cwd=tmp_path)


def test_go_tool_run_script_with_args(tmp_path, mocker):
    tool = GoTool(tmp_path)
    mock_run = mocker.patch("pkg.tools.go.run_command", return_value=0)
    result = tool.run("main.go", ["--flag", "value"])
    assert result == 0
    mock_run.assert_called_once_with(["go", "run", "main.go", "--flag", "value"], cwd=tmp_path)


def test_go_tool_init(tmp_path, mocker):
    tool = GoTool(tmp_path)
    mock_run = mocker.patch("pkg.tools.go.run_command", return_value=0)
    result = tool.init(name="myproject")
    assert result == 0
    mock_run.assert_called_once_with(["go", "mod", "init", "myproject"], cwd=tmp_path)
    assert (tmp_path / "main.go").exists()
    assert (tmp_path / ".gitignore").exists()


def test_go_tool_init_uses_dir_name_when_no_name(tmp_path, mocker):
    tool = GoTool(tmp_path)
    mock_run = mocker.patch("pkg.tools.go.run_command", return_value=0)
    tool.init()
    mock_run.assert_called_once_with(["go", "mod", "init", tmp_path.name], cwd=tmp_path)


def test_go_tool_init_fails(tmp_path, mocker):
    tool = GoTool(tmp_path)
    mocker.patch("pkg.tools.go.run_command", return_value=1)
    result = tool.init()
    assert result == 1


def test_go_tool_uplift(tmp_path):
    tool = GoTool(tmp_path)
    result = tool.uplift()
    assert result == 0
    assert (tmp_path / ".gitignore").exists()


def test_go_tool_uplift_idempotent(tmp_path):
    (tmp_path / ".gitignore").write_text("existing")
    tool = GoTool(tmp_path)
    tool.uplift()
    tool.uplift()
    assert (tmp_path / ".gitignore").read_text() == "existing"
