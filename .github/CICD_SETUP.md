# CI/CD Setup for Fantasy Decision Maker

This repository uses GitHub Actions to automatically run tests on pull requests and commits.

## Workflows

### 1. Pull Request Tests (`pr-tests.yml`)

**Purpose:** Run quick tests on every pull request to ensure code quality.

**Triggers:**
- Opening a new pull request
- Pushing new commits to an existing PR
- Reopening a closed PR

**What it does:**
1. Checks out the code
2. Sets up Python 3.11
3. Installs dependencies
4. Runs the full test suite (`run_tests.py`)
5. Comments on the PR with test results

**Usage:**
- Runs automatically on every PR
- Provides immediate feedback on code changes
- Blocks merge if tests fail (if required checks are enabled)

**Example PR comment:**
```
✅ All tests passed! Ready for review.
```

or

```
❌ Some tests failed. Please check the workflow logs.
```

### 2. Fantasy Decision Maker Tests (`fantasy-decision-maker-tests.yml`)

**Purpose:** Comprehensive testing across multiple Python versions with code quality checks.

**Triggers:**
- Pull requests to master/main
- Pushes to master/main
- Changes to test files, source code, or requirements
- Manual trigger via GitHub UI

**What it does:**
1. **Test Matrix**: Runs tests on Python 3.9, 3.10, 3.11, and 3.12
2. **Smoke Tests**: Validates project structure
3. **Unit Tests**: Tests player performance and simulator
4. **Integration Tests**: Tests decision maker CLI
5. **Code Quality**: Runs flake8 and pylint
6. **Coverage Report**: Generates test coverage report
7. **Config Validation**: Ensures config files are valid JSON

**Jobs:**

#### Test Job
- Runs on 4 Python versions (3.9-3.12)
- Uses pip caching for faster runs
- Runs all 69 tests
- Fails if any critical test fails

#### Lint Job
- Checks code quality with flake8
- Advisory pylint check
- Helps maintain code standards

#### Coverage Job
- Generates test coverage report
- Uploads HTML coverage report as artifact
- Available for download for 7 days

#### Validate Config Job
- Validates JSON syntax in config files
- Checks documentation files exist

## Setup Instructions

### Prerequisites

1. **GitHub Repository**: Your code must be on GitHub
2. **Tests Written**: Test suite must exist (✅ already done)
3. **requirements.txt**: Dependencies must be specified (✅ already done)

### Enable Workflows

Workflows are **automatically enabled** when you push the `.github/workflows/` directory to GitHub.

```bash
# Add workflow files
git add .github/workflows/

# Commit
git commit -m "Add GitHub Actions CI/CD workflows"

# Push to GitHub
git push origin master
```

### Required Permissions

For PR comments to work, ensure the workflow has write permissions:

1. Go to your GitHub repo
2. Settings → Actions → General
3. Scroll to "Workflow permissions"
4. Select "Read and write permissions"
5. Click "Save"

### Branch Protection Rules (Optional but Recommended)

To require tests to pass before merging:

1. Go to Settings → Branches
2. Click "Add rule" for your main branch
3. Enable:
   - ✅ Require status checks to pass before merging
   - ✅ Require branches to be up to date before merging
4. Select which checks are required:
   - `Quick Tests` (from pr-tests.yml)
   - `Run Fantasy Decision Maker Tests` (from fantasy-decision-maker-tests.yml)
5. Click "Create"

## Viewing Test Results

### On Pull Requests

1. Open any pull request
2. Scroll to the bottom to see "Checks"
3. Click on any check to view details
4. Click "Details" to see full logs

### On Commits

1. Go to the "Actions" tab in your repo
2. Click on any workflow run
3. View job details and logs

### Coverage Reports

1. Go to Actions → Fantasy Decision Maker Tests → latest run
2. Scroll to "Artifacts"
3. Download "coverage-report"
4. Open `htmlcov/index.html` in a browser

## Workflow Configuration

### Changing Python Versions

Edit `fantasy-decision-maker-tests.yml`:

```yaml
strategy:
  matrix:
    python-version: ['3.9', '3.10', '3.11', '3.12']
```

Add/remove versions as needed.

### Changing Triggers

Edit the `on:` section:

```yaml
on:
  pull_request:
    branches:
      - master
      - main
      - develop  # Add more branches
  push:
    branches:
      - master
```

### Adding More Tests

Tests are automatically discovered from the `tests/` directory.

To add new test jobs:

```yaml
- name: Run new tests
  run: |
    python -m unittest tests.new_test_module -v
```

### Caching Dependencies

The workflows already cache pip packages:

