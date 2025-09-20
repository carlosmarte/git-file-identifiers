"""Unit tests for GitFileId main class."""

import pytest
from pathlib import Path
import sys
from unittest.mock import Mock, MagicMock, patch, call

sys.path.insert(0, str(Path(__file__).parent.parent))

from git_identify import GitFileId, generate_github_url_direct


class TestGitFileIdInit:
    """Test GitFileId initialization."""

    def test_init_default(self):
        """Test default initialization."""
        git_id = GitFileId()
        assert git_id.repo_path is None
        assert git_id.repo is None

    @patch('git_identify.logger')
    def test_init_logging(self, mock_logger):
        """Test that initialization logs properly."""
        git_id = GitFileId()
        mock_logger.info.assert_called_once_with("GitFileId initialized")
        assert git_id.repo_path is None


class TestGitFileIdFindRepository:
    """Test GitFileId.find_repository method."""

    @patch('git_identify.find_git_root')
    @patch('git_identify.git.Repo')
    @patch('git_identify.USE_PYGIT2', False)
    def test_find_repository_success(self, mock_repo_cls, mock_find_root):
        """Test successful repository finding."""
        mock_find_root.return_value = Path("/test/repo")
        mock_repo = Mock()
        mock_repo_cls.return_value = mock_repo

        git_id = GitFileId()
        git_id.find_repository("/test/repo/file.txt")

        assert git_id.repo_path == Path("/test/repo")
        assert git_id.repo == mock_repo
        mock_find_root.assert_called_once_with("/test/repo/file.txt")
        mock_repo_cls.assert_called_once_with(str(Path("/test/repo")))

    @patch('git_identify.find_git_root')
    def test_find_repository_not_found(self, mock_find_root):
        """Test repository not found."""
        mock_find_root.side_effect = ValueError("No .git directory found")

        git_id = GitFileId()
        with pytest.raises(ValueError, match="Failed to find repository"):
            git_id.find_repository("/not/a/repo")

    @patch('git_identify.find_git_root')
    @patch('git_identify.git.Repo')
    @patch('git_identify.USE_PYGIT2', False)
    def test_find_repository_repo_error(self, mock_repo_cls, mock_find_root):
        """Test error opening repository."""
        mock_find_root.return_value = Path("/test/repo")
        mock_repo_cls.side_effect = Exception("Cannot open repository")

        git_id = GitFileId()
        with pytest.raises(ValueError, match="Failed to find repository"):
            git_id.find_repository("/test/repo/file.txt")


class TestGitFileIdGenerateGithubUrl:
    """Test GitFileId.generate_github_url method."""

    @patch('git_identify.get_remote_url')
    @patch('git_identify.get_current_branch_commit_for_file')
    @patch('git_identify.generate_github_url')
    def test_generate_url_success(self, mock_gen_url, mock_get_commit, mock_get_remote):
        """Test successful URL generation."""
        mock_get_remote.return_value = "git@github.com:owner/repo.git"
        mock_get_commit.return_value = "abc123"
        mock_gen_url.return_value = "https://github.com/owner/repo/blob/abc123/file.txt"

        git_id = GitFileId()
        git_id.repo_path = Path("/test/repo")
        git_id.repo = Mock()

        # Test with absolute path
        with patch('git_identify.Path.cwd', return_value=Path("/test/repo")):
            result = git_id.generate_github_url("file.txt")

        assert result == "https://github.com/owner/repo/blob/abc123/file.txt"

    def test_generate_url_no_repo(self):
        """Test URL generation without repository."""
        git_id = GitFileId()
        with pytest.raises(ValueError, match="Repository not found"):
            git_id.generate_github_url("file.txt")

    @patch('git_identify.get_remote_url')
    def test_generate_url_remote_error(self, mock_get_remote):
        """Test URL generation with remote error."""
        mock_get_remote.side_effect = Exception("No origin remote")

        git_id = GitFileId()
        git_id.repo_path = Path("/test/repo")
        git_id.repo = Mock()

        with pytest.raises(ValueError, match="Failed to generate GitHub URL"):
            git_id.generate_github_url("file.txt")


