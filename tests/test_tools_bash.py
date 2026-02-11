import stat
from pathlib import Path
from unittest.mock import patch

from pkg.tools.bash import BashTool, BIN_DIR


def test_bash_tool_name(tmp_path):
    tool = BashTool(tmp_path)
    assert tool.name == "bash"


def test_bash_tool_project_dir(tmp_path):
    tool = BashTool(tmp_path)
    assert tool.project_dir == tmp_path


def test_bash_tool_init_creates_structure(tmp_path):
    tool = BashTool(tmp_path)
    result = tool.init()
    assert result == 0
    assert (tmp_path / "src").is_dir()
    assert (tmp_path / "tests").is_dir()
    assert (tmp_path / "src" / "hello.sh").exists()
    assert (tmp_path / "tests" / "hello_test.sh").exists()
    assert (tmp_path / ".gitignore").exists()


def test_bash_tool_init_hello_script_content(tmp_path):
    tool = BashTool(tmp_path)
    tool.init()
    content = (tmp_path / "src" / "hello.sh").read_text()
    assert "echo 'Hello, World!'" in content
    assert "set -euo pipefail" in content


def test_bash_tool_init_hello_script_executable(tmp_path):
    tool = BashTool(tmp_path)
    tool.init()
    mode = (tmp_path / "src" / "hello.sh").stat().st_mode
    assert mode & stat.S_IEXEC


def test_bash_tool_init_test_script_content(tmp_path):
    tool = BashTool(tmp_path)
    tool.init()
    content = (tmp_path / "tests" / "hello_test.sh").read_text()
    assert "PASS" in content
    assert "FAIL" in content


def test_bash_tool_init_test_script_executable(tmp_path):
    tool = BashTool(tmp_path)
    tool.init()
    mode = (tmp_path / "tests" / "hello_test.sh").stat().st_mode
    assert mode & stat.S_IEXEC


def test_bash_tool_test_passes(tmp_path):
    tool = BashTool(tmp_path)
    tool.init()
    result = tool.test()
    assert result == 0


def test_bash_tool_test_no_tests_dir(tmp_path):
    tool = BashTool(tmp_path)
    result = tool.test()
    assert result == 0


def test_bash_tool_test_no_test_files(tmp_path):
    (tmp_path / "tests").mkdir()
    tool = BashTool(tmp_path)
    result = tool.test()
    assert result == 0


def test_bash_tool_test_failing_test(tmp_path):
    tool = BashTool(tmp_path)
    test_dir = tmp_path / "tests"
    test_dir.mkdir()
    failing = test_dir / "bad_test.sh"
    failing.write_text("#!/usr/bin/env bash\nexit 1\n")
    failing.chmod(failing.stat().st_mode | stat.S_IEXEC)
    result = tool.test()
    assert result == 1


def test_bash_tool_test_mixed_pass_fail(tmp_path):
    tool = BashTool(tmp_path)
    test_dir = tmp_path / "tests"
    test_dir.mkdir()

    passing = test_dir / "a_test.sh"
    passing.write_text("#!/usr/bin/env bash\nexit 0\n")
    passing.chmod(passing.stat().st_mode | stat.S_IEXEC)

    failing = test_dir / "b_test.sh"
    failing.write_text("#!/usr/bin/env bash\nexit 1\n")
    failing.chmod(failing.stat().st_mode | stat.S_IEXEC)

    result = tool.test()
    assert result == 1


def test_bash_tool_build_copies_to_bin(tmp_path, mocker):
    tool = BashTool(tmp_path)
    tool.init()

    fake_bin = tmp_path / "fake_bin"
    fake_bin.mkdir()
    mocker.patch("pkg.tools.bash.BIN_DIR", fake_bin)

    result = tool.build()
    assert result == 0
    assert (fake_bin / "hello.sh").exists()
    mode = (fake_bin / "hello.sh").stat().st_mode
    assert mode & stat.S_IEXEC


def test_bash_tool_build_aborts_on_test_failure(tmp_path, mocker):
    tool = BashTool(tmp_path)
    mocker.patch.object(tool, "test", return_value=1)
    result = tool.build()
    assert result == 1


