"""Unit tests for objects module."""

import pytest
from pathlib import Path
import sys
from unittest.mock import Mock, MagicMock, patch

sys.path.insert(0, str(Path(__file__).parent.parent))

from git_identify.objects import (
    GitBlob,
    GitTree,
    GitCommit,
    GitTag,
    get_blob,
    get_tree,
    get_commit,
    get_tag,
)


class TestGitBlob:
    """Test GitBlob dataclass."""

    def test_git_blob_creation(self):
        """Test creating GitBlob instance."""
        blob = GitBlob(id="abc123", size=1024, is_binary=False)
        assert blob.id == "abc123"
        assert blob.size == 1024
        assert blob.is_binary is False

    def test_git_blob_binary(self):
        """Test creating binary GitBlob."""
        blob = GitBlob(id="def456", size=2048, is_binary=True)
        assert blob.id == "def456"
        assert blob.size == 2048
        assert blob.is_binary is True

    def test_git_blob_equality(self):
        """Test GitBlob equality."""
        blob1 = GitBlob(id="abc", size=100, is_binary=False)
        blob2 = GitBlob(id="abc", size=100, is_binary=False)
        blob3 = GitBlob(id="def", size=100, is_binary=False)

        assert blob1 == blob2
        assert blob1 != blob3


class TestGitTree:
    """Test GitTree dataclass."""

    def test_git_tree_creation(self):
        """Test creating GitTree instance."""
        tree = GitTree(id="tree123", len=10)
        assert tree.id == "tree123"
        assert tree.len == 10

    def test_git_tree_empty(self):
        """Test creating empty GitTree."""
        tree = GitTree(id="empty", len=0)
        assert tree.id == "empty"
        assert tree.len == 0

    def test_git_tree_equality(self):
        """Test GitTree equality."""
        tree1 = GitTree(id="tree1", len=5)
        tree2 = GitTree(id="tree1", len=5)
        tree3 = GitTree(id="tree2", len=5)

        assert tree1 == tree2
        assert tree1 != tree3


class TestGitCommit:
    """Test GitCommit dataclass."""

    def test_git_commit_creation(self):
        """Test creating GitCommit instance."""
        commit = GitCommit(
            id="commit123",
            message="Test commit",
            author_name="Test Author",
            author_email="test@example.com",
            time=1234567890,
            tree_id="tree456",
            parent_ids=["parent1", "parent2"]
        )
        assert commit.id == "commit123"
        assert commit.message == "Test commit"
        assert commit.author_name == "Test Author"
        assert commit.author_email == "test@example.com"
        assert commit.time == 1234567890
        assert commit.tree_id == "tree456"
        assert commit.parent_ids == ["parent1", "parent2"]

    def test_git_commit_no_parents(self):
        """Test creating GitCommit with no parents (initial commit)."""
        commit = GitCommit(
            id="initial",
            message="Initial commit",
            author_name="Author",
            author_email="author@example.com",
            time=1000000000,
            tree_id="tree000",
            parent_ids=[]
        )
        assert commit.parent_ids == []

    def test_git_commit_empty_fields(self):
        """Test creating GitCommit with empty fields."""
        commit = GitCommit(
            id="commit",
            message="",
            author_name="",
            author_email="",
            time=0,
            tree_id="tree",
            parent_ids=[]
        )
        assert commit.message == ""
        assert commit.author_name == ""
        assert commit.author_email == ""


class TestGitTag:
    """Test GitTag dataclass."""

    def test_git_tag_creation(self):
        """Test creating GitTag instance."""
        tag = GitTag(
            id="tag123",
            name="v1.0.0",
            message="Release version 1.0.0",
            target_id="commit456"
        )
        assert tag.id == "tag123"
        assert tag.name == "v1.0.0"
        assert tag.message == "Release version 1.0.0"
        assert tag.target_id == "commit456"

    def test_git_tag_no_message(self):
        """Test creating GitTag without message."""
        tag = GitTag(
            id="tag789",
            name="v2.0.0",
            message="",
            target_id="commit789"
        )
        assert tag.message == ""

    def test_git_tag_equality(self):
        """Test GitTag equality."""
        tag1 = GitTag(id="tag1", name="v1", message="msg", target_id="commit1")
        tag2 = GitTag(id="tag1", name="v1", message="msg", target_id="commit1")
        tag3 = GitTag(id="tag2", name="v1", message="msg", target_id="commit1")

        assert tag1 == tag2
        assert tag1 != tag3


