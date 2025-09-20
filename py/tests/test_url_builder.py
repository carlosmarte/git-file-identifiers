"""Unit tests for url_builder module."""

import pytest
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))

from git_identify.url_builder import (
    parse_remote_url,
    build_github_url,
    normalize_file_path,
    generate_github_url,
    GitHubInfo,
)


class TestParseRemoteUrl:
    """Test parse_remote_url function."""

    def test_parse_ssh_url_with_git_extension(self):
        """Test parsing SSH URL with .git extension."""
        url = "git@github.com:owner/repo.git"
        result = parse_remote_url(url)
        assert isinstance(result, GitHubInfo)
        assert result.owner == "owner"
        assert result.repo == "repo"

    def test_parse_ssh_url_without_git_extension(self):
        """Test parsing SSH URL without .git extension."""
        url = "git@github.com:myuser/myrepo"
        result = parse_remote_url(url)
        assert result.owner == "myuser"
        assert result.repo == "myrepo"

    def test_parse_ssh_url_with_hyphen(self):
        """Test parsing SSH URL with hyphens in names."""
        url = "git@github.com:my-org/my-repo.git"
        result = parse_remote_url(url)
        assert result.owner == "my-org"
        assert result.repo == "my-repo"

    def test_parse_https_url_with_git_extension(self):
        """Test parsing HTTPS URL with .git extension."""
        url = "https://github.com/owner/repo.git"
        result = parse_remote_url(url)
        assert result.owner == "owner"
        assert result.repo == "repo"

    def test_parse_https_url_without_git_extension(self):
        """Test parsing HTTPS URL without .git extension."""
        url = "https://github.com/testuser/testrepo"
        result = parse_remote_url(url)
        assert result.owner == "testuser"
        assert result.repo == "testrepo"

    def test_parse_http_url(self):
        """Test parsing HTTP URL."""
        url = "http://github.com/organization/project.git"
        result = parse_remote_url(url)
        assert result.owner == "organization"
        assert result.repo == "project"

    def test_parse_invalid_url_format(self):
        """Test parsing completely invalid URL."""
        with pytest.raises(ValueError, match="Unsupported remote URL format"):
            parse_remote_url("not-a-url")

    def test_parse_non_github_url(self):
        """Test parsing non-GitHub URL."""
        with pytest.raises(ValueError, match="Unsupported remote URL format"):
            parse_remote_url("git@gitlab.com:owner/repo.git")

    def test_parse_invalid_github_https_url(self):
        """Test parsing invalid GitHub HTTPS URL."""
        with pytest.raises(ValueError, match="Invalid GitHub repository URL"):
            parse_remote_url("https://github.com/onlyowner")

    def test_parse_empty_url(self):
        """Test parsing empty URL."""
        with pytest.raises(ValueError):
            parse_remote_url("")


class TestNormalizeFilePath:
    """Test normalize_file_path function."""

    def test_normalize_absolute_path(self):
        """Test normalizing absolute path."""
        path = "/src/main.py"
        result = normalize_file_path(path)
        assert result == "src/main.py"

    def test_normalize_absolute_path_multiple_slashes(self):
        """Test normalizing absolute path with multiple leading slashes."""
        path = "///src/lib/file.py"
        result = normalize_file_path(path)
        assert result == "src/lib/file.py"

    def test_normalize_relative_path(self):
        """Test normalizing relative path."""
        path = "src/lib.py"
        result = normalize_file_path(path)
        assert result == "src/lib.py"

    def test_normalize_windows_path(self):
        """Test normalizing Windows-style path."""
        path = "src\\windows\\path\\file.py"
        result = normalize_file_path(path)
        assert result == "src/windows/path/file.py"

    def test_normalize_mixed_separators(self):
        """Test normalizing path with mixed separators."""
        path = "src\\unix/mixed\\path/file.py"
        result = normalize_file_path(path)
        assert result == "src/unix/mixed/path/file.py"

    def test_normalize_dot_path(self):
        """Test normalizing path with dots."""
        path = "./src/file.py"
        result = normalize_file_path(path)
        assert result == "src/file.py"

    def test_normalize_empty_path(self):
        """Test normalizing empty path."""
        path = ""
        result = normalize_file_path(path)
        assert result == ""

    def test_normalize_root_slash_only(self):
        """Test normalizing just a slash."""
        path = "/"
        result = normalize_file_path(path)
        assert result == ""