class TestGitFileIdGetFileHash:
    """Test GitFileId.get_file_hash method."""

    @patch('git_identify.get_current_branch_commit_for_file')
    def test_get_file_hash_success(self, mock_get_commit):
        """Test successful file hash retrieval."""
        mock_get_commit.return_value = "abc123def456"

        git_id = GitFileId()
        git_id.repo = Mock()

        result = git_id.get_file_hash("test.txt")
        assert result == "abc123def456"
        mock_get_commit.assert_called_once_with(git_id.repo, "test.txt")

    def test_get_file_hash_no_repo(self):
        """Test file hash without repository."""
        git_id = GitFileId()
        with pytest.raises(ValueError, match="Repository not found"):
            git_id.get_file_hash("test.txt")

    @patch('git_identify.get_current_branch_commit_for_file')
    def test_get_file_hash_error(self, mock_get_commit):
        """Test file hash with error."""
        mock_get_commit.side_effect = Exception("File not found")

        git_id = GitFileId()
        git_id.repo = Mock()

        with pytest.raises(ValueError, match="Failed to get file hash"):
            git_id.get_file_hash("test.txt")


class TestGitFileIdGetObjects:
    """Test GitFileId methods for getting Git objects."""

    @patch('git_identify.get_blob')
    def test_get_blob_success(self, mock_get_blob):
        """Test successful blob retrieval."""
        mock_blob = Mock()
        mock_get_blob.return_value = mock_blob

        git_id = GitFileId()
        git_id.repo = Mock()

        result = git_id.get_blob("blobhash123")
        assert result == mock_blob
        mock_get_blob.assert_called_once_with(git_id.repo, "blobhash123")

    def test_get_blob_no_repo(self):
        """Test blob retrieval without repository."""
        git_id = GitFileId()
        with pytest.raises(ValueError, match="Repository not found"):
            git_id.get_blob("hash")

    @patch('git_identify.get_tree')
    def test_get_tree_success(self, mock_get_tree):
        """Test successful tree retrieval."""
        mock_tree = Mock()
        mock_get_tree.return_value = mock_tree

        git_id = GitFileId()
        git_id.repo = Mock()

        result = git_id.get_tree("treehash123")
        assert result == mock_tree

    @patch('git_identify.get_commit')
    def test_get_commit_success(self, mock_get_commit):
        """Test successful commit retrieval."""
        mock_commit = Mock()
        mock_get_commit.return_value = mock_commit

        git_id = GitFileId()
        git_id.repo = Mock()

        result = git_id.get_commit("commithash123")
        assert result == mock_commit

    @patch('git_identify.get_tag')
    def test_get_tag_success(self, mock_get_tag):
        """Test successful tag retrieval."""
        mock_tag = Mock()
        mock_get_tag.return_value = mock_tag

        git_id = GitFileId()
        git_id.repo = Mock()

        result = git_id.get_tag("taghash123")
        assert result == mock_tag

    @patch('git_identify.get_blob')
    def test_get_blob_error(self, mock_get_blob):
        """Test blob retrieval with error."""
        mock_get_blob.side_effect = Exception("Blob not found")

        git_id = GitFileId()
        git_id.repo = Mock()

        with pytest.raises(ValueError, match="Failed to get blob"):
            git_id.get_blob("invalid")


class TestGitFileIdListRefs:
    """Test GitFileId.list_refs method."""

    @patch('git_identify.list_refs')
    def test_list_refs_success(self, mock_list_refs):
        """Test successful reference listing."""
        mock_list_refs.return_value = ["refs/heads/main", "refs/tags/v1.0.0"]

        git_id = GitFileId()
        git_id.repo = Mock()

        result = git_id.list_refs()
        assert result == ["refs/heads/main", "refs/tags/v1.0.0"]
        mock_list_refs.assert_called_once_with(git_id.repo)

    def test_list_refs_no_repo(self):
        """Test listing refs without repository."""
        git_id = GitFileId()
        with pytest.raises(ValueError, match="Repository not found"):
            git_id.list_refs()

    @patch('git_identify.list_refs')
    def test_list_refs_error(self, mock_list_refs):
        """Test listing refs with error."""
        mock_list_refs.side_effect = Exception("Cannot list refs")

        git_id = GitFileId()
        git_id.repo = Mock()

        with pytest.raises(ValueError, match="Failed to list refs"):
            git_id.list_refs()


