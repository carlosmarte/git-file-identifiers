#[cfg(not(target_arch = "wasm32"))]
use git2::{Repository, StatusOptions};
use std::path::{Path, PathBuf};
use anyhow::{Result, anyhow};

pub fn find_git_root(start_path: &str) -> Result<PathBuf> {
    let path = Path::new(start_path);
    let mut current_dir = if path.is_file() {
        path.parent().ok_or_else(|| anyhow!("Cannot get parent directory"))?
    } else {
        path
    };

    loop {
        let git_dir = current_dir.join(".git");
        if git_dir.exists() {
            return Ok(current_dir.to_path_buf());
        }

        match current_dir.parent() {
            Some(parent) => current_dir = parent,
            None => return Err(anyhow!("No .git directory found")),
        }
    }
}

#[cfg(not(target_arch = "wasm32"))]
#[allow(dead_code)]
pub fn get_file_hash_at_commit(repo: &Repository, file_path: &str, commit_hash: &str) -> Result<String> {
    let oid = git2::Oid::from_str(commit_hash)?;
    let commit = repo.find_commit(oid)?;
    let tree = commit.tree()?;

    let entry = tree.get_path(Path::new(file_path))?;
    Ok(entry.id().to_string())
}

#[cfg(not(target_arch = "wasm32"))]
pub fn get_current_branch_commit_for_file(repo: &Repository, file_path: &str) -> Result<String> {
    let head = repo.head()?;
    let commit = head.peel_to_commit()?;

    let repo_path = repo.path().parent().ok_or_else(|| anyhow!("Cannot get repository path"))?;
    let full_path = repo_path.join(file_path);

    if !full_path.exists() {
        return Err(anyhow!("File does not exist: {}", file_path));
    }

    Ok(commit.id().to_string())
}

#[cfg(not(target_arch = "wasm32"))]
pub fn get_remote_url(repo: &Repository) -> Result<String> {
    let remote = repo.find_remote("origin")?;
    let url = remote.url().ok_or_else(|| anyhow!("Remote URL not found"))?;
    Ok(url.to_string())
}

#[cfg(not(target_arch = "wasm32"))]
pub fn list_refs(repo: &Repository) -> Result<Vec<String>> {
    let mut refs = Vec::new();

    let references = repo.references()?;
    for reference in references {
        if let Ok(reference) = reference {
            if let Some(name) = reference.name() {
                refs.push(name.to_string());
            }
        }
    }

    Ok(refs)
}

#[cfg(not(target_arch = "wasm32"))]
pub fn get_file_status(repo: &Repository, file_path: &str) -> Result<String> {
    let mut opts = StatusOptions::new();
    opts.include_untracked(true)
        .include_ignored(false)
        .pathspec(file_path);

    let statuses = repo.statuses(Some(&mut opts))?;

    if statuses.is_empty() {
        return Ok("clean".to_string());
    }

    let status = statuses.get(0).ok_or_else(|| anyhow!("Cannot get file status"))?;
    let status_flags = status.status();

    let status_str = if status_flags.contains(git2::Status::WT_NEW) {
        "untracked"
    } else if status_flags.contains(git2::Status::WT_MODIFIED) {
        "modified"
    } else if status_flags.contains(git2::Status::INDEX_NEW) {
        "added"
    } else if status_flags.contains(git2::Status::INDEX_MODIFIED) {
        "staged"
    } else if status_flags.contains(git2::Status::INDEX_DELETED) {
        "deleted"
    } else {
        "unknown"
    };

    Ok(status_str.to_string())
}

#[cfg(not(target_arch = "wasm32"))]
pub fn get_head_ref(repo: &Repository) -> Result<String> {
    let head = repo.head()?;

    if head.is_branch() {
        Ok(head.shorthand().unwrap_or("HEAD").to_string())
    } else {
        let commit = head.peel_to_commit()?;
        Ok(commit.id().to_string())
    }
}

#[cfg(all(test, not(target_arch = "wasm32")))]
mod tests {
    use super::*;
    use git2::Repository;

    #[test]
    fn test_find_git_root_from_file() {
        let readme_path = std::env::current_dir()
            .expect("Failed to get current dir")
            .join("README.md");

        if readme_path.exists() {
            let result = find_git_root(readme_path.to_str().unwrap());
            assert!(result.is_ok());
            let git_root = result.unwrap();
            assert!(git_root.join(".git").exists());
        }
    }

