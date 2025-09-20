pub mod git;

use wasm_bindgen::prelude::*;
use std::path::PathBuf;

#[cfg(not(target_arch = "wasm32"))]
use git2::Repository;

#[wasm_bindgen]
extern "C" {
    #[wasm_bindgen(js_namespace = console)]
    fn log(s: &str);
}

macro_rules! console_log {
    ($($t:tt)*) => (log(&format_args!($($t)*).to_string()))
}

#[wasm_bindgen]
pub struct GitFileId {
    #[allow(dead_code)]
    repo_path: Option<PathBuf>,
}

#[wasm_bindgen]
impl GitFileId {
    #[wasm_bindgen(constructor)]
    pub fn new() -> Self {
        #[cfg(target_arch = "wasm32")]
        console_log!("GitFileId initialized");
        GitFileId { repo_path: None }
    }

    #[cfg(not(target_arch = "wasm32"))]
    pub fn new_native() -> Self {
        GitFileId { repo_path: None }
    }

    #[wasm_bindgen]
    pub fn find_repository(&mut self, _file_path: &str) -> Result<(), JsValue> {
        #[cfg(not(target_arch = "wasm32"))]
        {
            match git::repository::find_git_root(_file_path) {
                Ok(path) => {
                    self.repo_path = Some(path);
                    Ok(())
                }
                Err(e) => Err(JsValue::from_str(&e.to_string()))
            }
        }
        #[cfg(target_arch = "wasm32")]
        {
            Err(JsValue::from_str("Git operations are not available in WASM environment"))
        }
    }

    #[wasm_bindgen]
    pub fn generate_github_url(&self, _file_path: &str) -> Result<String, JsValue> {
        #[cfg(not(target_arch = "wasm32"))]
        {
            let repo_path = self.repo_path.as_ref()
                .ok_or_else(|| JsValue::from_str("Repository not found. Call find_repository first."))?;

            let repo = Repository::open(repo_path)
                .map_err(|e| JsValue::from_str(&e.to_string()))?;

            let remote_url = git::repository::get_remote_url(&repo)
                .map_err(|e| JsValue::from_str(&e.to_string()))?;

            let commit_hash = git::repository::get_current_branch_commit_for_file(&repo, _file_path)
                .map_err(|e| JsValue::from_str(&e.to_string()))?;

            let relative_path = PathBuf::from(_file_path)
                .strip_prefix(repo_path)
                .unwrap_or(&PathBuf::from(_file_path))
                .to_string_lossy()
                .to_string();

            git::url_builder::generate_github_url(&remote_url, &commit_hash, &relative_path)
                .map_err(|e| JsValue::from_str(&e.to_string()))
        }
        #[cfg(target_arch = "wasm32")]
        {
            Err(JsValue::from_str("Git operations are not available in WASM environment"))
        }
    }

    #[wasm_bindgen]
    pub fn get_file_hash(&self, file_path: &str) -> Result<String, JsValue> {
        #[cfg(not(target_arch = "wasm32"))]
        {
            let repo_path = self.repo_path.as_ref()
                .ok_or_else(|| JsValue::from_str("Repository not found. Call find_repository first."))?;

            let repo = Repository::open(repo_path)
                .map_err(|e| JsValue::from_str(&e.to_string()))?;

            git::repository::get_current_branch_commit_for_file(&repo, file_path)
                .map_err(|e| JsValue::from_str(&e.to_string()))
        }
        #[cfg(target_arch = "wasm32")]
        {
            let _ = file_path;
            Err(JsValue::from_str("Git operations are not available in WASM environment"))
        }
    }

    #[wasm_bindgen]
    pub fn get_blob(&self, hash: &str) -> Result<git::objects::GitBlob, JsValue> {
        #[cfg(not(target_arch = "wasm32"))]
        {
            let repo_path = self.repo_path.as_ref()
                .ok_or_else(|| JsValue::from_str("Repository not found. Call find_repository first."))?;

            let repo = Repository::open(repo_path)
                .map_err(|e| JsValue::from_str(&e.to_string()))?;

            git::objects::get_blob(&repo, hash)
                .map_err(|e| JsValue::from_str(&e.to_string()))
        }
        #[cfg(target_arch = "wasm32")]
        {
            let _ = hash;
            Err(JsValue::from_str("Git operations are not available in WASM environment"))
        }
    }

    #[wasm_bindgen]
    pub fn get_tree(&self, hash: &str) -> Result<git::objects::GitTree, JsValue> {
        #[cfg(not(target_arch = "wasm32"))]
        {
            let repo_path = self.repo_path.as_ref()
                .ok_or_else(|| JsValue::from_str("Repository not found. Call find_repository first."))?;

            let repo = Repository::open(repo_path)
                .map_err(|e| JsValue::from_str(&e.to_string()))?;

            git::objects::get_tree(&repo, hash)
                .map_err(|e| JsValue::from_str(&e.to_string()))
        }
        #[cfg(target_arch = "wasm32")]
        {
            let _ = hash;
            Err(JsValue::from_str("Git operations are not available in WASM environment"))
        }
    }

    #[wasm_bindgen]
    pub fn get_commit(&self, hash: &str) -> Result<git::objects::GitCommit, JsValue> {
        #[cfg(not(target_arch = "wasm32"))]
        {
            let repo_path = self.repo_path.as_ref()
                .ok_or_else(|| JsValue::from_str("Repository not found. Call find_repository first."))?;

            let repo = Repository::open(repo_path)
                .map_err(|e| JsValue::from_str(&e.to_string()))?;

            git::objects::get_commit(&repo, hash)
                .map_err(|e| JsValue::from_str(&e.to_string()))
        }
        #[cfg(target_arch = "wasm32")]
        {
            let _ = hash;
            Err(JsValue::from_str("Git operations are not available in WASM environment"))
        }
    }