def test_bash_tool_build_no_src_dir(tmp_path, mocker):
    tool = BashTool(tmp_path)
    mocker.patch.object(tool, "test", return_value=0)
    result = tool.build()
    assert result == 1


def test_bash_tool_build_no_scripts(tmp_path, mocker):
    tool = BashTool(tmp_path)
    (tmp_path / "src").mkdir()
    mocker.patch.object(tool, "test", return_value=0)
    result = tool.build()
    assert result == 0


def test_bash_tool_clean_removes_installed(tmp_path, mocker):
    tool = BashTool(tmp_path)
    src_dir = tmp_path / "src"
    src_dir.mkdir()
    (src_dir / "myscript.sh").write_text("#!/bin/bash\necho hi\n")

    fake_bin = tmp_path / "fake_bin"
    fake_bin.mkdir()
    (fake_bin / "myscript.sh").write_text("#!/bin/bash\necho hi\n")
    mocker.patch("pkg.tools.bash.BIN_DIR", fake_bin)

    result = tool.clean()
    assert result == 0
    assert not (fake_bin / "myscript.sh").exists()


def test_bash_tool_clean_nothing_to_clean(tmp_path, mocker):
    tool = BashTool(tmp_path)
    src_dir = tmp_path / "src"
    src_dir.mkdir()
    (src_dir / "myscript.sh").write_text("#!/bin/bash\necho hi\n")

    fake_bin = tmp_path / "fake_bin"
    fake_bin.mkdir()
    mocker.patch("pkg.tools.bash.BIN_DIR", fake_bin)

    result = tool.clean()
    assert result == 0


def test_bash_tool_clean_no_src_dir(tmp_path):
    tool = BashTool(tmp_path)
    result = tool.clean()
    assert result == 0


def test_bash_tool_run_script(tmp_path, mocker):
    tool = BashTool(tmp_path)
    src_dir = tmp_path / "src"
    src_dir.mkdir()
    script = src_dir / "myscript.sh"
    script.write_text("#!/bin/bash\necho hi\n")

    mock_run = mocker.patch("pkg.tools.bash.run_command", return_value=0)
    result = tool.run("myscript.sh")
    assert result == 0
    mock_run.assert_called_once_with(
        ["bash", str(script)], cwd=tmp_path
    )


def test_bash_tool_run_script_with_args(tmp_path, mocker):
    tool = BashTool(tmp_path)
    src_dir = tmp_path / "src"
    src_dir.mkdir()
    script = src_dir / "myscript.sh"
    script.write_text("#!/bin/bash\necho $1\n")

    mock_run = mocker.patch("pkg.tools.bash.run_command", return_value=0)
    result = tool.run("myscript.sh", ["arg1", "arg2"])
    assert result == 0
    mock_run.assert_called_once_with(
        ["bash", str(script), "arg1", "arg2"], cwd=tmp_path
    )


def test_bash_tool_run_script_not_found(tmp_path):
    tool = BashTool(tmp_path)
    (tmp_path / "src").mkdir()
    result = tool.run("missing.sh")
    assert result == 1


def test_bash_tool_install(tmp_path):
    tool = BashTool(tmp_path)
    result = tool.install()
    assert result == 0


def test_bash_tool_create_gitignore(tmp_path):
    tool = BashTool(tmp_path)
    tool._create_gitignore()
    gitignore = tmp_path / ".gitignore"
    assert gitignore.exists()
    content = gitignore.read_text()
    assert ".DS_Store" in content
    assert "*.log" in content


def test_bash_tool_create_gitignore_skips_existing(tmp_path):
    (tmp_path / ".gitignore").write_text("existing")
    tool = BashTool(tmp_path)
    tool._create_gitignore()
    assert (tmp_path / ".gitignore").read_text() == "existing"


def test_bash_tool_uplift(tmp_path):
    tool = BashTool(tmp_path)
    result = tool.uplift()
    assert result == 0
    assert (tmp_path / "src").is_dir()
    assert (tmp_path / "tests").is_dir()
    assert (tmp_path / ".gitignore").exists()


def test_bash_tool_uplift_idempotent(tmp_path):
    (tmp_path / ".gitignore").write_text("existing")
    tool = BashTool(tmp_path)
    tool.uplift()
    tool.uplift()
    assert (tmp_path / ".gitignore").read_text() == "existing"
