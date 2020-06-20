from abc import ABC
import os
from pathlib import Path
from typing import Generator, List, Optional, Union


class _FsQueryAbc(ABC):
    def __init__(
        self,
        root: Union[str, Path],
        dirs: bool = True,
        files: bool = True,
        patterns: Optional[List[str]] = None,
    ):
        self._root = Path(root).resolve()
        assert self._root.is_dir(), "Root path must be a directory"
        self._patterns = patterns if patterns else []
        self._dirs = dirs
        self._files = files

    def _check(self, path: Path) -> bool:
        if not self._dirs and path.is_dir():
            return False
        if not self._files and path.is_file():
            return False
        if self._patterns:
            return any(path.match(g) for g in self._patterns)
        return True


class FsQuery(_FsQueryAbc):
    def __iter__(self) -> Generator[Path, None, None]:
        for path in self._root.iterdir():
            if self._check(path):
                yield path


class FsQueryRecursive(_FsQueryAbc):
    def __iter__(self) -> Generator[Path, None, None]:
        for root, dirs, files in os.walk(self._root.as_posix()):
            if self._files:
                for path in (Path(root) / f for f in files):
                    if self._check(path):
                        yield path
            if self._dirs:
                for path in (Path(root) / d for d in dirs):
                    if self._check(path):
                        yield path