class TestGetBlob:
    """Test get_blob function."""

    @patch('git_identify.objects.USE_PYGIT2', False)
    def test_get_blob_gitpython(self):
        """Test getting blob using GitPython."""
        mock_repo = Mock()
        mock_stream = Mock()
        mock_data = b"Hello, World!"
        mock_stream.read.return_value = mock_data

        mock_repo.odb.stream.return_value = mock_stream

        result = get_blob(mock_repo, "abc123")
        assert isinstance(result, GitBlob)
        assert result.id == "abc123"
        assert result.size == len(mock_data)
        assert result.is_binary is False

    @patch('git_identify.objects.USE_PYGIT2', False)
    def test_get_blob_binary_gitpython(self):
        """Test getting binary blob using GitPython."""
        mock_repo = Mock()
        mock_stream = Mock()
        # Binary data with null byte
        mock_data = b"Binary\x00Data"
        mock_stream.read.return_value = mock_data

        mock_repo.odb.stream.return_value = mock_stream

        result = get_blob(mock_repo, "bin123")
        assert isinstance(result, GitBlob)
        assert result.id == "bin123"
        assert result.is_binary is True

    def test_get_blob_error(self):
        """Test error handling when getting blob."""
        mock_repo = Mock()
        mock_repo.odb.stream.side_effect = Exception("Blob not found")

        with pytest.raises(ValueError, match="Failed to get blob"):
            get_blob(mock_repo, "invalid")


class TestGetTree:
    """Test get_tree function."""

    @patch('git_identify.objects.USE_PYGIT2', False)
    def test_get_tree_gitpython(self):
        """Test getting tree using GitPython."""
        mock_repo = Mock()
        mock_tree = Mock()
        mock_tree.traverse.return_value = ["entry1", "entry2", "entry3"]

        mock_repo.tree.return_value = mock_tree

        result = get_tree(mock_repo, "tree123")
        assert isinstance(result, GitTree)
        assert result.id == "tree123"
        assert result.len == 3

    @patch('git_identify.objects.USE_PYGIT2', False)
    def test_get_tree_empty(self):
        """Test getting empty tree."""
        mock_repo = Mock()
        mock_tree = Mock()
        mock_tree.traverse.return_value = []

        mock_repo.tree.return_value = mock_tree

        result = get_tree(mock_repo, "emptytree")
        assert result.len == 0

    def test_get_tree_error(self):
        """Test error handling when getting tree."""
        mock_repo = Mock()
        mock_repo.tree.side_effect = Exception("Tree not found")

        with pytest.raises(ValueError, match="Failed to get tree"):
            get_tree(mock_repo, "invalid")


