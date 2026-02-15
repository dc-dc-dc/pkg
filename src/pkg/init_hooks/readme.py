from pathlib import Path

from . import register


class ReadmeHook:
    name = "readme"
    enabled_by_default = True

    def run(self, project_dir: Path, name: str) -> int:
        """Create a README.md file in the project directory."""
        readme_path = project_dir / "README.md"

        if readme_path.exists():
            return 0

        content = f"""# {name}

## Getting Started

### Install

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
        readme_path.write_text(content)
        return 0


register(ReadmeHook())
