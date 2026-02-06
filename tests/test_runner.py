import pytest
from pkg.runner import run_command


def test_run_command_success(tmp_path):
    result = run_command(["true"], tmp_path)
    assert result == 0


def test_run_command_failure(tmp_path):
    result = run_command(["false"], tmp_path)
    assert result == 1


def test_run_command_with_args(tmp_path):
    result = run_command(["echo", "hello"], tmp_path)
    assert result == 0
