"""Git object representations for Git Identify."""

from dataclasses import dataclass
from typing import List, Any, Optional
from datetime import datetime

try:
    import pygit2
    USE_PYGIT2 = True
except ImportError:
    USE_PYGIT2 = False

import git  # GitPython as fallback


@dataclass
class GitBlob:
    """Represents a Git blob object."""

    id: str
    size: int
    is_binary: bool


@dataclass
class GitTree:
    """Represents a Git tree object."""

    id: str
    len: int


@dataclass
class GitCommit:
    """Represents a Git commit object."""

    id: str
    message: str
    author_name: str
    author_email: str
    time: int  # Unix timestamp
    tree_id: str
    parent_ids: List[str]


@dataclass
class GitTag:
    """Represents a Git tag object."""

    id: str
    name: str
    message: str
    target_id: str


def get_blob(repo: Any, hash: str) -> GitBlob:
    """
    Get a Git blob object by hash.

    Args:
        repo: Repository object (pygit2.Repository or git.Repo)
        hash: SHA-1 hash of the blob

    Returns:
        GitBlob object

    Raises:
        ValueError: If blob not found
    """
    try:
        if USE_PYGIT2 and isinstance(repo, pygit2.Repository):
            oid = pygit2.Oid(hex=hash)
            blob = repo[oid]

            if not isinstance(blob, pygit2.Blob):
                raise ValueError(f"Object {hash} is not a blob")

            return GitBlob(
                id=str(blob.id),
                size=blob.size,
                is_binary=blob.is_binary,
            )
        else:
            blob = repo.odb.stream(hash)
            data = blob.read()

            # Simple binary detection
            is_binary = b"\x00" in data[:8192]

            return GitBlob(
                id=hash,
                size=len(data),
                is_binary=is_binary,
            )
    except Exception as e:
        raise ValueError(f"Failed to get blob {hash}: {e}")


def get_tree(repo: Any, hash: str) -> GitTree:
    """
    Get a Git tree object by hash.

    Args:
        repo: Repository object (pygit2.Repository or git.Repo)
        hash: SHA-1 hash of the tree

    Returns:
        GitTree object

    Raises:
        ValueError: If tree not found
    """
    try:
        if USE_PYGIT2 and isinstance(repo, pygit2.Repository):
            oid = pygit2.Oid(hex=hash)
            tree = repo[oid]

            if not isinstance(tree, pygit2.Tree):
                raise ValueError(f"Object {hash} is not a tree")

            return GitTree(
                id=str(tree.id),
                len=len(tree),
            )
        else:
            tree = repo.tree(hash)
            return GitTree(
                id=hash,
                len=len(list(tree.traverse())),
            )
    except Exception as e:
        raise ValueError(f"Failed to get tree {hash}: {e}")


def get_commit(repo: Any, hash: str) -> GitCommit:
    """
    Get a Git commit object by hash.

    Args:
        repo: Repository object (pygit2.Repository or git.Repo)
        hash: SHA-1 hash of the commit

    Returns:
        GitCommit object

    Raises:
        ValueError: If commit not found
    """
    try:
        if USE_PYGIT2 and isinstance(repo, pygit2.Repository):
            oid = pygit2.Oid(hex=hash)
            commit = repo[oid]

            if not isinstance(commit, pygit2.Commit):
                raise ValueError(f"Object {hash} is not a commit")

            parent_ids = [str(p) for p in commit.parent_ids]

            return GitCommit(
                id=str(commit.id),
                message=commit.message or "",
                author_name=commit.author.name or "",
                author_email=commit.author.email or "",
                time=commit.author.time,
                tree_id=str(commit.tree_id),
                parent_ids=parent_ids,
            )
        else:
            commit = repo.commit(hash)
            parent_ids = [p.hexsha for p in commit.parents]

            return GitCommit(
                id=commit.hexsha,
                message=commit.message or "",
                author_name=commit.author.name or "",
                author_email=commit.author.email or "",
                time=int(commit.authored_date),
                tree_id=commit.tree.hexsha,
                parent_ids=parent_ids,
            )
    except Exception as e:
        raise ValueError(f"Failed to get commit {hash}: {e}")


def get_tag(repo: Any, hash: str) -> GitTag:
    """
    Get a Git tag object by hash.

    Args:
        repo: Repository object (pygit2.Repository or git.Repo)
        hash: SHA-1 hash of the tag

    Returns:
        GitTag object

    Raises:
        ValueError: If tag not found
    """
    try:
        if USE_PYGIT2 and isinstance(repo, pygit2.Repository):
            oid = pygit2.Oid(hex=hash)
            tag = repo[oid]

            if not isinstance(tag, pygit2.Tag):
                raise ValueError(f"Object {hash} is not a tag")

            return GitTag(
                id=str(tag.id),
                name=tag.name or "",
                message=tag.message or "",
                target_id=str(tag.target),
            )
        else:
            # GitPython - find tag by hash
            for tag_ref in repo.tags:
                if tag_ref.tag and tag_ref.tag.hexsha == hash:
                    tag = tag_ref.tag
                    return GitTag(
                        id=tag.hexsha,
                        name=tag_ref.name,
                        message=tag.message or "",
                        target_id=tag.object.hexsha,
                    )

            raise ValueError(f"Tag with hash {hash} not found")
    except Exception as e:
        raise ValueError(f"Failed to get tag {hash}: {e}")