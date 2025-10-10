"""
Command-line interface for git-identify.

Provides CLI commands for generating file identifiers and detecting changes.
"""

import argparse
import asyncio
import json
import sys
from pathlib import Path
from typing import Optional

from . import (
    __version__,
    generate_batch_identifiers,
    generate_change_report,
    generate_identifier,
    get_github_metadata,
    get_local_metadata,
    get_repository_info,
    load_manifest,
    save_manifest,
)
from .batch import BatchInput
from .errors import GitError


def main() -> int:
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        prog="git-identify",
        description="Generate unique, deterministic file identifiers from Git metadata"
    )

    parser.add_argument(
        "--version",
        action="version",
        version=f"%(prog)s {__version__}"
    )

    subparsers = parser.add_subparsers(dest="command", help="Command to execute")

    # Local command
    local_parser = subparsers.add_parser(
        "local",
        help="Generate identifier from local Git repository"
    )
    local_parser.add_argument("file", help="File path")
    local_parser.add_argument(
        "--repo",
        default=".",
        help="Repository path (default: current directory)"
    )
    local_parser.add_argument(
        "--algorithm",
        choices=["sha256", "sha1"],
        default="sha256",
        help="Hash algorithm (default: sha256)"
    )
    local_parser.add_argument(
        "--encoding",
        choices=["hex", "base64"],
        default="hex",
        help="Output encoding (default: hex)"
    )
    local_parser.add_argument(
        "--short",
        action="store_true",
        help="Output short identifier only"
    )
    local_parser.add_argument(
        "--json",
        action="store_true",
        help="Output full JSON metadata"
    )

    # GitHub command
    github_parser = subparsers.add_parser(
        "github",
        help="Generate identifier from GitHub API"
    )
    github_parser.add_argument("owner", help="Repository owner")
    github_parser.add_argument("repo", help="Repository name")
    github_parser.add_argument("file", help="File path")
    github_parser.add_argument(
        "--branch",
        default="main",
        help="Branch name (default: main)"
    )
    github_parser.add_argument(
        "--token",
        help="GitHub token (uses GITHUB_TOKEN env var if not provided)"
    )
    github_parser.add_argument(
        "--algorithm",
        choices=["sha256", "sha1"],
        default="sha256",
        help="Hash algorithm (default: sha256)"
    )
    github_parser.add_argument(
        "--encoding",
        choices=["hex", "base64"],
        default="hex",
        help="Output encoding (default: hex)"
    )
    github_parser.add_argument(
        "--short",
        action="store_true",
        help="Output short identifier only"
    )
    github_parser.add_argument(
        "--json",
        action="store_true",
        help="Output full JSON metadata"
    )

    # Batch command
    batch_parser = subparsers.add_parser(
        "batch",
        help="Process multiple files in batch"
    )
    batch_parser.add_argument(
        "input_file",
        help="JSON file with batch inputs"
    )
    batch_parser.add_argument(
        "--output",
        help="Output file for results (default: stdout)"
    )
    batch_parser.add_argument(
        "--concurrency",
        type=int,
        default=10,
        help="Maximum concurrent operations (default: 10)"
    )
    batch_parser.add_argument(
        "--algorithm",
        choices=["sha256", "sha1"],
        default="sha256",
        help="Hash algorithm (default: sha256)"
    )
    batch_parser.add_argument(
        "--progress",
        action="store_true",
        help="Show progress"
    )

    # Diff command
    diff_parser = subparsers.add_parser(
        "diff",
        help="Compare current state with previous manifest"
    )
    diff_parser.add_argument(
        "input_file",
        help="JSON file with batch inputs"
    )
    diff_parser.add_argument(
        "manifest_file",
        help="Previous manifest JSON file"
    )
    diff_parser.add_argument(
        "--output",
        help="Output file for change report (default: stdout)"
    )
    diff_parser.add_argument(
        "--concurrency",
        type=int,
        default=10,
        help="Maximum concurrent operations (default: 10)"
    )

    # Info command
    info_parser = subparsers.add_parser(
        "info",
        help="Get complete repository info for a file"
    )
    info_parser.add_argument("file", help="File path")
    info_parser.add_argument(
        "--repo",
        default=".",
        help="Repository path (default: current directory)"
    )

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return 1

    try:
        if args.command == "local":
            return cmd_local(args)
        elif args.command == "github":
            return cmd_github(args)
        elif args.command == "batch":
            return asyncio.run(cmd_batch(args))
        elif args.command == "diff":
            return asyncio.run(cmd_diff(args))
        elif args.command == "info":
            return cmd_info(args)
        else:
            parser.print_help()
            return 1

    except GitError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"Unexpected error: {e}", file=sys.stderr)
        return 2