class TestBuildGithubUrl:
    """Test build_github_url function."""

    def test_build_url_basic(self):
        """Test building basic GitHub URL."""
        info = GitHubInfo(owner="owner", repo="repo")
        commit = "abc123"
        file_path = "src/main.py"
        result = build_github_url(info, commit, file_path)
        assert result == "https://github.com/owner/repo/blob/abc123/src/main.py"

    def test_build_url_with_long_sha(self):
        """Test building URL with full SHA hash."""
        info = GitHubInfo(owner="myorg", repo="myproject")
        commit = "a" * 40  # Full SHA-1 hash
        file_path = "README.md"
        result = build_github_url(info, commit, file_path)
        assert result == f"https://github.com/myorg/myproject/blob/{'a' * 40}/README.md"

    def test_build_url_deep_path(self):
        """Test building URL with deep file path."""
        info = GitHubInfo(owner="org", repo="project")
        commit = "def456"
        file_path = "src/components/ui/buttons/Button.tsx"
        result = build_github_url(info, commit, file_path)
        assert result == "https://github.com/org/project/blob/def456/src/components/ui/buttons/Button.tsx"

    def test_build_url_root_file(self):
        """Test building URL for root-level file."""
        info = GitHubInfo(owner="user", repo="repo")
        commit = "123abc"
        file_path = "README.md"
        result = build_github_url(info, commit, file_path)
        assert result == "https://github.com/user/repo/blob/123abc/README.md"

    def test_build_url_special_characters_in_path(self):
        """Test building URL with special characters in path."""
        info = GitHubInfo(owner="owner", repo="repo")
        commit = "abc123"
        file_path = "src/file-with-dash_and_underscore.py"
        result = build_github_url(info, commit, file_path)
        assert result == "https://github.com/owner/repo/blob/abc123/src/file-with-dash_and_underscore.py"

    def test_build_url_with_spaces_in_path(self):
        """Test building URL with spaces in path (should be preserved)."""
        info = GitHubInfo(owner="owner", repo="repo")
        commit = "abc123"
        file_path = "src/file with spaces.py"
        result = build_github_url(info, commit, file_path)
        # Note: GitHub will handle URL encoding when needed
        assert result == "https://github.com/owner/repo/blob/abc123/src/file with spaces.py"


class TestGenerateGithubUrl:
    """Test generate_github_url function."""

    def test_generate_url_ssh_format(self):
        """Test generating URL from SSH remote."""
        remote_url = "git@github.com:testorg/testrepo.git"
        commit = "commit123"
        file_path = "src/main.py"
        result = generate_github_url(remote_url, commit, file_path)
        assert result == "https://github.com/testorg/testrepo/blob/commit123/src/main.py"

    def test_generate_url_https_format(self):
        """Test generating URL from HTTPS remote."""
        remote_url = "https://github.com/myuser/myproject.git"
        commit = "abc456"
        file_path = "docs/README.md"
        result = generate_github_url(remote_url, commit, file_path)
        assert result == "https://github.com/myuser/myproject/blob/abc456/docs/README.md"

    def test_generate_url_normalized_path(self):
        """Test generating URL with path that needs normalization."""
        remote_url = "git@github.com:org/repo.git"
        commit = "xyz789"
        file_path = "/src/lib/module.py"  # Absolute path
        result = generate_github_url(remote_url, commit, file_path)
        assert result == "https://github.com/org/repo/blob/xyz789/src/lib/module.py"

    def test_generate_url_invalid_remote(self):
        """Test generating URL from invalid remote."""
        with pytest.raises(ValueError, match="Failed to generate GitHub URL"):
            generate_github_url("invalid-url", "commit", "file.py")

    def test_generate_url_empty_commit(self):
        """Test generating URL with empty commit (should still work)."""
        remote_url = "git@github.com:owner/repo.git"
        commit = ""
        file_path = "file.txt"
        result = generate_github_url(remote_url, commit, file_path)
        assert result == "https://github.com/owner/repo/blob//file.txt"


class TestGitHubInfo:
    """Test GitHubInfo dataclass."""

    def test_github_info_creation(self):
        """Test creating GitHubInfo instance."""
        info = GitHubInfo(owner="testowner", repo="testrepo")
        assert info.owner == "testowner"
        assert info.repo == "testrepo"

    def test_github_info_equality(self):
        """Test GitHubInfo equality."""
        info1 = GitHubInfo(owner="owner", repo="repo")
        info2 = GitHubInfo(owner="owner", repo="repo")
        info3 = GitHubInfo(owner="different", repo="repo")

        assert info1 == info2
        assert info1 != info3

    def test_github_info_string_representation(self):
        """Test GitHubInfo string representation."""
        info = GitHubInfo(owner="myorg", repo="myrepo")
        str_repr = str(info)
        assert "myorg" in str_repr
        assert "myrepo" in str_repr


if __name__ == "__main__":
    pytest.main([__file__, "-v"])