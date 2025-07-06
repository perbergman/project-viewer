# Project Viewer

A web-based application for viewing, annotating, and managing code projects with GitHub integration.

## Features

- **Project Overview**: Displays all projects in a grid layout with key information
- **Project Annotations**: Add notes, tags, and priority levels to projects
- **Git Integration**: Initialize git repositories directly from the interface
- **GitHub Integration**: Create GitHub repositories (public/private) using gh CLI
- **Filtering**: Filter projects by language, type, and status
- **Search**: Search projects by name, notes, or tags
- **Statistics**: View overall statistics about your projects

## Requirements

- Python 3.7+
- Flask
- gh CLI (for GitHub integration)
- Git

## Installation

1. Clone or navigate to the project-viewer directory:
```bash
cd ~/Documents/dev/project-viewer
```

2. Create a virtual environment (recommended):
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Ensure gh CLI is installed and authenticated:
```bash
gh auth login
```

## Usage

1. Start the application:
```bash
python app.py
```

2. Open your browser and navigate to:
```
http://localhost:5000
```

3. The application will scan all projects in `~/Documents/dev/` directory

## Features Guide

### Viewing Projects
- Projects are displayed in a responsive grid layout
- Each card shows:
  - Project name and type
  - Programming language
  - Git/GitHub status
  - README and .gitignore existence
  - Last modified date
  - Annotations (if any)

### Filtering and Search
- Filter by programming language
- Filter by project type
- Filter by status (no git, no remote, no README)
- Search across project names, notes, and tags

### Annotating Projects
1. Click on any project card
2. A side panel will open with annotation options:
   - Add/edit notes
   - Add tags (press Enter to add)
   - Set priority (low/normal/high)
   - View GitHub status

### Git Operations
- **Initialize Git**: Creates a git repository and makes initial commit
- **Create GitHub Repo**: Creates a GitHub repository and pushes the code
  - Option to make repository private
  - Uses gh CLI for authentication

### Project Annotations Storage
Annotations are stored in `project_annotations.json` in the application directory.

### Project Metadata Files
Each project can have a `.project-meta.json` file in its root directory with additional information:

```json
{
  "description": "Detailed project description",
  "status": "active|inactive|archived",
  "category": "Web|Mobile|CLI|Library|etc",
  "technologies": ["Python", "Flask", "etc"],
  "created": "2023-01-15",
  "lastActive": "2023-06-20",
  "purpose": "Why this project exists",
  "notes": "Any additional notes"
}
```

This metadata is automatically loaded and displayed in the project viewer.

## Configuration

To change the projects directory, edit the `PROJECTS_DIR` variable in `app.py`:
```python
PROJECTS_DIR = os.path.expanduser("~/Documents/dev")
```

## Security Note

This application runs locally and performs git operations on your filesystem. Only run it in trusted environments.

## Future Enhancements

- Batch operations for multiple projects
- Integration with the code-project-scanner
- Project templates and initialization
- Webhook integration for automatic updates
- Export functionality for project reports