def cmd_local(args: argparse.Namespace) -> int:
    """Handle local command."""
    metadata = get_local_metadata(args.repo, args.file)
    result = generate_identifier(
        metadata,
        algorithm=args.algorithm,
        encoding=args.encoding
    )

    if args.json:
        output = {
            "identifier": result.identifier,
            "short": result.short,
            "algorithm": result.algorithm,
            "metadata": metadata
        }
        print(json.dumps(output, indent=2))
    elif args.short:
        print(result.short)
    else:
        print(result.identifier)

    return 0


def cmd_github(args: argparse.Namespace) -> int:
    """Handle github command."""
    metadata = get_github_metadata(
        args.owner,
        args.repo,
        args.file,
        args.branch,
        args.token
    )
    result = generate_identifier(
        metadata,
        algorithm=args.algorithm,
        encoding=args.encoding
    )

    if args.json:
        output = {
            "identifier": result.identifier,
            "short": result.short,
            "algorithm": result.algorithm,
            "metadata": metadata
        }
        print(json.dumps(output, indent=2))
    elif args.short:
        print(result.short)
    else:
        print(result.identifier)

    return 0


async def cmd_batch(args: argparse.Namespace) -> int:
    """Handle batch command."""
    # Read input file
    with open(args.input_file, "r") as f:
        inputs_data = json.load(f)

    if not isinstance(inputs_data, list):
        print("Error: Input file must contain a JSON array", file=sys.stderr)
        return 1

    # Progress callback
    def progress_callback(done: int, total: int) -> None:
        if args.progress:
            print(f"Progress: {done}/{total}", file=sys.stderr)

    # Process batch
    results = await generate_batch_identifiers(
        inputs_data,
        concurrency=args.concurrency,
        algorithm=args.algorithm,
        progress_callback=progress_callback if args.progress else None
    )

    # Convert to dict format
    output = [r.to_dict() for r in results]

    # Write output
    output_json = json.dumps(output, indent=2)
    if args.output:
        with open(args.output, "w") as f:
            f.write(output_json)
    else:
        print(output_json)

    return 0


async def cmd_diff(args: argparse.Namespace) -> int:
    """Handle diff command."""
    # Read input file
    with open(args.input_file, "r") as f:
        inputs_data = json.load(f)

    # Read manifest file
    with open(args.manifest_file, "r") as f:
        manifest_json = f.read()
    previous_manifest = load_manifest(manifest_json)

    # Process batch
    results = await generate_batch_identifiers(
        inputs_data,
        concurrency=args.concurrency
    )

    # Generate change report
    report = generate_change_report(results, previous_manifest)

    # Write output
    output = report.to_dict()
    output_json = json.dumps(output, indent=2)

    if args.output:
        with open(args.output, "w") as f:
            f.write(output_json)
    else:
        print(output_json)

    # Print summary to stderr
    print(f"\nSummary:", file=sys.stderr)
    print(f"  Added: {len(report.added)}", file=sys.stderr)
    print(f"  Modified: {len(report.modified)}", file=sys.stderr)
    print(f"  Unchanged: {len(report.unchanged)}", file=sys.stderr)
    print(f"  Removed: {len(report.removed)}", file=sys.stderr)
    print(f"  Errors: {len(report.errors)}", file=sys.stderr)

    return 0


def cmd_info(args: argparse.Namespace) -> int:
    """Handle info command."""
    info = get_repository_info(args.file, args.repo)
    print(json.dumps(info, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
