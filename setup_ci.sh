#!/bin/bash
# Setup script for GitHub Actions CI/CD

set -e  # Exit on error

echo "🚀 Setting up GitHub Actions CI/CD for Fantasy Football Decision Maker"
echo ""

# Check if we're in a git repo
if ! git rev-parse --git-dir > /dev/null 2>&1; then
    echo "❌ Error: Not in a git repository"
    echo "   Run this script from the root of your git repo"
    exit 1
fi

# Check if workflows exist
if [ ! -d ".github/workflows" ]; then
    echo "❌ Error: .github/workflows directory not found"
    exit 1
fi

echo "✅ Found .github/workflows directory"
echo ""

# List workflow files
echo "📋 Workflow files:"
ls -1 .github/workflows/*.yml | while read file; do
    echo "   - $(basename $file)"
done
echo ""

# Check if changes need to be committed
if ! git diff --quiet .github/workflows/ 2>/dev/null; then
    echo "📝 Workflow files have uncommitted changes"
    echo ""
    echo "Would you like to commit and push the workflow files? (y/n)"
    read -r response

    if [[ "$response" =~ ^[Yy]$ ]]; then
        echo ""
        echo "📦 Adding workflow files to git..."
        git add .github/workflows/

        echo "💾 Committing..."
        git commit -m "Add GitHub Actions CI/CD workflows for Fantasy Decision Maker

- Add pr-tests.yml: Quick tests on every pull request
- Add fantasy-decision-maker-tests.yml: Comprehensive testing with coverage
- Tests run on Python 3.9, 3.10, 3.11, 3.12
- Includes linting and coverage reports"

        echo ""
        echo "🔄 Pushing to GitHub..."
        git push

        echo ""
        echo "✅ Workflows committed and pushed!"
    else
        echo ""
        echo "ℹ️  Skipping commit. You can commit manually later with:"
        echo "   git add .github/workflows/"
        echo "   git commit -m 'Add CI/CD workflows'"
        echo "   git push"
    fi
else
    echo "✅ Workflow files are already committed"
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🎉 CI/CD Setup Complete!"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "📚 Next Steps:"
echo ""
echo "1. Enable Workflow Permissions (for PR comments):"
echo "   → Go to: https://github.com/$(git config --get remote.origin.url | sed 's/.*github.com[:/]\(.*\)\.git/\1/')/settings/actions"
echo "   → Under 'Workflow permissions'"
echo "   → Select 'Read and write permissions'"
echo "   → Click 'Save'"
echo ""
echo "2. Create a test Pull Request:"
echo "   → Make a small change to test the workflows"
echo "   → Create a PR to see tests run automatically"
echo ""
echo "3. Optional: Enable Branch Protection:"
echo "   → Go to: https://github.com/$(git config --get remote.origin.url | sed 's/.*github.com[:/]\(.*\)\.git/\1/')/settings/branches"
echo "   → Add rule for your main branch"
echo "   → Require status checks to pass before merging"
echo ""
echo "4. View Workflow Runs:"
echo "   → Go to: https://github.com/$(git config --get remote.origin.url | sed 's/.*github.com[:/]\(.*\)\.git/\1/')/actions"
echo ""
echo "📖 For detailed documentation, see: .github/CICD_SETUP.md"
echo ""
echo "✨ Happy coding!"
