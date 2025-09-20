#!/usr/bin/env python3
"""Example usage of git_identify Python module."""

from pathlib import Path
from git_identify import GitFileId, generate_github_url_direct


def main():
    print("Git Identify Python Module - Example Usage\n")
    print("=" * 50)

    # Example 1: Direct URL generation
    print("\n1. Direct GitHub URL Generation:")
    try:
        current_file = __file__
        url = generate_github_url_direct(current_file)
        print(f"   File: {current_file}")
        print(f"   URL:  {url}")
    except ValueError as e:
        print(f"   Error: {e}")

    # Example 2: Using GitFileId instance
    print("\n2. Using GitFileId Instance:")
    git_id = GitFileId()

    try:
        # Find repository
        git_id.find_repository(str(Path.cwd()))
        print(f"   Repository found: {git_id.repo_path}")

        # Get HEAD reference
        head = git_id.get_head_ref()
        print(f"   Current HEAD: {head}")

        # List references (first 5)
        refs = git_id.list_refs()
        print(f"   Total references: {len(refs)}")
        for ref in refs[:5]:
            print(f"     - {ref}")

        # Check file status
        test_files = ["README.md", "setup.py", "pyproject.toml"]
        print("\n   File Status:")
        for file in test_files:
            if (Path.cwd() / file).exists():
                status = git_id.get_file_status(file)
                print(f"     - {file}: {status}")

        # Generate URL for README.md if it exists
        if (Path.cwd() / "README.md").exists():
            url = git_id.generate_github_url("README.md")
            print(f"\n   README.md URL: {url}")

    except ValueError as e:
        print(f"   Error: {e}")

    # Example 3: URL parsing
    print("\n3. URL Parsing Examples:")
    from git_identify import parse_remote_url

    test_urls = [
        "git@github.com:owner/repo.git",
        "https://github.com/owner/repo.git",
        "http://github.com/owner/repo",
    ]

    for url in test_urls:
        try:
            info = parse_remote_url(url)
            print(f"   {url}")
            print(f"     -> Owner: {info.owner}, Repo: {info.repo}")
        except ValueError as e:
            print(f"   {url} -> Error: {e}")

    print("\n" + "=" * 50)
    print("Example complete!")


if __name__ == "__main__":
    main()