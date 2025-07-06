#!/usr/bin/env python3
"""
Standalone script to link a local project to an existing GitHub repository
"""

import sys
import os
import subprocess

def link_to_github(project_path, repo_name):
    """Link local project to existing GitHub repo and push."""
    
    # Get GitHub username
    user_result = subprocess.run(['gh', 'api', 'user', '-q', '.login'], 
                               capture_output=True, text=True)
    if user_result.returncode != 0:
        print("Error: Could not get GitHub username. Make sure 'gh' is authenticated.")
        return False
    
    username = user_result.stdout.strip()
    print(f"GitHub username: {username}")
    
    # Initialize git if needed
    if not os.path.exists(os.path.join(project_path, '.git')):
        print("Initializing git repository...")
        subprocess.run(['git', 'init'], cwd=project_path)
        subprocess.run(['git', 'add', '.'], cwd=project_path)
        subprocess.run(['git', 'commit', '-m', 'Initial commit'], cwd=project_path)
    
    # Check current remote
    remote_result = subprocess.run(['git', 'remote', 'get-url', 'origin'], 
                                 cwd=project_path, capture_output=True, text=True)
    
    if remote_result.returncode == 0:
        print(f"Remote already exists: {remote_result.stdout.strip()}")
        # Remove existing remote
        subprocess.run(['git', 'remote', 'remove', 'origin'], cwd=project_path)
    
    # Add new remote
    remote_url = f'https://github.com/{username}/{repo_name}.git'
    print(f"Adding remote: {remote_url}")
    subprocess.run(['git', 'remote', 'add', 'origin', remote_url], cwd=project_path)
    
    # Get current branch
    branch_result = subprocess.run(['git', 'branch', '--show-current'], 
                                 cwd=project_path, capture_output=True, text=True)
    branch = branch_result.stdout.strip() or 'master'
    print(f"Current branch: {branch}")
    
    # Force push to overwrite remote
    print(f"Pushing to origin/{branch}...")
    push_result = subprocess.run(['git', 'push', '-u', 'origin', branch, '--force'], 
                               cwd=project_path, capture_output=True, text=True)
    
    if push_result.returncode == 0:
        print("Successfully pushed to GitHub!")
        return True
    else:
        print(f"Push failed: {push_result.stderr}")
        return False

if __name__ == '__main__':
    if len(sys.argv) != 3:
        print("Usage: python link_github.py <project_path> <repo_name>")
        sys.exit(1)
    
    project_path = sys.argv[1]
    repo_name = sys.argv[2]
    
    if not os.path.exists(project_path):
        print(f"Error: Project path '{project_path}' does not exist")
        sys.exit(1)
    
    success = link_to_github(project_path, repo_name)
    sys.exit(0 if success else 1)