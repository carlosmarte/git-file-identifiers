"""Unit tests for repository module."""

import pytest
from pathlib import Path
import tempfile
import os
import sys
from unittest.mock import Mock, MagicMock, patch, PropertyMock

sys.path.insert(0, str(Path(__file__).parent.parent))

from git_identify.repository import (
    find_git_root,
    get_file_hash_at_commit,
    get_current_branch_commit_for_file,
    get_remote_url,
    list_refs,
    get_file_status,
    get_head_ref,
)


class TestFindGitRoot:
    """Test find_git_root function."""

    def test_find_git_root_from_git_directory(self):
        """Test finding git root from a directory with .git."""
        with tempfile.TemporaryDirectory() as tmpdir:
            git_dir = Path(tmpdir) / ".git"
            git_dir.mkdir()

            result = find_git_root(tmpdir)
            assert result.resolve() == Path(tmpdir).resolve()

    def test_find_git_root_from_subdirectory(self):
        """Test finding git root from a subdirectory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmppath = Path(tmpdir)
            git_dir = tmppath / ".git"
            git_dir.mkdir()

            # Create subdirectory
            subdir = tmppath / "src" / "lib"
            subdir.mkdir(parents=True)

            result = find_git_root(str(subdir))
            assert result.resolve() == tmppath.resolve()

    def test_find_git_root_from_file(self):
        """Test finding git root from a file path."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmppath = Path(tmpdir)
            git_dir = tmppath / ".git"
            git_dir.mkdir()

            # Create a file
            test_file = tmppath / "test.txt"
            test_file.write_text("test")

            result = find_git_root(str(test_file))
            assert result.resolve() == tmppath.resolve()

    def test_find_git_root_no_repository(self):
        """Test finding git root when no repository exists."""
        with tempfile.TemporaryDirectory() as tmpdir:
            with pytest.raises(ValueError, match="No .git directory found"):
                find_git_root(tmpdir)

    def test_find_git_root_deeply_nested(self):
        """Test finding git root from deeply nested directory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmppath = Path(tmpdir)
            git_dir = tmppath / ".git"
            git_dir.mkdir()

            # Create deeply nested directory
            deep_dir = tmppath / "a" / "b" / "c" / "d" / "e"
            deep_dir.mkdir(parents=True)

            result = find_git_root(str(deep_dir))
            assert result.resolve() == tmppath.resolve()


class TestGetRemoteUrl:
    """Test get_remote_url function."""

    @patch('git_identify.repository.USE_PYGIT2', False)
    def test_get_remote_url_gitpython(self):
        """Test getting remote URL using GitPython."""
        mock_repo = Mock()
        mock_origin = Mock()
        mock_origin.url = "git@github.com:owner/repo.git"
        mock_repo.remotes = {"origin": mock_origin}

        result = get_remote_url(mock_repo)
        assert result == "git@github.com:owner/repo.git"

    @patch('git_identify.repository.USE_PYGIT2', False)
    def test_get_remote_url_no_origin_gitpython(self):
        """Test getting remote URL when no origin exists using GitPython."""
        mock_repo = Mock()
        mock_repo.remotes = {}

        with pytest.raises(ValueError, match="No origin remote found"):
            get_remote_url(mock_repo)

    def test_get_remote_url_error_handling(self):
        """Test error handling in get_remote_url."""
        mock_repo = Mock()
        mock_repo.remotes = Mock(side_effect=Exception("Test error"))

        with pytest.raises(ValueError, match="Failed to get remote URL"):
            get_remote_url(mock_repo)


class TestListRefs:
    """Test list_refs function."""

    @patch('git_identify.repository.USE_PYGIT2', False)
    def test_list_refs_gitpython(self):
        """Test listing refs using GitPython."""
        mock_repo = Mock()
        mock_ref1 = Mock()
        mock_ref1.path = "refs/heads/main"
        mock_ref2 = Mock()
        mock_ref2.path = "refs/heads/develop"
        mock_ref3 = Mock()
        mock_ref3.path = "refs/tags/v1.0.0"

        mock_repo.references = [mock_ref1, mock_ref2, mock_ref3]

        result = list_refs(mock_repo)
        assert len(result) == 3
        assert "refs/heads/main" in result
        assert "refs/heads/develop" in result
        assert "refs/tags/v1.0.0" in result

    @patch('git_identify.repository.USE_PYGIT2', False)
    def test_list_refs_empty(self):
        """Test listing refs when repository has no refs."""
        mock_repo = Mock()
        mock_repo.references = []

        result = list_refs(mock_repo)
        assert result == []

    def test_list_refs_error_handling(self):
        """Test error handling in list_refs."""
        mock_repo = Mock()
        mock_repo.references = Mock(side_effect=Exception("Test error"))

        with pytest.raises(ValueError, match="Failed to list refs"):
            list_refs(mock_repo)


class TestGetFileStatus:
    """Test get_file_status function."""

    @patch('git_identify.repository.USE_PYGIT2', False)
    def test_get_file_status_untracked(self):
        """Test getting status of untracked file."""
        mock_repo = Mock()
        mock_repo.untracked_files = ["newfile.txt"]
        mock_repo.index.diff = Mock(return_value=[])

        result = get_file_status(mock_repo, "newfile.txt")
        assert result == "untracked"

    @patch('git_identify.repository.USE_PYGIT2', False)
    def test_get_file_status_modified(self):
        """Test getting status of modified file."""
        mock_repo = Mock()
        mock_repo.untracked_files = []

        # Mock diff for working directory changes
        mock_diff = Mock()
        mock_diff.a_path = "modified.txt"
        mock_diff.change_type = "M"

        mock_repo.index.diff = Mock(side_effect=[
            [],  # No staged changes
            [mock_diff]  # Working directory changes
        ])

        result = get_file_status(mock_repo, "modified.txt")
        assert result == "modified"

    @patch('git_identify.repository.USE_PYGIT2', False)
    def test_get_file_status_staged(self):
        """Test getting status of staged file."""
        mock_repo = Mock()
        mock_repo.untracked_files = []

        # Mock diff for staged changes
        mock_diff = Mock()
        mock_diff.a_path = "staged.txt"
        mock_diff.change_type = "M"

        mock_repo.index.diff = Mock(side_effect=[
            [mock_diff],  # Staged changes
            []  # No working directory changes
        ])
        mock_repo.head.commit = Mock()

        result = get_file_status(mock_repo, "staged.txt")
        assert result == "staged"

    @patch('git_identify.repository.USE_PYGIT2', False)
    def test_get_file_status_added(self):
        """Test getting status of newly added file."""
        mock_repo = Mock()
        mock_repo.untracked_files = []

        # Mock diff for newly added file
        mock_diff = Mock()
        mock_diff.a_path = None
        mock_diff.b_path = "added.txt"
        mock_diff.change_type = "A"

        mock_repo.index.diff = Mock(side_effect=[
            [mock_diff],  # Staged addition
            []  # No working directory changes
        ])
        mock_repo.head.commit = Mock()

        result = get_file_status(mock_repo, "added.txt")
        assert result == "added"

    @patch('git_identify.repository.USE_PYGIT2', False)
    def test_get_file_status_deleted(self):
        """Test getting status of deleted file."""
        mock_repo = Mock()
        mock_repo.untracked_files = []

        # Mock diff for deleted file
        mock_diff = Mock()
        mock_diff.a_path = "deleted.txt"
        mock_diff.b_path = None
        mock_diff.change_type = "D"

        mock_repo.index.diff = Mock(side_effect=[
            [mock_diff],  # Staged deletion
            []  # No working directory changes
        ])
        mock_repo.head.commit = Mock()

        result = get_file_status(mock_repo, "deleted.txt")
        assert result == "deleted"

    @patch('git_identify.repository.USE_PYGIT2', False)
    def test_get_file_status_clean(self):
        """Test getting status of clean file."""
        mock_repo = Mock()
        mock_repo.untracked_files = []
        mock_repo.index.diff = Mock(return_value=[])
        mock_repo.head.commit = Mock()

        result = get_file_status(mock_repo, "clean.txt")
        assert result == "clean"


class TestGetHeadRef:
    """Test get_head_ref function."""

    @patch('git_identify.repository.USE_PYGIT2', False)
    def test_get_head_ref_on_branch(self):
        """Test getting HEAD ref when on a branch."""
        mock_repo = Mock()
        mock_repo.head.is_detached = False
        mock_repo.active_branch.name = "main"

        result = get_head_ref(mock_repo)
        assert result == "main"

    @patch('git_identify.repository.USE_PYGIT2', False)
    def test_get_head_ref_detached(self):
        """Test getting HEAD ref when in detached state."""
        mock_repo = Mock()
        mock_repo.head.is_detached = True
        mock_repo.head.commit.hexsha = "abc123def456"

        result = get_head_ref(mock_repo)
        assert result == "abc123def456"

    @patch('git_identify.repository.USE_PYGIT2', False)
    def test_get_head_ref_error_handling(self):
        """Test error handling in get_head_ref."""
        mock_repo = Mock()
        # Make accessing is_detached raise an exception
        type(mock_repo.head).is_detached = PropertyMock(side_effect=Exception("Test error"))

        with pytest.raises(ValueError, match="Failed to get HEAD ref"):
            get_head_ref(mock_repo)


class TestGetCurrentBranchCommitForFile:
    """Test get_current_branch_commit_for_file function."""

    @patch('git_identify.repository.USE_PYGIT2', False)
    def test_get_commit_for_existing_file(self):
        """Test getting commit for existing file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create test file
            test_file = Path(tmpdir) / "test.txt"
            test_file.write_text("test")

            mock_repo = Mock()
            mock_repo.working_dir = tmpdir
            mock_repo.head.commit.hexsha = "abc123"

            result = get_current_branch_commit_for_file(mock_repo, "test.txt")
            assert result == "abc123"

    @patch('git_identify.repository.USE_PYGIT2', False)
    def test_get_commit_for_nonexistent_file(self):
        """Test getting commit for non-existent file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            mock_repo = Mock()
            mock_repo.working_dir = tmpdir

            with pytest.raises(ValueError, match="File does not exist"):
                get_current_branch_commit_for_file(mock_repo, "nonexistent.txt")


class TestGetFileHashAtCommit:
    """Test get_file_hash_at_commit function."""

    @patch('git_identify.repository.USE_PYGIT2', False)
    def test_get_file_hash_at_commit_gitpython(self):
        """Test getting file hash at specific commit using GitPython."""
        mock_repo = Mock()
        mock_commit = Mock()
        mock_blob = Mock()
        mock_blob.binsha.hex.return_value = "filehashabc123"

        mock_commit.tree = {"path/to/file.txt": mock_blob}
        mock_repo.commit.return_value = mock_commit

        result = get_file_hash_at_commit(mock_repo, "path/to/file.txt", "commitabc123")
        assert result == "filehashabc123"

    def test_get_file_hash_at_commit_error(self):
        """Test error handling when getting file hash at commit."""
        mock_repo = Mock()
        mock_repo.commit.side_effect = Exception("Invalid commit")

        with pytest.raises(ValueError, match="Failed to get file hash at commit"):
            get_file_hash_at_commit(mock_repo, "file.txt", "invalid")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])