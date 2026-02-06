from pathlib import Path

from . import register


class AgentMdHook:
    name = "agent-md"
    enabled_by_default = True

    def run(self, project_dir: Path, name: str) -> int:
        """Create an AGENTS.md file in the project directory."""
        agent_md_path = project_dir / "AGENTS.md"

        if agent_md_path.exists():
            return 0

        content = f"""# {name}

## Overview

<!-- Describe what this project does -->

## Development

### Setup

```bash
pkg install
```

### Build

```bash
pkg build
```

### Test

```bash
pkg test
```
"""
        agent_md_path.write_text(content)
        return 0


register(AgentMdHook())
