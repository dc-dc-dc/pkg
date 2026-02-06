from abc import ABC, abstractmethod
from pathlib import Path


class BuildTool(ABC):
    def __init__(self, project_dir: Path):
        self.project_dir = project_dir

    @property
    @abstractmethod
    def name(self) -> str:
        ...

    @abstractmethod
    def init(self, git: bool = True) -> int:
        ...

    @abstractmethod
    def build(self) -> int:
        ...

    @abstractmethod
    def test(self) -> int:
        ...

    @abstractmethod
    def install(self) -> int:
        ...

    @abstractmethod
    def run(self, script: str, args: list[str] | None = None) -> int:
        ...

    @abstractmethod
    def clean(self) -> int:
        ...

    @abstractmethod
    def uplift(self) -> int:
        ...
