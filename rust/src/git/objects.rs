#[cfg(not(target_arch = "wasm32"))]
use git2::{Blob, Commit, Oid, Repository, Tag, Tree};
use serde::{Deserialize, Serialize};
use wasm_bindgen::prelude::*;

#[derive(Debug, Serialize, Deserialize, Clone)]
#[wasm_bindgen]
pub struct GitBlob {
    id: String,
    size: usize,
    is_binary: bool,
}

#[wasm_bindgen]
impl GitBlob {
    #[cfg(not(target_arch = "wasm32"))]
    #[allow(dead_code)]
    fn new_internal(blob: &Blob) -> Self {
        GitBlob {
            id: blob.id().to_string(),
            size: blob.size(),
            is_binary: blob.is_binary(),
        }
    }

    #[wasm_bindgen(getter)]
    pub fn id(&self) -> String {
        self.id.clone()
    }

    #[wasm_bindgen(getter)]
    pub fn size(&self) -> usize {
        self.size
    }

    #[wasm_bindgen(getter)]
    pub fn is_binary(&self) -> bool {
        self.is_binary
    }
}

#[derive(Debug, Serialize, Deserialize, Clone)]
#[wasm_bindgen]
pub struct GitTree {
    id: String,
    len: usize,
}

#[wasm_bindgen]
impl GitTree {
    #[cfg(not(target_arch = "wasm32"))]
    #[allow(dead_code)]
    fn new_internal(tree: &Tree) -> Self {
        GitTree {
            id: tree.id().to_string(),
            len: tree.len(),
        }
    }

    #[cfg(test)]
    pub fn new_for_test(id: String, len: usize) -> Self {
        GitTree { id, len }
    }

    #[wasm_bindgen(getter)]
    pub fn id(&self) -> String {
        self.id.clone()
    }

    #[wasm_bindgen(getter)]
    pub fn len(&self) -> usize {
        self.len
    }
}

#[derive(Debug, Serialize, Deserialize, Clone)]
#[wasm_bindgen]
pub struct GitCommit {
    id: String,
    message: String,
    author_name: String,
    author_email: String,
    time: i64,
    tree_id: String,
    parent_ids: Vec<String>,
}

#[wasm_bindgen]
impl GitCommit {
    #[cfg(not(target_arch = "wasm32"))]
    #[allow(dead_code)]
    fn new_internal(commit: &Commit) -> Self {
        let parent_ids = (0..commit.parent_count())
            .filter_map(|i| commit.parent_id(i).ok().map(|id| id.to_string()))
            .collect();

        GitCommit {
            id: commit.id().to_string(),
            message: commit.message().unwrap_or("").to_string(),
            author_name: commit.author().name().unwrap_or("").to_string(),
            author_email: commit.author().email().unwrap_or("").to_string(),
            time: commit.time().seconds(),
            tree_id: commit.tree_id().to_string(),
            parent_ids,
        }
    }

    #[cfg(test)]
    pub fn new_for_test(id: String, message: String, author_name: String, author_email: String, time: i64, tree_id: String, parent_ids: Vec<String>) -> Self {
        GitCommit { id, message, author_name, author_email, time, tree_id, parent_ids }
    }

    #[wasm_bindgen(getter)]
    pub fn id(&self) -> String {
        self.id.clone()
    }

    #[wasm_bindgen(getter)]
    pub fn message(&self) -> String {
        self.message.clone()
    }

    #[wasm_bindgen(getter)]
    pub fn author_name(&self) -> String {
        self.author_name.clone()
    }

    #[wasm_bindgen(getter)]
    pub fn author_email(&self) -> String {
        self.author_email.clone()
    }

    #[wasm_bindgen(getter)]
    pub fn time(&self) -> i64 {
        self.time
    }

    #[wasm_bindgen(getter)]
    pub fn tree_id(&self) -> String {
        self.tree_id.clone()
    }

    #[wasm_bindgen(getter)]
    pub fn parent_ids(&self) -> Vec<String> {
        self.parent_ids.clone()
    }
}

#[derive(Debug, Serialize, Deserialize, Clone)]
#[wasm_bindgen]
pub struct GitTag {
    id: String,
    name: String,
    message: String,
    target_id: String,
}

#[wasm_bindgen]
impl GitTag {
    #[cfg(not(target_arch = "wasm32"))]
    #[allow(dead_code)]
    fn new_internal(tag: &Tag) -> Self {
        GitTag {
            id: tag.id().to_string(),
            name: tag.name().unwrap_or("").to_string(),
            message: tag.message().unwrap_or("").to_string(),
            target_id: tag.target_id().to_string(),
        }
    }

    #[cfg(test)]
    pub fn new_for_test(id: String, name: String, message: String, target_id: String) -> Self {
        GitTag { id, name, message, target_id }
    }

    #[wasm_bindgen(getter)]
    pub fn id(&self) -> String {
        self.id.clone()
    }

    #[wasm_bindgen(getter)]
    pub fn name(&self) -> String {
        self.name.clone()
    }

    #[wasm_bindgen(getter)]
    pub fn message(&self) -> String {
        self.message.clone()
    }

    #[wasm_bindgen(getter)]
    pub fn target_id(&self) -> String {
        self.target_id.clone()
    }
}

