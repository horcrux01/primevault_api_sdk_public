# Secret Scanning Setup

Following the signing key exposure incident (2026-04-06), we added gitleaks-based secret scanning to this repo. This document covers what was done, how it works, and what remains.

## What Was Done

### 1. Pre-commit Hook (local, developer-side)

Added gitleaks to `.pre-commit-config.yaml`. Every `git commit` runs gitleaks locally and rejects the commit if a secret is detected.

**Setup for new developers:**

```bash
pip install pre-commit
cd primevault_api_sdk_public
pre-commit install
```

### 2. GitHub Action (server-side)

Added `.github/workflows/gitleaks.yml`. Runs on every push and pull request. Installs gitleaks CLI directly (no license required) and scans the full git history.

This cannot be bypassed — even if a developer skips the local hook with `--no-verify`, the GitHub Action will catch it.

### 3. False Positive Handling

Added `.gitleaksignore` for suppressing known false positives. One entry exists for the test API key in `test_api_client.py`.

To add a new exception, copy the `Fingerprint` field from `gitleaks detect` or CI output and add it to `.gitleaksignore`.

## How It Works

gitleaks detects secrets using two methods:

- **Pattern matching** — regex rules for known secret formats (PEM keys, AWS keys, API tokens, JWTs, etc.) covering ~150 patterns
- **Shannon entropy** — flags random-looking strings above a threshold, catching secrets that don't match any known pattern

## Protection Layers

| Layer | What it does | Can be bypassed? |
|---|---|---|
| Pre-commit hook | Blocks secrets on developer's machine before commit | Yes, with `--no-verify` |
| GitHub Action | Detects secrets on every push/PR | No, but findings can be ignored if merge isn't blocked |
| Required status check (UI setting) | Prevents merging PRs if gitleaks fails | No |
| GitHub push protection (UI setting) | Prevents pushing secrets directly to `main` | No |

## Remaining Steps (Requires Repo Admin)

These are UI-only settings — no code changes needed.

### 1. Make gitleaks a required status check

1. Go to repo **Settings > Branches**
2. Add or edit branch protection rule for `main`
3. Check **Require a pull request before merging**
4. Check **Require status checks to pass before merging**
5. Search for and add `gitleaks`
6. Check **Require branches to be up to date before merging**
7. Save

### 2. Enable GitHub's built-in secret scanning

1. Go to repo **Settings > Code security and analysis**
2. Enable **Secret scanning** for the repo
3. Enable **Push protection** to block pushes containing detected secrets

GitHub's built-in scanner covers a different set of patterns (provider-specific: AWS, Stripe, etc.) than gitleaks. Running both gives broader coverage.

## Replicating to Other Repos

To add the same setup to another repo:

1. Copy `.pre-commit-config.yaml` gitleaks entry (or add it manually)
2. Copy `.github/workflows/gitleaks.yml`
3. Copy `.gitleaksignore`
4. Run `pre-commit install` in the repo
5. Apply the two UI settings above

## Auditing Existing Repos

Run against the full git history to find previously committed secrets:

```bash
gitleaks detect --source <repo-path> --verbose
```

Any secrets found must be **rotated immediately**. Removing a commit from git history does NOT invalidate the secret — GitHub caches commits and bots/archives may have already captured it.
