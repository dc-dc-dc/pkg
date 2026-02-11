# pkg

Unified CLI tool that wraps language-specific build tools with hooks and plugins.

## Installation

```bash
pip install pkg
```

## Quick Start

```bash
# Initialize a new project
pkg init my-project --tool uv

# Install dependencies
pkg install

# Build the project
pkg build

# Run tests
pkg test

# Run a script
pkg run <script> [args...]

# Clean build artifacts
pkg clean
```

## Configuration

Create a `pkg.toml` in your project root:

```toml
[pkg]
tool = "uv"

[hooks.build]
pre = ["echo 'Starting build...'"]
post = ["echo 'Build complete!'"]

[hooks.test]
pre = []
post = []

[hooks.install]
pre = []
post = []

[plugins]
enabled = []
```

## Supported Tools

- `bash` - Bash script projects (scripts in `src/`, tests in `tests/`, installs to `~/bin`)
- `bun` - Fast JavaScript/TypeScript runtime and bundler
- `uv` - Fast Python package installer and resolver

## Hooks

Hooks run before (`pre`) and after (`post`) commands. Configure them per-command in `pkg.toml`:

```toml
[hooks.build]
pre = ["lint", "typecheck"]
post = ["notify"]
```

## Init Hooks

When running `pkg init`, these hooks run automatically:

- `git` - Initializes a git repository
- `agent-md` - Creates an AGENT.md file

Disable git initialization with `--no-git`:

```bash
pkg init my-project --tool uv --no-git
```

## Plugins

Plugins extend pkg functionality. Enable them in `pkg.toml`:

```toml
[plugins]
enabled = ["my-plugin"]
```

Create plugins by implementing the plugin interface and registering via entry points:

```toml
# In your plugin's pyproject.toml
[project.entry-points."pkg.plugins"]
my_plugin = "my_plugin:Plugin"
```

## Adding New Tools

Implement the `BuildTool` abstract class:

```python
from pkg.tools.base import BuildTool

class MyTool(BuildTool):
    name = "mytool"

    def init(self, name: str) -> int: ...
    def build(self) -> int: ...
    def test(self) -> int: ...
    def install(self) -> int: ...
    def run(self, script: str, args: list[str] | None = None) -> int: ...
    def clean(self) -> int: ...
```

Register it in `src/pkg/tools/__init__.py`.
