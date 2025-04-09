#!/usr/bin/env python3
"""
Release script for Draw Things gRPCServer Installer.
Handles version bumping and GitHub release creation.
"""

import argparse
import os
import re
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import List, Optional, Tuple

def get_current_version() -> Tuple[int, int, int]:
    """Get the current version from the latest git tag."""
    try:
        result = subprocess.run(['git', 'describe', '--tags', '--abbrev=0'],
                              capture_output=True, text=True, check=True)
        version = result.stdout.strip().lstrip('v')
        major, minor, patch = map(int, version.split('.'))
        return major, minor, patch
    except subprocess.CalledProcessError:
        return 0, 0, 0

def bump_version(current: Tuple[int, int, int], bump_type: str) -> Tuple[int, int, int]:
    """Bump the version number based on the bump type."""
    major, minor, patch = current
    if bump_type == 'major':
        return major + 1, 0, 0
    elif bump_type == 'minor':
        return major, minor + 1, 0
    else:  # patch
        return major, minor, patch + 1

def get_changes_since_last_tag() -> List[str]:
    """Get a list of commit messages since the last tag."""
    try:
        # Get the last tag
        last_tag = subprocess.run(['git', 'describe', '--tags', '--abbrev=0'],
                                capture_output=True, text=True, check=True)

        # Get commits since last tag
        result = subprocess.run(['git', 'log', f'{last_tag.stdout.strip()}..HEAD', '--pretty=format:%s'],
                              capture_output=True, text=True, check=True)
        return [line for line in result.stdout.split('\n') if line.strip()]
    except subprocess.CalledProcessError:
        # If no tags exist, get all commits
        result = subprocess.run(['git', 'log', '--pretty=format:%s'],
                              capture_output=True, text=True, check=True)
        return [line for line in result.stdout.split('\n') if line.strip()]

def categorize_changes(changes: List[str]) -> dict:
    """Categorize changes based on conventional commit prefixes."""
    categories = {
        'Features': [],
        'Bug Fixes': [],
        'Documentation': [],
        'Other': []
    }

    for change in changes:
        if change.startswith(('feat', 'feature')):
            categories['Features'].append(change)
        elif change.startswith(('fix', 'bug')):
            categories['Bug Fixes'].append(change)
        elif change.startswith(('docs', 'doc')):
            categories['Documentation'].append(change)
        else:
            categories['Other'].append(change)

    return categories

def generate_release_notes(version: str, changes: dict) -> str:
    """Generate formatted release notes."""
    date = datetime.now().strftime('%Y-%m-%d')
    notes = [
        f"# Draw Things gRPCServer Installer {version}",
        "",
        f"Release Date: {date}",
        "",
        "## Changes",
        ""
    ]

    for category, items in changes.items():
        if items:
            notes.append(f"### {category}")
            notes.extend([f"- {item}" for item in items])
            notes.append("")

    notes.extend([
        "## Installation",
        "",
        "```bash",
        "# Clone the repository",
        "git clone https://github.com/funkatron/draw-things-grpcservercli-installer.git",
        "",
        "# Make the script executable",
        "chmod +x grpc_server_installer.py",
        "",
        "# Run the installer",
        "./grpc_server_installer.py",
        "```",
        ""
    ])

    return '\n'.join(notes)

def create_github_release(version: str, notes: str):
    """Create a GitHub release using gh CLI."""
    # Write release notes to temporary file
    notes_file = Path('RELEASE.md')
    notes_file.write_text(notes)

    try:
        # Create and push tag
        subprocess.run(['git', 'tag', '-a', version, '-m', f"Release {version}"], check=True)
        subprocess.run(['git', 'push', 'origin', version], check=True)

        # Create GitHub release
        subprocess.run(['gh', 'release', 'create', version,
                       '--title', f"Draw Things gRPCServer Installer {version}",
                       '--notes-file', 'RELEASE.md'], check=True)
    finally:
        # Clean up temporary file
        notes_file.unlink()

def main():
    parser = argparse.ArgumentParser(description='Create a new release of Draw Things gRPCServer Installer')
    parser.add_argument('bump', choices=['major', 'minor', 'patch'],
                       help='Version number to bump (major.minor.patch)')
    parser.add_argument('--dry-run', action='store_true',
                       help='Show what would be done without making changes')
    args = parser.parse_args()

    # Check if git is clean
    result = subprocess.run(['git', 'status', '--porcelain'],
                          capture_output=True, text=True, check=True)
    if result.stdout.strip():
        print("Error: Working directory is not clean. Commit or stash changes first.")
        sys.exit(1)

    # Get current and new versions
    current_version = get_current_version()
    new_version = bump_version(current_version, args.bump)
    version_str = f"v{'.'.join(map(str, new_version))}"

    # Get and categorize changes
    changes = get_changes_since_last_tag()
    categorized_changes = categorize_changes(changes)

    # Generate release notes
    release_notes = generate_release_notes(version_str, categorized_changes)

    if args.dry_run:
        print(f"\nWould create release {version_str} with these notes:\n")
        print(release_notes)
        return

    # Create GitHub release
    print(f"\nCreating release {version_str}...")
    create_github_release(version_str, release_notes)
    print(f"\nRelease {version_str} created successfully!")

    # Make installer executable and test it
    commands = [
        "chmod +x grpc_server_installer.py",
        "python3 -m pytest tests/",
        "./grpc_server_installer.py",
    ]

if __name__ == '__main__':
    main()