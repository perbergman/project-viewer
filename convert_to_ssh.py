#!/usr/bin/env python3
"""
Convert all git repositories from HTTPS to SSH URLs
"""

import os
import subprocess
import sys

def convert_to_ssh(repo_path):
    """Convert a repository's remote URL from HTTPS to SSH."""
    try:
        # Get current remote URL
        result = subprocess.run(['git', 'remote', 'get-url', 'origin'], 
                              cwd=repo_path, capture_output=True, text=True)
        
        if result.returncode != 0:
            return None, "No remote found"
        
        current_url = result.stdout.strip()
        
        # Check if it's already SSH
        if current_url.startswith('git@'):
            return current_url, "Already using SSH"
        
        # Convert HTTPS to SSH
        if 'github.com' in current_url:
            # https://github.com/user/repo.git -> git@github.com:user/repo.git
            ssh_url = current_url.replace('https://github.com/', 'git@github.com:')
            
            # Set the new URL
            subprocess.run(['git', 'remote', 'set-url', 'origin', ssh_url], 
                         cwd=repo_path, check=True)
            
            return ssh_url, "Converted to SSH"
        else:
            return current_url, "Not a GitHub URL"
            
    except Exception as e:
        return None, f"Error: {str(e)}"

def main():
    if len(sys.argv) > 1:
        base_dir = sys.argv[1]
    else:
        base_dir = os.path.expanduser("~/Documents/dev")
    
    print(f"Converting repositories in {base_dir} to use SSH...\n")
    
    converted = 0
    already_ssh = 0
    no_remote = 0
    errors = 0
    
    for item in sorted(os.listdir(base_dir)):
        item_path = os.path.join(base_dir, item)
        
        if os.path.isdir(item_path) and not item.startswith('.'):
            git_dir = os.path.join(item_path, '.git')
            
            if os.path.exists(git_dir):
                url, status = convert_to_ssh(item_path)
                
                if status == "Converted to SSH":
                    print(f"✓ {item}: {url}")
                    converted += 1
                elif status == "Already using SSH":
                    already_ssh += 1
                elif status == "No remote found":
                    no_remote += 1
                else:
                    print(f"✗ {item}: {status}")
                    errors += 1
    
    print(f"\nSummary:")
    print(f"  Converted to SSH: {converted}")
    print(f"  Already using SSH: {already_ssh}")
    print(f"  No remote: {no_remote}")
    print(f"  Errors: {errors}")

if __name__ == '__main__':
    main()