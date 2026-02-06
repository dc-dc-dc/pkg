import pytest
from pkg.init_hooks import register, run_init_hooks, _hooks
from pkg.init_hooks.git import GitHook
from pkg.init_hooks.agent_md import AgentMdHook


def test_git_hook_creates_repo(tmp_path):
    hook = GitHook()
    assert hook.name == "git"
    assert hook.enabled_by_default is True
    result = hook.run(tmp_path, "test")
    assert result == 0
    assert (tmp_path / ".git").exists()


def test_git_hook_skips_existing(tmp_path):
    (tmp_path / ".git").mkdir()
    hook = GitHook()
    result = hook.run(tmp_path, "test")
    assert result == 0


def test_agent_md_hook_creates_file(tmp_path):
    hook = AgentMdHook()
    assert hook.name == "agent-md"
    assert hook.enabled_by_default is True
    result = hook.run(tmp_path, "myproject")
    assert result == 0
    content = (tmp_path / "AGENTS.md").read_text()
    assert "# myproject" in content


def test_agent_md_hook_skips_existing(tmp_path):
    (tmp_path / "AGENTS.md").write_text("existing")
    hook = AgentMdHook()
    result = hook.run(tmp_path, "test")
    assert result == 0
    assert (tmp_path / "AGENTS.md").read_text() == "existing"


def test_run_init_hooks_with_disabled(tmp_path):
    result = run_init_hooks(tmp_path, "test", disabled={"git", "agent-md"})
    assert result == 0
    assert not (tmp_path / ".git").exists()


def test_run_init_hooks_runs_enabled(tmp_path):
    result = run_init_hooks(tmp_path, "test", disabled=set())
    assert result == 0


class FailingHook:
    name = "failing"
    enabled_by_default = True

    def run(self, project_dir, name):
        return 1


def test_run_init_hooks_stops_on_failure(tmp_path, mocker):
    from pkg import init_hooks
    original_hooks = init_hooks._hooks.copy()
    try:
        init_hooks._hooks.clear()
        init_hooks._hooks.append(FailingHook())
        result = run_init_hooks(tmp_path, "test")
        assert result == 1
    finally:
        init_hooks._hooks.clear()
        init_hooks._hooks.extend(original_hooks)
