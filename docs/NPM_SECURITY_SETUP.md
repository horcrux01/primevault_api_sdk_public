# npm Package Security Setup

Complete security hardening for @primevault/js-api-sdk (and any future npm packages).

## 1. Trusted Publishing (CRITICAL — blocks unauthorized publishes)

Locks npm so that ONLY your GitHub Actions workflow can publish. Anyone running `npm publish` from their laptop gets rejected — even with valid credentials.

### Step 1: Configure on npmjs.com

1. Log into https://www.npmjs.com
2. Go to your package > **Settings** > **Trusted publishing**
3. Click **Add trusted publisher**
4. Select **GitHub Actions**
5. Fill in:
   - **Repository owner:** horcrux01
   - **Repository name:** primevault_api_sdk_js_public (or the private repo if publishing from there)
   - **Workflow filename:** npm-publish.yml
   - **Environment:** (leave blank unless you use GitHub environments)
6. Save

### Step 2: Update the publish workflow

Update `.github/workflows/npm-publish.yml` to use OIDC tokens instead of npm tokens:

```yaml
jobs:
  publish:
    runs-on: ubuntu-latest
    permissions:
      id-token: write    # required for trusted publishing
      contents: read
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: '20'
          registry-url: 'https://registry.npmjs.org'
      - run: npm ci
      - run: npm publish --provenance --access public
```

Note: Requires npm CLI 11.5.1+. Add `npm install -g npm@latest` before publish if needed.

### Step 3: Lock down publishing access

1. Go to package **Settings** > **Publishing access**
2. Select **Require two-factor authentication and disallow tokens**
3. This means:
   - Long-lived npm tokens can no longer publish
   - Only trusted publishers (your GitHub Action) can publish
   - Even if someone steals an npm token, it's useless

## 2. Enable 2FA on All npm Accounts (CRITICAL)

Every team member with npm access must enable 2FA:

1. Log into https://www.npmjs.com
2. Go to **Account** > **Security** (or Profile > Two-Factor Authentication)
3. Enable **2FA for authorization and publishing**
4. Use an authenticator app (not SMS)

This protects against:
- Account takeover via stolen passwords
- Unauthorized publishing even if someone has your credentials

## 3. Minimize npm Owners (HIGH)

Fewer people with publish access = smaller attack surface.

Check current owners:
```bash
npm access list collaborators @primevault/js-api-sdk
```

Remove unnecessary owners:
```bash
npm owner rm <username> @primevault/js-api-sdk
```

Ideally only 1-2 people should have owner access, and publishing should only happen via CI.

## 4. Monitor for Unauthorized Changes (MEDIUM)

### Option A: newreleases.io (recommended — free, no code)

1. Go to https://newreleases.io
2. Sign up
3. Add `@primevault/js-api-sdk` as an npm package to track
4. Connect your Slack workspace
5. Get alerts on any new version, no matter how it was published

### Option B: GitHub Action (hourly version check)

Add `.github/workflows/npm-version-monitor.yml` to the repo. Runs every hour, compares npm registry version to repo, alerts Slack if they don't match. See `docs/shared/npm-version-monitor.yml`.

## 5. Pin Dependencies (MEDIUM)

Always commit `package-lock.json`. This prevents:
- Dependency confusion attacks
- Automatically pulling a malicious new version of a dependency

In CI, use `npm ci` (not `npm install`) to install exact versions from the lockfile.

## 6. Audit Dependencies (ONGOING)

Run regularly:
```bash
npm audit
```

Enable Dependabot on the repo to auto-detect vulnerable dependencies:
- Go to repo Settings > Code security and analysis > Enable Dependabot alerts

## Summary

| Protection | What it does | Blocks |
|---|---|---|
| Trusted Publishing | Only CI can publish | Manual npm publish, stolen tokens |
| 2FA | Requires authenticator for account actions | Account takeover |
| Minimal owners | Fewer targets for attackers | Wider attack surface |
| Monitoring | Alerts on any version change | Unnoticed publishes |
| Pinned deps | Locks exact dependency versions | Dependency confusion |
| Audit | Finds known vulnerabilities | Vulnerable dependencies |