```yaml
- name: Cache pip packages
  uses: actions/cache@v3
  with:
    path: ~/.cache/pip
    key: ${{ runner.os }}-pip-${{ hashFiles('requirements.txt') }}
```

This speeds up subsequent runs significantly.

## Troubleshooting

### Tests Pass Locally but Fail in CI

**Common causes:**
1. **Missing dependencies**: Ensure all deps are in `requirements.txt`
2. **Path issues**: Use absolute imports or configure PYTHONPATH
3. **Python version**: Test locally with the same Python version as CI
4. **Environment variables**: CI doesn't have your local env vars

**Debug steps:**
```bash
# Test with same Python version as CI
python3.11 run_tests.py

# Check dependencies
pip freeze > actual_requirements.txt
diff requirements.txt actual_requirements.txt

# Run in clean environment
python -m venv test_env
source test_env/bin/activate
pip install -r requirements.txt
python run_tests.py
```

### Workflow Not Triggering

**Check:**
1. Workflow file is in `.github/workflows/` directory
2. YAML syntax is valid (use https://www.yamllint.com/)
3. Trigger conditions match your PR/push
4. Actions are enabled in repo settings

### Permission Errors

**Error:** `Resource not accessible by integration`

**Solution:**
1. Go to Settings → Actions → General
2. Enable "Read and write permissions"

### Cache Issues

To clear cache:
1. Go to Actions → Caches
2. Delete old caches
3. Re-run workflow

## Best Practices

### 1. Run Tests Locally First

```bash
# Before pushing
python run_tests.py

# Before creating PR
git add .
git commit -m "Your changes"
python run_tests.py  # Verify tests pass
git push
```

### 2. Keep Tests Fast

- Current suite runs in ~15 seconds
- Use mocks instead of real API calls
- Reduce simulations in tests (100 vs 10,000)

### 3. Monitor Test Performance

Check workflow run times:
- Quick tests: Should be < 2 minutes
- Full matrix: Should be < 10 minutes
- Coverage: Should be < 3 minutes

### 4. Fix Failing Tests Immediately

Don't let tests stay red:
- Failing tests reduce confidence
- Makes it harder to find new failures
- Blocks PRs if branch protection is enabled

### 5. Update Tests When Changing Code

When you add features, add tests:
- New functions → New unit tests
- New CLI features → New integration tests
- Bug fixes → Regression tests

## Workflow Status Badges

Add status badges to your README:

```markdown
![Tests](https://github.com/YOUR_USERNAME/espn-api/actions/workflows/pr-tests.yml/badge.svg)
![Decision Maker Tests](https://github.com/YOUR_USERNAME/espn-api/actions/workflows/fantasy-decision-maker-tests.yml/badge.svg)
```

Replace `YOUR_USERNAME` with your GitHub username.

## Manual Workflow Runs

You can manually trigger the comprehensive workflow:

1. Go to Actions tab
2. Select "Fantasy Decision Maker Tests"
3. Click "Run workflow"
4. Select branch
5. Click "Run workflow"

## Notifications

Configure notifications in GitHub settings:
- Settings → Notifications
- Choose email/web notifications for:
  - Failed workflows
  - Successful workflows (optional)

## Cost

GitHub Actions is **free** for public repositories:
- Unlimited minutes for public repos
- Concurrent jobs based on your plan

For private repos:
- Free tier: 2,000 minutes/month
- Our workflows use ~2-3 minutes per run

## Next Steps

1. **Push workflows to GitHub**:
   ```bash
   git add .github/workflows/
   git commit -m "Add CI/CD workflows"
   git push
   ```

2. **Create a test PR** to see workflows in action

3. **Enable branch protection** to require passing tests

4. **Add status badges** to README

5. **Monitor** first few runs to ensure everything works

## Example Workflow Run

```
Pull Request Tests
├─ Checkout code ✅
├─ Set up Python 3.11 ✅
├─ Install dependencies ✅
└─ Run all tests ✅
   ├─ test_model_initialization ✅
   ├─ test_train_model_success ✅
   ├─ test_player_state_detection ✅
   ├─ test_simulate_matchup ✅
   └─ ... (65 more tests) ✅

Fantasy Decision Maker Tests
├─ Test (Python 3.9) ✅
├─ Test (Python 3.10) ✅
├─ Test (Python 3.11) ✅
├─ Test (Python 3.12) ✅
├─ Lint ✅
├─ Coverage ✅
└─ Validate Config ✅

Result: ✅ All checks passed!
```

## Support

If you have issues:
1. Check workflow logs for error messages
2. Review this documentation
3. Check GitHub Actions documentation: https://docs.github.com/actions
4. Open an issue in the repo

---

**Happy Testing! 🧪**