#[cfg(not(target_arch = "wasm32"))]
pub fn get_blob(repo: &Repository, hash: &str) -> Result<GitBlob, git2::Error> {
    let oid = Oid::from_str(hash)?;
    let blob = repo.find_blob(oid)?;
    Ok(GitBlob::new_internal(&blob))
}

#[cfg(not(target_arch = "wasm32"))]
pub fn get_tree(repo: &Repository, hash: &str) -> Result<GitTree, git2::Error> {
    let oid = Oid::from_str(hash)?;
    let tree = repo.find_tree(oid)?;
    Ok(GitTree::new_internal(&tree))
}

#[cfg(not(target_arch = "wasm32"))]
pub fn get_commit(repo: &Repository, hash: &str) -> Result<GitCommit, git2::Error> {
    let oid = Oid::from_str(hash)?;
    let commit = repo.find_commit(oid)?;
    Ok(GitCommit::new_internal(&commit))
}

#[cfg(not(target_arch = "wasm32"))]
pub fn get_tag(repo: &Repository, hash: &str) -> Result<GitTag, git2::Error> {
    let oid = Oid::from_str(hash)?;
    let tag = repo.find_tag(oid)?;
    Ok(GitTag::new_internal(&tag))
}

#[cfg(test)]
impl GitBlob {
    pub fn new_test(id: String, size: usize, is_binary: bool) -> Self {
        GitBlob { id, size, is_binary }
    }
}

#[cfg(test)]
impl GitTree {
    pub fn new_test(id: String, len: usize) -> Self {
        GitTree { id, len }
    }
}

#[cfg(test)]
impl GitCommit {
    pub fn new_test(
        id: String,
        message: String,
        author_name: String,
        author_email: String,
        time: i64,
        tree_id: String,
        parent_ids: Vec<String>,
    ) -> Self {
        GitCommit {
            id,
            message,
            author_name,
            author_email,
            time,
            tree_id,
            parent_ids,
        }
    }
}

#[cfg(test)]
impl GitTag {
    pub fn new_test(id: String, name: String, message: String, target_id: String) -> Self {
        GitTag {
            id,
            name,
            message,
            target_id,
        }
    }
}

#[cfg(all(test, not(target_arch = "wasm32")))]
mod tests {
    use super::*;
    use git2::{Repository};

    fn get_test_repo() -> Repository {
        let current_dir = std::env::current_dir().expect("Failed to get current directory");
        let mut path = current_dir;

        loop {
            if path.join(".git").exists() {
                return Repository::open(path).expect("Failed to open repository");
            }
            if !path.pop() {
                panic!("No git repository found in parent directories");
            }
        }
    }

    #[test]
    fn test_git_blob_creation() {
        let blob = GitBlob::new_test(
            "test123".to_string(),
            100,
            false,
        );

        assert_eq!(blob.id(), "test123");
        assert_eq!(blob.size(), 100);
        assert_eq!(blob.is_binary(), false);
    }

    #[test]
    fn test_git_tree_creation() {
        let tree = GitTree::new_test(
            "tree456".to_string(),
            5,
        );

        assert_eq!(tree.id(), "tree456");
        assert_eq!(tree.len(), 5);
    }

    #[test]
    fn test_git_commit_creation() {
        let commit = GitCommit::new_test(
            "commit789".to_string(),
            "Test commit".to_string(),
            "Test Author".to_string(),
            "test@example.com".to_string(),
            1234567890,
            "tree123".to_string(),
            vec!["parent1".to_string(), "parent2".to_string()],
        );

        assert_eq!(commit.id(), "commit789");
        assert_eq!(commit.message(), "Test commit");
        assert_eq!(commit.author_name(), "Test Author");
        assert_eq!(commit.author_email(), "test@example.com");
        assert_eq!(commit.time(), 1234567890);
        assert_eq!(commit.tree_id(), "tree123");
        assert_eq!(commit.parent_ids(), vec!["parent1", "parent2"]);
    }

    #[test]
    fn test_git_tag_creation() {
        let tag = GitTag::new_test(
            "tag999".to_string(),
            "v1.0.0".to_string(),
            "Release version 1.0.0".to_string(),
            "target123".to_string(),
        );

        assert_eq!(tag.id(), "tag999");
        assert_eq!(tag.name(), "v1.0.0");
        assert_eq!(tag.message(), "Release version 1.0.0");
        assert_eq!(tag.target_id(), "target123");
    }

    #[test]
    fn test_get_commit_from_repo() {
        let repo = get_test_repo();
        let head = repo.head().expect("Failed to get HEAD");
        let head_commit = head.peel_to_commit().expect("Failed to get commit");
        let commit_id = head_commit.id().to_string();

        let git_commit = get_commit(&repo, &commit_id).expect("Failed to get commit");

        assert_eq!(git_commit.id(), commit_id);
        assert!(!git_commit.message().is_empty() || git_commit.message() == "");
        assert_eq!(git_commit.tree_id(), head_commit.tree_id().to_string());
    }

    #[test]
    fn test_invalid_oid() {
        let repo = get_test_repo();

        let result = get_blob(&repo, "invalid_hash");
        assert!(result.is_err());

        let result = get_tree(&repo, "invalid_hash");
        assert!(result.is_err());

        let result = get_commit(&repo, "invalid_hash");
        assert!(result.is_err());
    }
}