class TestGetCommit:
    """Test get_commit function."""

    @patch('git_identify.objects.USE_PYGIT2', False)
    def test_get_commit_gitpython(self):
        """Test getting commit using GitPython."""
        mock_repo = Mock()
        mock_commit = Mock()
        mock_commit.hexsha = "commit123"
        mock_commit.message = "Test commit message"
        mock_commit.author.name = "Test Author"
        mock_commit.author.email = "test@example.com"
        mock_commit.authored_date = 1234567890
        mock_commit.tree.hexsha = "tree456"

        # Mock parents
        parent1 = Mock()
        parent1.hexsha = "parent1"
        parent2 = Mock()
        parent2.hexsha = "parent2"
        mock_commit.parents = [parent1, parent2]

        mock_repo.commit.return_value = mock_commit

        result = get_commit(mock_repo, "commit123")
        assert isinstance(result, GitCommit)
        assert result.id == "commit123"
        assert result.message == "Test commit message"
        assert result.author_name == "Test Author"
        assert result.author_email == "test@example.com"
        assert result.time == 1234567890
        assert result.tree_id == "tree456"
        assert result.parent_ids == ["parent1", "parent2"]

    @patch('git_identify.objects.USE_PYGIT2', False)
    def test_get_commit_no_parents(self):
        """Test getting commit with no parents."""
        mock_repo = Mock()
        mock_commit = Mock()
        mock_commit.hexsha = "initial"
        mock_commit.message = "Initial commit"
        mock_commit.author.name = "Author"
        mock_commit.author.email = "author@example.com"
        mock_commit.authored_date = 1000000000
        mock_commit.tree.hexsha = "tree000"
        mock_commit.parents = []

        mock_repo.commit.return_value = mock_commit

        result = get_commit(mock_repo, "initial")
        assert result.parent_ids == []

    @patch('git_identify.objects.USE_PYGIT2', False)
    def test_get_commit_none_fields(self):
        """Test getting commit with None fields."""
        mock_repo = Mock()
        mock_commit = Mock()
        mock_commit.hexsha = "commit"
        mock_commit.message = None
        mock_commit.author.name = None
        mock_commit.author.email = None
        mock_commit.authored_date = 0
        mock_commit.tree.hexsha = "tree"
        mock_commit.parents = []

        mock_repo.commit.return_value = mock_commit

        result = get_commit(mock_repo, "commit")
        assert result.message == ""
        assert result.author_name == ""
        assert result.author_email == ""

    def test_get_commit_error(self):
        """Test error handling when getting commit."""
        mock_repo = Mock()
        mock_repo.commit.side_effect = Exception("Commit not found")

        with pytest.raises(ValueError, match="Failed to get commit"):
            get_commit(mock_repo, "invalid")


class TestGetTag:
    """Test get_tag function."""

    @patch('git_identify.objects.USE_PYGIT2', False)
    def test_get_tag_gitpython(self):
        """Test getting tag using GitPython."""
        mock_repo = Mock()

        # Create mock tag
        mock_tag_obj = Mock()
        mock_tag_obj.hexsha = "tag123"
        mock_tag_obj.message = "Release v1.0.0"
        mock_tag_obj.object.hexsha = "commit456"

        mock_tag_ref = Mock()
        mock_tag_ref.name = "v1.0.0"
        mock_tag_ref.tag = mock_tag_obj

        mock_repo.tags = [mock_tag_ref]

        result = get_tag(mock_repo, "tag123")
        assert isinstance(result, GitTag)
        assert result.id == "tag123"
        assert result.name == "v1.0.0"
        assert result.message == "Release v1.0.0"
        assert result.target_id == "commit456"

    @patch('git_identify.objects.USE_PYGIT2', False)
    def test_get_tag_not_found(self):
        """Test getting non-existent tag."""
        mock_repo = Mock()
        mock_repo.tags = []

        with pytest.raises(ValueError, match="Tag with hash notfound not found"):
            get_tag(mock_repo, "notfound")

    @patch('git_identify.objects.USE_PYGIT2', False)
    def test_get_tag_no_message(self):
        """Test getting tag without message."""
        mock_repo = Mock()

        mock_tag_obj = Mock()
        mock_tag_obj.hexsha = "tag789"
        mock_tag_obj.message = None
        mock_tag_obj.object.hexsha = "commit789"

        mock_tag_ref = Mock()
        mock_tag_ref.name = "v2.0.0"
        mock_tag_ref.tag = mock_tag_obj

        mock_repo.tags = [mock_tag_ref]

        result = get_tag(mock_repo, "tag789")
        assert result.message == ""

    def test_get_tag_error(self):
        """Test error handling when getting tag."""
        mock_repo = Mock()
        mock_repo.tags = Mock(side_effect=Exception("Error accessing tags"))

        with pytest.raises(ValueError, match="Failed to get tag"):
            get_tag(mock_repo, "invalid")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])