    #[wasm_bindgen]
    pub fn get_tag(&self, hash: &str) -> Result<git::objects::GitTag, JsValue> {
        #[cfg(not(target_arch = "wasm32"))]
        {
            let repo_path = self.repo_path.as_ref()
                .ok_or_else(|| JsValue::from_str("Repository not found. Call find_repository first."))?;

            let repo = Repository::open(repo_path)
                .map_err(|e| JsValue::from_str(&e.to_string()))?;

            git::objects::get_tag(&repo, hash)
                .map_err(|e| JsValue::from_str(&e.to_string()))
        }
        #[cfg(target_arch = "wasm32")]
        {
            let _ = hash;
            Err(JsValue::from_str("Git operations are not available in WASM environment"))
        }
    }

    #[wasm_bindgen]
    pub fn list_refs(&self) -> Result<Vec<JsValue>, JsValue> {
        #[cfg(not(target_arch = "wasm32"))]
        {
            let repo_path = self.repo_path.as_ref()
                .ok_or_else(|| JsValue::from_str("Repository not found. Call find_repository first."))?;

            let repo = Repository::open(repo_path)
                .map_err(|e| JsValue::from_str(&e.to_string()))?;

            let refs = git::repository::list_refs(&repo)
                .map_err(|e| JsValue::from_str(&e.to_string()))?;

            Ok(refs.into_iter().map(JsValue::from).collect())
        }
        #[cfg(target_arch = "wasm32")]
        {
            Err(JsValue::from_str("Git operations are not available in WASM environment"))
        }
    }

    #[cfg(not(target_arch = "wasm32"))]
    pub fn list_refs_native(&self) -> Result<Vec<String>, String> {
        let repo_path = self.repo_path.as_ref()
            .ok_or_else(|| "Repository not found. Call find_repository first.".to_string())?;

        let repo = Repository::open(repo_path)
            .map_err(|e| e.to_string())?;

        git::repository::list_refs(&repo)
            .map_err(|e| e.to_string())
    }

    #[wasm_bindgen]
    pub fn get_file_status(&self, file_path: &str) -> Result<String, JsValue> {
        #[cfg(not(target_arch = "wasm32"))]
        {
            let repo_path = self.repo_path.as_ref()
                .ok_or_else(|| JsValue::from_str("Repository not found. Call find_repository first."))?;

            let repo = Repository::open(repo_path)
                .map_err(|e| JsValue::from_str(&e.to_string()))?;

            git::repository::get_file_status(&repo, file_path)
                .map_err(|e| JsValue::from_str(&e.to_string()))
        }
        #[cfg(target_arch = "wasm32")]
        {
            let _ = file_path;
            Err(JsValue::from_str("Git operations are not available in WASM environment"))
        }
    }

    #[wasm_bindgen]
    pub fn get_head_ref(&self) -> Result<String, JsValue> {
        #[cfg(not(target_arch = "wasm32"))]
        {
            let repo_path = self.repo_path.as_ref()
                .ok_or_else(|| JsValue::from_str("Repository not found. Call find_repository first."))?;

            let repo = Repository::open(repo_path)
                .map_err(|e| JsValue::from_str(&e.to_string()))?;

            git::repository::get_head_ref(&repo)
                .map_err(|e| JsValue::from_str(&e.to_string()))
        }
        #[cfg(target_arch = "wasm32")]
        {
            Err(JsValue::from_str("Git operations are not available in WASM environment"))
        }
    }
}

#[wasm_bindgen]
pub fn generate_github_url_direct(file_path: &str) -> Result<String, JsValue> {
    #[cfg(not(target_arch = "wasm32"))]
    {
        let git_root = git::repository::find_git_root(file_path)
            .map_err(|e| JsValue::from_str(&e.to_string()))?;

        let repo = Repository::open(&git_root)
            .map_err(|e| JsValue::from_str(&e.to_string()))?;

        let remote_url = git::repository::get_remote_url(&repo)
            .map_err(|e| JsValue::from_str(&e.to_string()))?;

        let commit_hash = git::repository::get_current_branch_commit_for_file(&repo, file_path)
            .map_err(|e| JsValue::from_str(&e.to_string()))?;

        let relative_path = PathBuf::from(file_path)
            .strip_prefix(&git_root)
            .unwrap_or(&PathBuf::from(file_path))
            .to_string_lossy()
            .to_string();

        git::url_builder::generate_github_url(&remote_url, &commit_hash, &relative_path)
            .map_err(|e| JsValue::from_str(&e.to_string()))
    }
    #[cfg(target_arch = "wasm32")]
    {
        let _ = file_path;
        Err(JsValue::from_str("Git operations are not available in WASM environment"))
    }
}

#[cfg(all(test, not(target_arch = "wasm32")))]
mod tests {
    use super::*;

    #[test]
    fn test_git_file_id_creation() {
        let git_file_id = GitFileId {
            repo_path: None
        };
        assert!(git_file_id.repo_path.is_none());
    }

    #[test]
    fn test_git_file_id_with_path() {
        let git_file_id = GitFileId {
            repo_path: Some(PathBuf::from("/test/path"))
        };
        assert!(git_file_id.repo_path.is_some());
        assert_eq!(git_file_id.repo_path.unwrap(), PathBuf::from("/test/path"));
    }
}