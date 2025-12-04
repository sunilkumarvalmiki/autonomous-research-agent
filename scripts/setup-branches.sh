#!/bin/bash

# Setup script for 3-branch strategy
# Creates dev, test, and main branches

set -e

echo "🚀 Setting up 3-branch strategy..."

# Check if we're in a git repository
if [ ! -d .git ]; then
    echo "❌ Not a git repository. Please run from repository root."
    exit 1
fi

# Get current branch
CURRENT_BRANCH=$(git branch --show-current)
echo "📍 Current branch: $CURRENT_BRANCH"

# Ensure we have latest
echo "📥 Fetching latest changes..."
git fetch origin || true

# Create test branch if it doesn't exist
if ! git show-ref --verify --quiet refs/heads/test; then
    echo "🌿 Creating test branch..."
    git checkout -b test
    git push -u origin test
else
    echo "✓ test branch already exists"
fi

# Create dev branch if it doesn't exist
if ! git show-ref --verify --quiet refs/heads/dev; then
    echo "🌿 Creating dev branch..."
    git checkout -b dev  
    git push -u origin dev
else
    echo "✓ dev branch already exists"
fi

# Return to original branch
git checkout $CURRENT_BRANCH

echo ""
echo "✅ Branch setup complete!"
echo ""
echo "Branches:"
echo "  📌 main  - Production"
echo "  📌 test  - Testing/Staging"
echo "  📌 dev   - Development"
echo ""
echo "Next: Configure branch protection in GitHub Settings"
echo "See docs/BRANCHING_STRATEGY.md for details"
