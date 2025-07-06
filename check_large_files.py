#!/usr/bin/env python3
"""
Check for large files in a git repository that might cause push issues
"""

import os
import sys
import subprocess

def format_size(bytes):
    """Format bytes to human readable size."""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if bytes < 1024.0:
            return f"{bytes:.2f} {unit}"
        bytes /= 1024.0
    return f"{bytes:.2f} TB"

def check_large_files(repo_path, size_limit_mb=50):
    """Check for files larger than size_limit_mb."""
    large_files = []
    
    # Get all tracked files
    result = subprocess.run(['git', 'ls-files'], 
                          cwd=repo_path, 
                          capture_output=True, 
                          text=True)
    
    if result.returncode != 0:
        print(f"Error: Not a git repository or git command failed")
        return []
    
    files = result.stdout.strip().split('\n')
    
    for file in files:
        if not file:
            continue
            
        file_path = os.path.join(repo_path, file)
        if os.path.exists(file_path) and os.path.isfile(file_path):
            size = os.path.getsize(file_path)
            size_mb = size / (1024 * 1024)
            
            if size_mb > size_limit_mb:
                large_files.append({
                    'path': file,
                    'size': size,
                    'size_formatted': format_size(size)
                })
    
    return large_files

def main():
    if len(sys.argv) < 2:
        print("Usage: python check_large_files.py <repo_path> [size_limit_mb]")
        sys.exit(1)
    
    repo_path = sys.argv[1]
    size_limit_mb = int(sys.argv[2]) if len(sys.argv) > 2 else 50
    
    print(f"Checking for files larger than {size_limit_mb} MB in {repo_path}...")
    
    large_files = check_large_files(repo_path, size_limit_mb)
    
    if large_files:
        print(f"\nFound {len(large_files)} large file(s):")
        print("-" * 60)
        for file in sorted(large_files, key=lambda x: x['size'], reverse=True):
            print(f"{file['size_formatted']:>10} | {file['path']}")
        print("-" * 60)
        print("\nThese files may cause issues when pushing to GitHub.")
        print("Consider:")
        print("1. Adding them to .gitignore if they shouldn't be tracked")
        print("2. Using Git LFS for large files that need to be tracked")
        print("3. Removing them from git history with 'git rm --cached <file>'")
    else:
        print(f"No files larger than {size_limit_mb} MB found.")

if __name__ == '__main__':
    main()