class TestGitFileIdGetFileStatus:
    """Test GitFileId.get_file_status method."""

    @patch('git_identify.get_file_status')
    def test_get_file_status_success(self, mock_get_status):
        """Test successful file status retrieval."""
        mock_get_status.return_value = "modified"

        git_id = GitFileId()
        git_id.repo = Mock()

        result = git_id.get_file_status("test.txt")
        assert result == "modified"
        mock_get_status.assert_called_once_with(git_id.repo, "test.txt")

    def test_get_file_status_no_repo(self):
        """Test file status without repository."""
        git_id = GitFileId()
        with pytest.raises(ValueError, match="Repository not found"):
            git_id.get_file_status("test.txt")


class TestGitFileIdGetHeadRef:
    """Test GitFileId.get_head_ref method."""

    @patch('git_identify.get_head_ref')
    def test_get_head_ref_success(self, mock_get_head):
        """Test successful HEAD ref retrieval."""
        mock_get_head.return_value = "main"

        git_id = GitFileId()
        git_id.repo = Mock()

        result = git_id.get_head_ref()
        assert result == "main"
        mock_get_head.assert_called_once_with(git_id.repo)

    def test_get_head_ref_no_repo(self):
        """Test HEAD ref without repository."""
        git_id = GitFileId()
        with pytest.raises(ValueError, match="Repository not found"):
            git_id.get_head_ref()


class TestGenerateGithubUrlDirect:
    """Test generate_github_url_direct standalone function."""

    @patch('git_identify.find_git_root')
    @patch('git_identify.git.Repo')
    @patch('git_identify.get_remote_url')
    @patch('git_identify.get_current_branch_commit_for_file')
    @patch('git_identify.generate_github_url')
    @patch('git_identify.USE_PYGIT2', False)
    def test_generate_direct_success(self, mock_gen_url, mock_get_commit,
                                    mock_get_remote, mock_repo_cls, mock_find_root):
        """Test successful direct URL generation."""
        mock_find_root.return_value = Path("/test/repo")
        mock_repo = Mock()
        mock_repo_cls.return_value = mock_repo
        mock_get_remote.return_value = "git@github.com:owner/repo.git"
        mock_get_commit.return_value = "abc123"
        mock_gen_url.return_value = "https://github.com/owner/repo/blob/abc123/file.txt"

        result = generate_github_url_direct("/test/repo/file.txt")

        assert result == "https://github.com/owner/repo/blob/abc123/file.txt"
        mock_find_root.assert_called_once_with("/test/repo/file.txt")
        mock_repo_cls.assert_called_once_with(str(Path("/test/repo")))

    @patch('git_identify.find_git_root')
    def test_generate_direct_no_repo(self, mock_find_root):
        """Test direct generation with no repository."""
        mock_find_root.side_effect = ValueError("No .git directory found")

        with pytest.raises(ValueError, match="Failed to generate GitHub URL"):
            generate_github_url_direct("/not/a/repo/file.txt")

    @patch('git_identify.find_git_root')
    @patch('git_identify.git.Repo')
    @patch('git_identify.get_remote_url')
    @patch('git_identify.USE_PYGIT2', False)
    def test_generate_direct_no_remote(self, mock_get_remote, mock_repo_cls, mock_find_root):
        """Test direct generation with no remote."""
        mock_find_root.return_value = Path("/test/repo")
        mock_repo = Mock()
        mock_repo_cls.return_value = mock_repo
        mock_get_remote.side_effect = ValueError("No origin remote")

        with pytest.raises(ValueError, match="Failed to generate GitHub URL"):
            generate_github_url_direct("/test/repo/file.txt")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])