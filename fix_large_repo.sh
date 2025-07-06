#!/bin/bash
# Script to create a clean copy of a repository without large files

if [ $# -lt 1 ]; then
    echo "Usage: $0 <repo_path>"
    exit 1
fi

REPO_PATH="$1"
REPO_NAME=$(basename "$REPO_PATH")
TEMP_PATH="${REPO_PATH}_clean"

echo "Creating clean copy of $REPO_NAME..."

# Create a clean copy
cp -r "$REPO_PATH" "$TEMP_PATH"

# Remove .git directory
rm -rf "$TEMP_PATH/.git"

# Remove large files
find "$TEMP_PATH" -type f -size +50M -delete

# Remove log files
find "$TEMP_PATH" -name "*.log" -type f -delete

# Initialize new git repo
cd "$TEMP_PATH"
git init
git add .
git commit -m "Initial commit - cleaned repository"

echo "Clean repository created at: $TEMP_PATH"
echo "Next steps:"
echo "1. Review the clean repository"
echo "2. Add remote: git remote add origin <github_url>"
echo "3. Push: git push -u origin main"