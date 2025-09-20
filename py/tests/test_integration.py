"""Integration tests for git_identify module."""

import os
import sys
import tempfile
from pathlib import Path
import pytest

# Add parent directory to path for testing
sys.path.insert(0, str(Path(__file__).parent.parent))

from git_identify import (
    GitFileId,
    generate_github_url_direct,
    find_git_root,
    parse_remote_url,
    build_github_url,
    GitHubInfo,
)
from git_identify.repository import (
    get_remote_url,
    list_refs,
    get_file_status,
    get_head_ref,
)
from git_identify.url_builder import normalize_file_path


class TestGitFileId:
    """Test GitFileId class functionality."""

    def test_initialization(self):
        """Test GitFileId initialization."""
        git_id = GitFileId()
        assert git_id.repo_path is None
        assert git_id.repo is None

    def test_find_repository(self):
        """Test repository discovery."""
        git_id = GitFileId()
        current_dir = Path.cwd()

        try:
            git_id.find_repository(str(current_dir))
            assert git_id.repo_path is not None
            assert (git_id.repo_path / ".git").exists()
        except ValueError:
            # Skip if not in a git repository
            pytest.skip("Not in a git repository")

    def test_generate_github_url(self):
        """Test GitHub URL generation."""
        git_id = GitFileId()
        current_dir = Path.cwd()

        try:
            git_id.find_repository(str(current_dir))

            # Find a file that exists
            test_file = None
            for file in ["setup.py", "README.md", "pyproject.toml"]:
                if (current_dir / file).exists():
                    test_file = file
                    break

            if test_file:
                url = git_id.generate_github_url(test_file)
                assert url.startswith("https://github.com/")
                assert "/blob/" in url
        except ValueError as e:
            # Skip if no origin remote or not in a git repository
            if "No origin remote" in str(e) or "No .git directory" in str(e):
                pytest.skip(f"Test environment issue: {e}")
            else:
                raise

    def test_list_refs(self):
        """Test listing repository references."""
        git_id = GitFileId()
        current_dir = Path.cwd()

        try:
            git_id.find_repository(str(current_dir))
            refs = git_id.list_refs()
            assert isinstance(refs, list)
            # Should have at least HEAD
            assert len(refs) > 0
        except ValueError:
            pytest.skip("Not in a git repository")

    def test_get_head_ref(self):
        """Test getting HEAD reference."""
        git_id = GitFileId()
        current_dir = Path.cwd()

        try:
            git_id.find_repository(str(current_dir))
            head = git_id.get_head_ref()
            assert isinstance(head, str)
            assert len(head) > 0
        except ValueError:
            pytest.skip("Not in a git repository")

    def test_get_file_status(self):
        """Test getting file status."""
        git_id = GitFileId()
        current_dir = Path.cwd()

        try:
            git_id.find_repository(str(current_dir))

            # Find a file that exists
            test_file = None
            for file in ["setup.py", "README.md", "pyproject.toml"]:
                if (current_dir / file).exists():
                    test_file = file
                    break

            if test_file:
                status = git_id.get_file_status(test_file)
                assert status in ["clean", "modified", "untracked", "added", "staged", "deleted", "unknown"]
        except ValueError:
            pytest.skip("Not in a git repository")


class TestRepositoryFunctions:
    """Test repository module functions."""

    def test_find_git_root(self):
        """Test finding Git repository root."""
        current_dir = Path.cwd()

        try:
            git_root = find_git_root(str(current_dir))
            assert isinstance(git_root, Path)
            assert (git_root / ".git").exists()
        except ValueError:
            pytest.skip("Not in a git repository")

    def test_find_git_root_from_file(self):
        """Test finding Git root from a file path."""
        current_dir = Path.cwd()

        # Find a file that exists
        test_file = None
        for file in ["setup.py", "README.md", "pyproject.toml"]:
            if (current_dir / file).exists():
                test_file = current_dir / file
                break

        if test_file:
            try:
                git_root = find_git_root(str(test_file))
                assert isinstance(git_root, Path)
                assert (git_root / ".git").exists()
            except ValueError:
                pytest.skip("Not in a git repository")

    def test_find_git_root_no_repo(self):
        """Test finding Git root when no repository exists."""
        with tempfile.TemporaryDirectory() as tmpdir:
            with pytest.raises(ValueError, match="No .git directory found"):
                find_git_root(tmpdir)


class TestURLBuilder:
    """Test URL builder functions."""

    def test_parse_ssh_url(self):
        """Test parsing SSH format URLs."""
        url = "git@github.com:owner/repo.git"
        info = parse_remote_url(url)
        assert info.owner == "owner"
        assert info.repo == "repo"

    def test_parse_ssh_url_no_extension(self):
        """Test parsing SSH URL without .git extension."""
        url = "git@github.com:myuser/myrepo"
        info = parse_remote_url(url)
        assert info.owner == "myuser"
        assert info.repo == "myrepo"

    def test_parse_https_url(self):
        """Test parsing HTTPS format URLs."""
        url = "https://github.com/owner/repo.git"
        info = parse_remote_url(url)
        assert info.owner == "owner"
        assert info.repo == "repo"

    def test_parse_http_url(self):
        """Test parsing HTTP format URLs."""
        url = "http://github.com/testuser/testrepo.git"
        info = parse_remote_url(url)
        assert info.owner == "testuser"
        assert info.repo == "testrepo"

    def test_parse_invalid_url(self):
        """Test parsing invalid URLs."""
        with pytest.raises(ValueError, match="Unsupported remote URL format"):
            parse_remote_url("not-a-github-url")

    def test_build_github_url(self):
        """Test building GitHub URLs."""
        info = GitHubInfo(owner="taskforcesh", repo="bullmq")
        url = build_github_url(info, "abc123def456", "src/main.py")
        assert url == "https://github.com/taskforcesh/bullmq/blob/abc123def456/src/main.py"

    def test_normalize_file_path(self):
        """Test file path normalization."""
        # Absolute path
        assert normalize_file_path("/src/main.py") == "src/main.py"

        # Relative path
        assert normalize_file_path("src/lib.py") == "src/lib.py"

        # Windows-style path
        assert normalize_file_path("src\\windows\\file.py") == "src/windows/file.py"

        # Multiple leading slashes
        assert normalize_file_path("//src/main.py") == "src/main.py"


class TestStandaloneFunctions:
    """Test standalone functions."""

    def test_generate_github_url_direct(self):
        """Test direct GitHub URL generation."""
        current_dir = Path.cwd()

        # Find a file that exists
        test_file = None
        for file in ["setup.py", "README.md", "pyproject.toml"]:
            if (current_dir / file).exists():
                test_file = current_dir / file
                break

        if test_file:
            try:
                url = generate_github_url_direct(str(test_file))
                assert url.startswith("https://github.com/")
                assert "/blob/" in url
            except ValueError as e:
                # Skip if no origin remote or not in a git repository
                if "No origin remote" in str(e) or "No .git directory" in str(e):
                    pytest.skip(f"Test environment issue: {e}")
                else:
                    raise


if __name__ == "__main__":
    pytest.main([__file__, "-v"])