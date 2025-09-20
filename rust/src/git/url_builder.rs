use anyhow::{Result, anyhow};
use url::Url;
use std::path::Path;

#[derive(Debug, Clone)]
pub struct GitHubInfo {
    pub owner: String,
    pub repo: String,
}

pub fn parse_remote_url(remote_url: &str) -> Result<GitHubInfo> {
    if remote_url.starts_with("git@github.com:") {
        let url_part = remote_url
            .strip_prefix("git@github.com:")
            .ok_or_else(|| anyhow!("Invalid SSH URL format"))?;

        let parts: Vec<&str> = url_part.trim_end_matches(".git").split('/').collect();

        if parts.len() != 2 {
            return Err(anyhow!("Invalid GitHub repository format"));
        }

        Ok(GitHubInfo {
            owner: parts[0].to_string(),
            repo: parts[1].to_string(),
        })
    } else if remote_url.starts_with("https://github.com/") || remote_url.starts_with("http://github.com/") {
        let url = Url::parse(remote_url)?;
        let path_segments: Vec<&str> = url
            .path_segments()
            .ok_or_else(|| anyhow!("Cannot parse URL path"))?
            .collect();

        if path_segments.len() < 2 {
            return Err(anyhow!("Invalid GitHub repository URL"));
        }

        let owner = path_segments[0].to_string();
        let repo = path_segments[1].trim_end_matches(".git").to_string();

        Ok(GitHubInfo { owner, repo })
    } else {
        Err(anyhow!("Unsupported remote URL format: {}", remote_url))
    }
}

pub fn build_github_url(
    github_info: &GitHubInfo,
    commit_hash: &str,
    file_path: &str,
) -> String {
    let normalized_path = normalize_file_path(file_path);
    format!(
        "https://github.com/{}/{}/blob/{}/{}",
        github_info.owner,
        github_info.repo,
        commit_hash,
        normalized_path
    )
}

fn normalize_file_path(file_path: &str) -> String {
    let path = Path::new(file_path);

    let normalized = if path.is_absolute() {
        path.strip_prefix("/").unwrap_or(path)
    } else {
        path
    };

    normalized
        .to_string_lossy()
        .replace('\\', "/")
        .trim_start_matches('/')
        .to_string()
}

pub fn generate_github_url(
    remote_url: &str,
    commit_hash: &str,
    file_path: &str,
) -> Result<String> {
    let github_info = parse_remote_url(remote_url)?;
    Ok(build_github_url(&github_info, commit_hash, file_path))
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_parse_ssh_url() {
        let url = "git@github.com:user/repo.git";
        let info = parse_remote_url(url).unwrap();
        assert_eq!(info.owner, "user");
        assert_eq!(info.repo, "repo");
    }

    #[test]
    fn test_parse_ssh_url_without_git_extension() {
        let url = "git@github.com:owner/repository";
        let info = parse_remote_url(url).unwrap();
        assert_eq!(info.owner, "owner");
        assert_eq!(info.repo, "repository");
    }

    #[test]
    fn test_parse_https_url() {
        let url = "https://github.com/user/repo.git";
        let info = parse_remote_url(url).unwrap();
        assert_eq!(info.owner, "user");
        assert_eq!(info.repo, "repo");
    }

    #[test]
    fn test_parse_http_url() {
        let url = "http://github.com/myuser/myrepo.git";
        let info = parse_remote_url(url).unwrap();
        assert_eq!(info.owner, "myuser");
        assert_eq!(info.repo, "myrepo");
    }

    #[test]
    fn test_parse_invalid_url() {
        let url = "not-a-github-url";
        let result = parse_remote_url(url);
        assert!(result.is_err());
        assert!(result.unwrap_err().to_string().contains("Unsupported remote URL format"));
    }

    #[test]
    fn test_normalize_file_path_absolute() {
        let path = "/src/main.rs";
        let normalized = normalize_file_path(path);
        assert_eq!(normalized, "src/main.rs");
    }

    #[test]
    fn test_normalize_file_path_relative() {
        let path = "src/lib.rs";
        let normalized = normalize_file_path(path);
        assert_eq!(normalized, "src/lib.rs");
    }

    #[test]
    fn test_normalize_file_path_with_backslashes() {
        let path = "src\\windows\\path.rs";
        let normalized = normalize_file_path(path);
        assert_eq!(normalized, "src/windows/path.rs");
    }

    #[test]
    fn test_build_github_url() {
        let info = GitHubInfo {
            owner: "taskforcesh".to_string(),
            repo: "bullmq".to_string(),
        };
        let url = build_github_url(&info, "bd8fbc164caaa01f665d0c7e94177d0584d04f8c", ".gitbook.yaml");
        assert_eq!(
            url,
            "https://github.com/taskforcesh/bullmq/blob/bd8fbc164caaa01f665d0c7e94177d0584d04f8c/.gitbook.yaml"
        );
    }

    #[test]
    fn test_generate_github_url_complete() {
        let remote_url = "git@github.com:rust-lang/rust.git";
        let commit_hash = "abc123def456";
        let file_path = "src/main.rs";

        let url = generate_github_url(remote_url, commit_hash, file_path).unwrap();
        assert_eq!(
            url,
            "https://github.com/rust-lang/rust/blob/abc123def456/src/main.rs"
        );
    }
}