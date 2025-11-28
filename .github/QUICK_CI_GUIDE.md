# Quick CI/CD Guide

## TL;DR - Get Tests Running on Pull Requests in 3 Steps

### 1. Push Workflows to GitHub
```bash
git add .github/workflows/
git commit -m "Add CI/CD workflows"
git push
```

### 2. Enable Workflow Permissions
- Go to: **Settings → Actions → General**
- Under "Workflow permissions": Select **"Read and write permissions"**
- Click **Save**

### 3. Create a Test PR
- Make any small change
- Push to a new branch
- Create a pull request
- Watch tests run automatically! ✨

---

## What Gets Tested on Every PR

✅ **69 automated tests**
- Player performance model (GMM)
- Monte Carlo simulator
- Trade analyzer
- Free agent recommender
- Decision maker CLI

✅ **Multiple Python versions**
- Tests run on Python 3.9, 3.10, 3.11, and 3.12

✅ **Automatic PR comments**
- "✅ All tests passed! Ready for review."
- "❌ Some tests failed. Check logs."

---

## Workflow Files

### `pr-tests.yml` - Quick Tests
**Runs on:** Every pull request
**Duration:** ~2 minutes
**Purpose:** Fast feedback loop

### `fantasy-decision-maker-tests.yml` - Full Suite
**Runs on:** PR + push to master
**Duration:** ~10 minutes (parallel jobs)
**Purpose:** Comprehensive validation
**Includes:**
- Test matrix (4 Python versions)
- Code linting (flake8, pylint)
- Coverage report
- Config validation

---

## Common Tasks

### View Test Results
1. Go to your PR
2. Scroll to "Checks" section
3. Click any check → "Details"

### Re-run Failed Tests
1. Go to Actions tab
2. Click the failed workflow
3. Click "Re-run jobs"

### Run Tests Locally Before PR
```bash
# Quick check
python run_tests.py

# Same as CI
python -m unittest discover tests -v
```

### Add Status Badge to README
```markdown
![Tests](https://github.com/YOUR_USERNAME/espn-api/actions/workflows/pr-tests.yml/badge.svg)
```

---

## Require Tests Before Merge (Optional)

### Enable Branch Protection
1. **Settings → Branches**
2. **Add rule** for `master` or `main`
3. Enable:
   - ✅ Require status checks to pass
   - ✅ Require branches to be up to date
4. Select checks:
   - Quick Tests
   - Run Fantasy Decision Maker Tests
5. **Create** or **Save changes**

Now PRs can't be merged unless tests pass!

---

## Troubleshooting

### Tests pass locally but fail in CI
```bash
# Use same Python version as CI
python3.11 -m venv test_env
source test_env/bin/activate
pip install -r requirements.txt
python run_tests.py
```

### Workflow doesn't run
- Check `.github/workflows/` files are committed
- Verify YAML syntax is correct
- Ensure Actions are enabled in repo settings

### Can't comment on PRs
- Enable "Read and write permissions" in Settings → Actions

---

## Quick Links

- **[Full Documentation](.github/CICD_SETUP.md)** - Complete setup guide
- **[Test Documentation](../TESTING.md)** - How tests work
- **[GitHub Actions Docs](https://docs.github.com/actions)** - Official docs

---

## Current Status

After setup, you'll see:
- ✅ Automatic tests on every PR
- ✅ Test results visible in PR checks
- ✅ Coverage reports available
- ✅ Multiple Python version validation
- ✅ Code quality checks

**Questions?** See `.github/CICD_SETUP.md` for detailed docs.
