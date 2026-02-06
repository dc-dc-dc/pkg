import pytest
from pathlib import Path
from pkg.hooks import run_hooks, run_pre_hooks, run_post_hooks
from pkg.config import HookConfig


def test_run_hooks_empty_returns_true(tmp_path):
    assert run_hooks([], "pre", "build", tmp_path) is True


def test_run_hooks_success(tmp_path):
    result = run_hooks(["true"], "pre", "build", tmp_path)
    assert result is True


def test_run_hooks_failure(tmp_path):
    result = run_hooks(["false"], "pre", "build", tmp_path)
    assert result is False


def test_run_hooks_sets_env(tmp_path, monkeypatch):
    script = tmp_path / "check_env.sh"
    script.write_text('#!/bin/sh\ntest "$PKG_COMMAND" = "build" && test "$PKG_PHASE" = "pre"')
    script.chmod(0o755)
    result = run_hooks([str(script)], "pre", "build", tmp_path)
    assert result is True


def test_run_pre_hooks(tmp_path):
    hc = HookConfig(pre=["true"], post=["false"])
    assert run_pre_hooks(hc, "build", tmp_path) is True


def test_run_post_hooks(tmp_path):
    hc = HookConfig(pre=["false"], post=["true"])
    assert run_post_hooks(hc, "build", tmp_path) is True