    #[test]
    fn test_find_git_root_from_directory() {
        let current_dir = std::env::current_dir().expect("Failed to get current dir");

        let result = find_git_root(current_dir.to_str().unwrap());

        assert!(result.is_ok());
        let git_root = result.unwrap();
        assert!(git_root.join(".git").exists());
    }

    #[test]
    fn test_find_git_root_no_repo() {
        let result = find_git_root("/tmp");
        assert!(result.is_err());
        assert!(result.unwrap_err().to_string().contains("No .git directory found"));
    }

    #[test]
    fn test_get_remote_url() {
        let current_dir = std::env::current_dir().expect("Failed to get current dir");

        if let Ok(git_root) = find_git_root(current_dir.to_str().unwrap()) {
            let repo = Repository::open(&git_root).expect("Failed to open repo");
            let result = get_remote_url(&repo);

            if result.is_ok() {
                let url = result.unwrap();
                assert!(!url.is_empty());
                assert!(url.contains("github.com") || url.contains("git@"));
            }
        }
    }

    #[test]
    fn test_list_refs() {
        let current_dir = std::env::current_dir().expect("Failed to get current dir");

        if let Ok(git_root) = find_git_root(current_dir.to_str().unwrap()) {
            let repo = Repository::open(&git_root).expect("Failed to open repo");
            let result = list_refs(&repo);

            assert!(result.is_ok());
            let refs = result.unwrap();
            assert!(!refs.is_empty());

            assert!(refs.iter().any(|r| r.contains("HEAD") || r.contains("main") || r.contains("master")));
        }
    }

    #[test]
    fn test_get_head_ref() {
        let current_dir = std::env::current_dir().expect("Failed to get current dir");

        if let Ok(git_root) = find_git_root(current_dir.to_str().unwrap()) {
            let repo = Repository::open(&git_root).expect("Failed to open repo");
            let result = get_head_ref(&repo);

            assert!(result.is_ok());
            let head_ref = result.unwrap();
            assert!(!head_ref.is_empty());
        }
    }

    #[test]
    fn test_get_file_status() {
        let current_dir = std::env::current_dir().expect("Failed to get current dir");

        if let Ok(git_root) = find_git_root(current_dir.to_str().unwrap()) {
            let repo = Repository::open(&git_root).expect("Failed to open repo");

            let result = get_file_status(&repo, "Cargo.toml");

            if result.is_ok() {
                let status = result.unwrap();
                assert!(["clean", "modified", "untracked", "added", "staged", "deleted", "unknown"]
                    .contains(&status.as_str()));
            }
        }
    }

    #[test]
    fn test_get_current_branch_commit_for_file() {
        let current_dir = std::env::current_dir().expect("Failed to get current dir");

        if let Ok(git_root) = find_git_root(current_dir.to_str().unwrap()) {
            let repo = Repository::open(&git_root).expect("Failed to open repo");

            if git_root.join("Cargo.toml").exists() {
                let result = get_current_branch_commit_for_file(&repo, "Cargo.toml");

                assert!(result.is_ok());
                let commit_hash = result.unwrap();
                assert!(!commit_hash.is_empty());
                assert_eq!(commit_hash.len(), 40);
            }
        }
    }

    #[test]
    fn test_get_current_branch_commit_for_nonexistent_file() {
        let current_dir = std::env::current_dir().expect("Failed to get current dir");

        if let Ok(git_root) = find_git_root(current_dir.to_str().unwrap()) {
            let repo = Repository::open(&git_root).expect("Failed to open repo");

            let result = get_current_branch_commit_for_file(&repo, "nonexistent_file_xyz.txt");
            assert!(result.is_err());
            assert!(result.unwrap_err().to_string().contains("File does not exist"));
        }
    }

    #[test]
    fn test_get_file_hash_at_commit() {
        let current_dir = std::env::current_dir().expect("Failed to get current dir");

        if let Ok(git_root) = find_git_root(current_dir.to_str().unwrap()) {
            let repo = Repository::open(&git_root).expect("Failed to open repo");

            let head = repo.head().expect("Failed to get HEAD");
            let head_commit = head.peel_to_commit().expect("Failed to get commit");
            let commit_hash = head_commit.id().to_string();

            if git_root.join("Cargo.toml").exists() {
                let result = get_file_hash_at_commit(&repo, "Cargo.toml", &commit_hash);

                if result.is_ok() {
                    let file_hash = result.unwrap();
                    assert!(!file_hash.is_empty());
                    assert_eq!(file_hash.len(), 40);
                }
            }
        }
    }
}