#!/usr/bin/env python3
"""
Commit and push all repositories with changes
"""

import os
import subprocess
import sys

def check_and_push_repo(repo_path, repo_name):
    """Check if repo has changes and push if needed."""
    try:
        # Check if there are uncommitted changes
        status = subprocess.run(['git', 'status', '--porcelain'], 
                              cwd=repo_path, capture_output=True, text=True)
        
        if status.stdout.strip():
            print(f"\n📝 {repo_name}: Has uncommitted changes")
            
            # Add all changes (ignore submodule warnings)
            subprocess.run(['git', 'add', '.'], cwd=repo_path, capture_output=True)
            
            # Commit
            commit_result = subprocess.run(['git', 'commit', '-m', 'Update project files'], 
                                         cwd=repo_path, capture_output=True, text=True)
            
            if commit_result.returncode == 0:
                print(f"   ✓ Committed changes")
            else:
                print(f"   ⚠ Commit failed or nothing to commit")
        
        # Check if we need to push
        push_check = subprocess.run(['git', 'status', '-sb'], 
                                  cwd=repo_path, capture_output=True, text=True)
        
        if 'ahead' in push_check.stdout or not 'origin' in push_check.stdout:
            print(f"   🚀 Pushing to remote...")
            
            # Get current branch
            branch_result = subprocess.run(['git', 'branch', '--show-current'], 
                                         cwd=repo_path, capture_output=True, text=True)
            branch = branch_result.stdout.strip() or 'main'
            
            # Push
            push_result = subprocess.run(['git', 'push', '-u', 'origin', branch], 
                                       cwd=repo_path, capture_output=True, text=True)
            
            if push_result.returncode == 0:
                print(f"   ✓ Pushed successfully")
                return "pushed"
            else:
                print(f"   ❌ Push failed: {push_result.stderr}")
                return "failed"
        else:
            print(f"✓ {repo_name}: Already up to date")
            return "up_to_date"
            
    except Exception as e:
        print(f"❌ {repo_name}: Error - {str(e)}")
        return "error"

def main():
    base_dir = "../"
    
    # List of repos that have SSH remotes (from previous output)
    repos_with_remotes = [
        'PluginsAPIDemo', 'SchwinnBTCapture', 'ags', 'besu', 'blockscout',
        'canton-local', 'circom', 'dumpproxies', 'eth_explorer', 'kurtosis-cdk',
        'pgpool', 'polygon-cli', 'pypoll', 'stark101', 'theLMbook', 'zk-demo',
        'zkp-test', 'music', 'zkp-test-book', 'addr', 'circpl', 'codedoc',
        'llm-queue', 'ppt', 'project-viewer', 'psych', 'ava', 'dynreact',
        'local-rag', 'podman-besu', 'repo_agent', 'sampo', 'sql_gpt'
    ]
    
    print(f"Checking and pushing repositories...\n")
    
    results = {
        'pushed': 0,
        'up_to_date': 0,
        'failed': 0,
        'error': 0
    }
    
    for repo in sorted(repos_with_remotes):
        repo_path = os.path.join(base_dir, repo)
        
        if os.path.exists(repo_path):
            result = check_and_push_repo(repo_path, repo)
            results[result] = results.get(result, 0) + 1
    
    print(f"\n📊 Summary:")
    print(f"   Pushed: {results['pushed']}")
    print(f"   Already up to date: {results['up_to_date']}")
    print(f"   Failed: {results['failed']}")
    print(f"   Errors: {results['error']}")

if __name__ == '__main__':
    main()