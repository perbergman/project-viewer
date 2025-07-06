#!/usr/bin/env python3
"""
Project Viewer - Web application for viewing and managing code projects
"""

from flask import Flask, render_template, jsonify, request, send_from_directory
import os
import json
import subprocess
import datetime
import glob
from pathlib import Path
import mimetypes

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-here'
app.config['JSON_SORT_KEYS'] = False

# Configuration
PROJECTS_DIR = os.path.expanduser("~/Documents/dev")
ANNOTATIONS_FILE = "project_annotations.json"

def load_annotations():
    """Load project annotations from JSON file."""
    if os.path.exists(ANNOTATIONS_FILE):
        with open(ANNOTATIONS_FILE, 'r') as f:
            return json.load(f)
    return {}

def save_annotations(annotations):
    """Save project annotations to JSON file."""
    with open(ANNOTATIONS_FILE, 'w') as f:
        json.dump(annotations, f, indent=2)

def load_project_metadata(project_path):
    """Load project-specific metadata from .project-meta.json file."""
    meta_file = os.path.join(project_path, '.project-meta.json')
    if os.path.exists(meta_file):
        try:
            with open(meta_file, 'r') as f:
                return json.load(f)
        except:
            pass
    return {}

def scan_project(project_path):
    """Analyze a single project directory."""
    project_name = os.path.basename(project_path)
    
    # Detect project type
    project_type = "Unknown"
    if os.path.exists(os.path.join(project_path, "package.json")):
        project_type = "JavaScript/Node.js"
    elif os.path.exists(os.path.join(project_path, "pom.xml")):
        project_type = "Java (Maven)"
    elif os.path.exists(os.path.join(project_path, "build.gradle")):
        project_type = "Java/Kotlin (Gradle)"
    elif os.path.exists(os.path.join(project_path, "go.mod")):
        project_type = "Go"
    elif os.path.exists(os.path.join(project_path, "Cargo.toml")):
        project_type = "Rust"
    elif os.path.exists(os.path.join(project_path, "requirements.txt")) or glob.glob(os.path.join(project_path, "*.py")):
        project_type = "Python" 
    elif os.path.exists(os.path.join(project_path, "Dockerfile")):
        project_type = "Docker"
    
    # Detect primary language
    language = "Unknown"
    ext_counts = {}
    lang_map = {
        ".js": "JavaScript", ".ts": "TypeScript", ".py": "Python",
        ".java": "Java", ".kt": "Kotlin", ".go": "Go",
        ".rs": "Rust", ".swift": "Swift", ".m": "Objective-C",
        ".pl": "Prolog", ".pro": "Prolog", ".P": "Prolog",
        ".sol": "Solidity", ".vy": "Vyper", ".circom": "Circom",
        ".rb": "Ruby", ".php": "PHP", ".c": "C", ".cpp": "C++",
        ".cs": "C#", ".lua": "Lua", ".r": "R", ".scala": "Scala",
        ".clj": "Clojure", ".ex": "Elixir", ".dart": "Dart",
        ".nim": "Nim", ".zig": "Zig", ".v": "V"
    }
    
    for root, _, files in os.walk(project_path):
        # Skip hidden directories
        if '/.git' in root or '/node_modules' in root:
            continue
        for file in files[:100]:  # Limit to first 100 files for performance
            _, ext = os.path.splitext(file.lower())
            if ext in lang_map:
                ext_counts[ext] = ext_counts.get(ext, 0) + 1
    
    if ext_counts:
        primary_ext = max(ext_counts, key=lambda k: ext_counts.get(k, 0))
        if primary_ext in lang_map:
            language = lang_map[primary_ext]
    
    # Check git status
    has_git = os.path.exists(os.path.join(project_path, ".git"))
    has_remote = False
    remote_url = ""
    is_private = None
    
    if has_git:
        try:
            result = subprocess.run(['git', 'remote', 'get-url', 'origin'], 
                                  cwd=project_path, capture_output=True, text=True)
            if result.returncode == 0:
                has_remote = True
                remote_url = result.stdout.strip()
                
                # Check if repo is private using gh CLI
                if 'github.com' in remote_url:
                    # Extract owner/repo from URL
                    if remote_url.startswith('git@github.com:'):
                        repo_path = remote_url.replace('git@github.com:', '').replace('.git', '')
                    elif 'github.com/' in remote_url:
                        repo_path = remote_url.split('github.com/')[-1].replace('.git', '')
                    else:
                        repo_path = None
                    
                    if repo_path:
                        try:
                            # Use gh api to check if repo is private
                            api_result = subprocess.run(['gh', 'api', f'repos/{repo_path}', '-q', '.private'], 
                                                      capture_output=True, text=True)
                            if api_result.returncode == 0:
                                is_private = api_result.stdout.strip().lower() == 'true'
                        except:
                            pass
        except:
            pass
    
    # Get last modified date
    last_modified = "Unknown"
    try:
        timestamp = os.path.getmtime(project_path)
        last_modified = datetime.datetime.fromtimestamp(timestamp).strftime("%Y-%m-%d %H:%M")
    except:
        pass
    
    # Check for README
    readme_exists = any(os.path.exists(os.path.join(project_path, name)) 
                       for name in ["README.md", "Readme.md", "readme.md", "README.txt", "README"])
    
    # Check for .gitignore
    gitignore_exists = os.path.exists(os.path.join(project_path, ".gitignore"))
    
    # Load project metadata
    metadata = load_project_metadata(project_path)
    
    return {
        'name': project_name,
        'path': project_path,
        'type': project_type,
        'language': language,
        'last_modified': last_modified,
        'has_git': has_git,
        'has_remote': has_remote,
        'remote_url': remote_url,
        'is_private': is_private,
        'readme_exists': readme_exists,
        'gitignore_exists': gitignore_exists,
        'metadata': metadata
    }

