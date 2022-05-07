import os

__all__ = ("Version",)


class Version:
    __slots__ = (
        "git_commit",
        "git_commit_short",
        "git_branch",
        "git_dirty_files",
    )

    # TODO: maybe fallback to getting git info ourselves if inside git repo:
    # GIT_COMMIT=$(git rev-parse HEAD)
    # GIT_BRANCH=$(git rev-parse --abbrev-ref HEAD)
    # GIT_DIRTY=$(git status --porcelain=v1 2>/dev/null | wc -l)
    def __init__(self) -> None:
        self.git_commit = os.environ.get("GIT_COMMIT")
        self.git_branch = os.environ.get("GIT_BRANCH")
        self.git_dirty_files = int(os.environ.get("GIT_DIRTY", "0"))

        if self.git_commit is None:
            self.git_commit_short = None
        else:
            self.git_commit_short = self.git_commit[:10]

    @property
    def is_dirty(self) -> bool:
        return self.git_dirty_files > 0

    def short(self) -> str:
        if self.git_commit is None:
            return "unversioned"

        result: str = self.git_commit_short  # type: ignore[assignment]
        if self.git_branch is not None:
            result = f"{self.git_branch}/{result}"

        if self.is_dirty:
            result = f"DIRTY[{self.git_dirty_files}] {result}"

        return result

    def full(self) -> str:
        if self.git_commit is None:
            return "unversioned"

        result = self.git_commit
        if self.git_branch is not None:
            result = f"{self.git_branch}/{result}"

        if self.is_dirty:
            result = f"DIRTY[{self.git_dirty_files}] {result}"

        return result

    def __str__(self) -> str:
        return self.short()
