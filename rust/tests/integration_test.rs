#[cfg(not(target_arch = "wasm32"))]
use git_identify::{GitFileId, generate_github_url_direct};
use std::env;

#[test]
#[cfg(not(target_arch = "wasm32"))]
fn test_git_file_id_initialization() {
    let mut git_file_id = GitFileId::new_native();

    let current_dir = env::current_dir().expect("Failed to get current directory");
    let test_file = current_dir.to_str().unwrap();

    match git_file_id.find_repository(test_file) {
        Ok(_) => {
            println!("Successfully found repository");

            // Test getting HEAD reference
            match git_file_id.get_head_ref() {
                Ok(head) => println!("HEAD ref: {}", head),
                Err(e) => println!("Error getting HEAD ref: {:?}", e),
            }

            // Test listing refs
            match git_file_id.list_refs_native() {
                Ok(refs) => println!("Found {} refs", refs.len()),
                Err(e) => println!("Error listing refs: {}", e),
            }
        }
        Err(e) => {
            println!("Could not find repository: {:?}", e);
            // This is expected if the test is not run in a git repository
        }
    }
}

#[test]
#[cfg(not(target_arch = "wasm32"))]
fn test_github_url_generation() {
    let current_dir = env::current_dir().expect("Failed to get current directory");

    // Try to find a file in the current directory
    let test_file = current_dir.join("Cargo.toml");

    if test_file.exists() {
        let test_path = test_file.to_str().unwrap();

        match generate_github_url_direct(test_path) {
            Ok(url) => {
                println!("Generated GitHub URL: {}", url);
                assert!(url.starts_with("https://github.com/"));
                assert!(url.contains("/blob/"));
            }
            Err(e) => {
                println!("Could not generate URL: {:?}", e);
                // This is expected if there's no git repository or no origin remote
            }
        }
    } else {
        println!("Test file does not exist, skipping URL generation test");
    }
}

#[test]
#[cfg(not(target_arch = "wasm32"))]
fn test_file_status() {
    let mut git_file_id = GitFileId::new_native();
    let current_dir = env::current_dir().expect("Failed to get current directory");

    if git_file_id.find_repository(current_dir.to_str().unwrap()).is_ok() {
        // Test with Cargo.toml if it exists
        let cargo_toml = "Cargo.toml";
        match git_file_id.get_file_status(cargo_toml) {
            Ok(status) => {
                println!("File status for {}: {}", cargo_toml, status);
                assert!(["clean", "modified", "untracked", "added", "staged", "deleted", "unknown"]
                    .contains(&status.as_str()));
            }
            Err(e) => println!("Error getting file status: {:?}", e),
        }
    }
}

#[test]
#[cfg(not(target_arch = "wasm32"))]
fn test_repository_discovery() {
    use git_identify::git::repository::find_git_root;

    let current_dir = env::current_dir().expect("Failed to get current directory");

    match find_git_root(current_dir.to_str().unwrap()) {
        Ok(git_root) => {
            println!("Found git root: {:?}", git_root);
            assert!(git_root.join(".git").exists());
        }
        Err(e) => {
            println!("No git repository found: {}", e);
            // This is expected when running outside a git repository
        }
    }
}

#[test]
#[cfg(not(target_arch = "wasm32"))]
fn test_url_parsing() {
    use git_identify::git::url_builder::parse_remote_url;

    // Test SSH format
    let ssh_url = "git@github.com:owner/repo.git";
    let result = parse_remote_url(ssh_url).expect("Failed to parse SSH URL");
    assert_eq!(result.owner, "owner");
    assert_eq!(result.repo, "repo");

    // Test HTTPS format
    let https_url = "https://github.com/owner/repo.git";
    let result = parse_remote_url(https_url).expect("Failed to parse HTTPS URL");
    assert_eq!(result.owner, "owner");
    assert_eq!(result.repo, "repo");

    // Test invalid URL
    let invalid_url = "not-a-github-url";
    assert!(parse_remote_url(invalid_url).is_err());
}

#[test]
#[cfg(not(target_arch = "wasm32"))]
fn test_git_objects() {
    let mut git_file_id = GitFileId::new_native();
    let current_dir = env::current_dir().expect("Failed to get current directory");

    if git_file_id.find_repository(current_dir.to_str().unwrap()).is_ok() {
        // Try to get HEAD commit
        match git_file_id.get_head_ref() {
            Ok(head_ref) => {
                println!("HEAD reference: {}", head_ref);

                // If HEAD is a commit hash (detached HEAD), try to get the commit
                if head_ref.len() == 40 {
                    match git_file_id.get_commit(&head_ref) {
                        Ok(commit) => {
                            println!("Commit ID: {}", commit.id());
                            println!("Commit message: {}", commit.message());
                            println!("Author: {} <{}>", commit.author_name(), commit.author_email());
                            println!("Tree ID: {}", commit.tree_id());
                        }
                        Err(e) => println!("Error getting commit: {:?}", e),
                    }
                }
            }
            Err(e) => println!("Error getting HEAD: {:?}", e),
        }
    }
}