@app.route('/')
def index():
    """Main page."""
    return render_template('index.html')

@app.route('/api/projects')
def get_projects():
    """Get all projects with their information."""
    projects = []
    annotations = load_annotations()
    
    for item in sorted(os.listdir(PROJECTS_DIR)):
        item_path = os.path.join(PROJECTS_DIR, item)
        if os.path.isdir(item_path) and not item.startswith('.'):
            project_info = scan_project(item_path)
            
            # Add annotations if they exist
            if project_info['name'] in annotations:
                project_info['annotation'] = annotations[project_info['name']]
            else:
                project_info['annotation'] = {
                    'notes': '',
                    'tags': [],
                    'github_created': False,
                    'priority': 'normal'
                }
            
            projects.append(project_info)
    
    return jsonify(projects)

@app.route('/api/project/<project_name>/annotate', methods=['POST'])
def annotate_project(project_name):
    """Save annotation for a project."""
    data = request.json
    annotations = load_annotations()
    
    annotations[project_name] = {
        'notes': data.get('notes', ''),
        'tags': data.get('tags', []),
        'github_created': data.get('github_created', False),
        'priority': data.get('priority', 'normal')
    }
    
    save_annotations(annotations)
    return jsonify({'status': 'success'})

@app.route('/api/project/<project_name>/metadata', methods=['POST'])
def save_project_metadata(project_name):
    """Save project-specific metadata to .project-meta.json file."""
    data = request.json
    project_path = os.path.join(PROJECTS_DIR, project_name)
    
    if not os.path.exists(project_path):
        return jsonify({'status': 'error', 'message': 'Project not found'}), 404
    
    meta_file = os.path.join(project_path, '.project-meta.json')
    
    try:
        # Load existing metadata
        existing_meta = load_project_metadata(project_path)
        
        # Update with new data
        existing_meta.update(data)
        
        # Save to file
        with open(meta_file, 'w') as f:
            json.dump(existing_meta, f, indent=2)
        
        return jsonify({'status': 'success', 'message': 'Metadata saved'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/project/<project_name>/create-github', methods=['POST'])
def create_github_repo(project_name):
    """Create GitHub repository for a project."""
    data = request.json
    private = data.get('private', False)
    
    project_path = os.path.join(PROJECTS_DIR, project_name)
    
    if not os.path.exists(project_path):
        return jsonify({'status': 'error', 'message': 'Project not found'}), 404
    
    try:
        # Check if git repo exists
        if not os.path.exists(os.path.join(project_path, '.git')):
            # Initialize git repo
            subprocess.run(['git', 'init'], cwd=project_path, check=True)
            subprocess.run(['git', 'add', '.'], cwd=project_path, check=True)
            subprocess.run(['git', 'commit', '-m', 'Initial commit'], cwd=project_path, check=True)
        
        # Create GitHub repo with source flag to set it as origin and push
        visibility = '--private' if private else '--public'
        cmd = ['gh', 'repo', 'create', project_name, visibility, '--source', '.', '--push']
        
        print(f"Running command: {' '.join(cmd)}")
        result = subprocess.run(cmd, cwd=project_path, capture_output=True, text=True)
        print(f"Return code: {result.returncode}")
        print(f"Stdout: {result.stdout}")
        print(f"Stderr: {result.stderr}")
        
        if result.returncode == 0:
            
            # Update annotations
            annotations = load_annotations()
            if project_name not in annotations:
                annotations[project_name] = {}
            annotations[project_name]['github_created'] = True
            save_annotations(annotations)
            
            return jsonify({'status': 'success', 'message': 'GitHub repository created'})
        else:
            error_msg = result.stderr if result.stderr else result.stdout
            if 'already exists' in error_msg or 'repository-exists' in error_msg:
                # Try to link existing repo
                print(f"Repository already exists, attempting to link and push...")
                return link_existing_github_repo(project_name, project_path)
            return jsonify({'status': 'error', 'message': error_msg}), 400
            
    except subprocess.CalledProcessError as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

def link_existing_github_repo(project_name, project_path):
    """Link to existing GitHub repository."""
    try:
        # Get current user's GitHub username
        user_result = subprocess.run(['gh', 'api', 'user', '-q', '.login'], 
                                   capture_output=True, text=True)
        if user_result.returncode != 0:
            return jsonify({'status': 'error', 'message': 'Could not get GitHub username'}), 500
        
        username = user_result.stdout.strip()
        print(f"GitHub username: {username}")
        
        # Remove existing remote if it exists
        remote_check = subprocess.run(['git', 'remote', 'get-url', 'origin'], 
                                    cwd=project_path, capture_output=True, text=True)
        
        if remote_check.returncode == 0:
            print(f"Removing existing remote: {remote_check.stdout.strip()}")
            subprocess.run(['git', 'remote', 'remove', 'origin'], cwd=project_path)
        
        # Add the correct remote
        remote_url = f'https://github.com/{username}/{project_name}.git'
        print(f"Adding remote: {remote_url}")
        subprocess.run(['git', 'remote', 'add', 'origin', remote_url], 
                     cwd=project_path, check=True)
        
        # Check which branch we're on
        branch_result = subprocess.run(['git', 'branch', '--show-current'], 
                                     cwd=project_path, capture_output=True, text=True)
        current_branch = branch_result.stdout.strip()
        
        if not current_branch:
            # No branch yet, create main
            subprocess.run(['git', 'checkout', '-b', 'main'], cwd=project_path)
            current_branch = 'main'
        
        print(f"Current branch: {current_branch}")
        
        # Check if remote has any commits
        remote_refs = subprocess.run(['git', 'ls-remote', 'origin'], 
                                   cwd=project_path, capture_output=True, text=True)
        
        if remote_refs.stdout.strip():
            # Remote has commits, try to pull first
            print("Remote has commits, attempting to pull...")
            pull_result = subprocess.run(['git', 'pull', 'origin', current_branch, '--allow-unrelated-histories'], 
                                       cwd=project_path, capture_output=True, text=True)
            
            if pull_result.returncode != 0 and current_branch == 'main':
                # Try master if main fails
                pull_result = subprocess.run(['git', 'pull', 'origin', 'master', '--allow-unrelated-histories'], 
                                           cwd=project_path, capture_output=True, text=True)
        
        # Now push (force if needed for empty repos)
        print(f"Pushing to origin/{current_branch}...")
        push_result = subprocess.run(['git', 'push', '-u', 'origin', current_branch], 
                                   cwd=project_path, capture_output=True, text=True)
        
        if push_result.returncode != 0 and not remote_refs.stdout.strip():
            # Empty remote, force push
            print("Empty remote detected, force pushing...")
            push_result = subprocess.run(['git', 'push', '-u', 'origin', current_branch, '--force'], 
                                       cwd=project_path, capture_output=True, text=True)
        
        if push_result.returncode == 0:
            # Update annotations
            annotations = load_annotations()
            if project_name not in annotations:
                annotations[project_name] = {}
            annotations[project_name]['github_created'] = True
            save_annotations(annotations)
            
            return jsonify({'status': 'success', 'message': 'Linked to existing GitHub repository and pushed code'})
        else:
            return jsonify({'status': 'error', 'message': f'Could not push to existing repo: {push_result.stderr}'}), 400
            
    except subprocess.CalledProcessError as e:
        return jsonify({'status': 'error', 'message': f'Error linking to existing repo: {str(e)}'}), 500

@app.route('/api/project/<project_name>/init-git', methods=['POST'])
def init_git(project_name):
    """Initialize git repository for a project."""
    project_path = os.path.join(PROJECTS_DIR, project_name)
    
    if not os.path.exists(project_path):
        return jsonify({'status': 'error', 'message': 'Project not found'}), 404
    
    try:
        subprocess.run(['git', 'init'], cwd=project_path, check=True)
        
        # Check if there are files to commit
        status = subprocess.run(['git', 'status', '--porcelain'], 
                              cwd=project_path, capture_output=True, text=True)
        
        if status.stdout.strip():
            subprocess.run(['git', 'add', '.'], cwd=project_path, check=True)
            subprocess.run(['git', 'commit', '-m', 'Initial commit'], 
                         cwd=project_path, check=True)
        
        return jsonify({'status': 'success', 'message': 'Git repository initialized'})
        
    except subprocess.CalledProcessError as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/project/<project_name>/open-vscode', methods=['POST'])
def open_in_vscode(project_name):
    """Open project in VS Code."""
    project_path = os.path.join(PROJECTS_DIR, project_name)
    
    if not os.path.exists(project_path):
        return jsonify({'status': 'error', 'message': 'Project not found'}), 404
    
    try:
        # Try to open with 'code' command
        subprocess.run(['code', project_path], check=True)
        return jsonify({'status': 'success', 'message': 'Opened in VS Code'})
    except subprocess.CalledProcessError:
        # Try with full path on macOS
        try:
            subprocess.run(['/usr/local/bin/code', project_path], check=True)
            return jsonify({'status': 'success', 'message': 'Opened in VS Code'})
        except subprocess.CalledProcessError:
            # Try another common VS Code path
            try:
                subprocess.run(['/Applications/Visual Studio Code.app/Contents/Resources/app/bin/code', project_path], check=True)
                return jsonify({'status': 'success', 'message': 'Opened in VS Code'})
            except subprocess.CalledProcessError as e:
                return jsonify({'status': 'error', 'message': 'Could not open VS Code. Make sure the "code" command is installed in PATH.'}), 500

@app.route('/api/project/<project_name>/files')
def get_project_files(project_name):
    """Get file tree for a project."""
    project_path = os.path.join(PROJECTS_DIR, project_name)
    
    if not os.path.exists(project_path):
        return jsonify({'status': 'error', 'message': 'Project not found'}), 404
    
    def build_tree(path, base_path, max_depth=5, current_depth=0):
        """Build file tree structure."""
        if current_depth >= max_depth:
            return None
            
        items = []
        try:
            for item in sorted(os.listdir(path)):
                if item.startswith('.'):
                    continue
                    
                item_path = os.path.join(path, item)
                relative_path = os.path.relpath(item_path, base_path)
                
                # Skip certain directories
                if item in ['node_modules', '__pycache__', 'dist', 'build', '.git', 
                           'venv', 'env', '.venv', 'target', '.idea', '.vscode']:
                    continue
                
                if os.path.isdir(item_path):
                    children = build_tree(item_path, base_path, max_depth, current_depth + 1)
                    if children is not None:
                        items.append({
                            'name': item,
                            'path': relative_path,
                            'type': 'directory',
                            'children': children
                        })
                else:
                    # Get file size
                    size = os.path.getsize(item_path)
                    items.append({
                        'name': item,
                        'path': relative_path,
                        'type': 'file',
                        'size': size
                    })
        except PermissionError:
            pass
            
        return items
    
    tree = build_tree(project_path, project_path)
    return jsonify({'status': 'success', 'tree': tree})

@app.route('/api/project/<project_name>/file/<path:file_path>')
def get_file_content(project_name, file_path):
    """Get content of a specific file."""
    project_path = os.path.join(PROJECTS_DIR, project_name)
    full_path = os.path.join(project_path, file_path)
    
    # Security check - ensure the path is within the project directory
    if not os.path.abspath(full_path).startswith(os.path.abspath(project_path)):
        return jsonify({'status': 'error', 'message': 'Invalid file path'}), 403
    
    if not os.path.exists(full_path):
        return jsonify({'status': 'error', 'message': 'File not found'}), 404
    
    if os.path.isdir(full_path):
        return jsonify({'status': 'error', 'message': 'Path is a directory'}), 400
    
    # Get file info
    file_size = os.path.getsize(full_path)
    mime_type, _ = mimetypes.guess_type(full_path)
    
    # Don't read files larger than 1MB
    if file_size > 1024 * 1024:
        return jsonify({
            'status': 'success',
            'content': None,
            'message': 'File too large to display',
            'size': file_size,
            'mime_type': mime_type
        })
    
    # Check if it's a binary file
    is_binary = mime_type and (
        mime_type.startswith('image/') or 
        mime_type.startswith('video/') or
        mime_type.startswith('audio/') or
        mime_type.startswith('application/') and not mime_type.endswith('json')
    )
    
    if is_binary:
        return jsonify({
            'status': 'success',
            'content': None,
            'message': 'Binary file',
            'size': file_size,
            'mime_type': mime_type
        })
    
    try:
        with open(full_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        return jsonify({
            'status': 'success',
            'content': content,
            'size': file_size,
            'mime_type': mime_type or 'text/plain'
        })
    except UnicodeDecodeError:
        return jsonify({
            'status': 'success',
            'content': None,
            'message': 'Unable to decode file',
            'size': file_size,
            'mime_type': mime_type
        })

if __name__ == '__main__':
    app.run(debug=True, port=5000, host='127.0.0.1')