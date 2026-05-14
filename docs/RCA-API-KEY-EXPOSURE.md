# RCA — API Signing Key Exposure via Public Branch Push

**Date of Incident:** April 10, 2026  
**Severity:** Critical  
**Status:** Contained — remediation in progress

---

## 1. Summary

A test API signing key was inadvertently exposed on a public GitHub branch when an AI coding agent pushed local branch code that included the key in test case files. The branch itself was publicly accessible. An external attacker discovered the exposed key and attempted unauthorized transactions.

---

## 2. Timeline of Events

| Time | Event |
|------|-------|
| 6th April, 2026 | AI agent pushes a branch to primevault_api_sdk_public containing API key in test case files |
| 10th April, 2026 | Attacker discovers the exposed API key on the public branch |
| 10th April, 2026 ~8:10 p.m. | Attempt 1: Attacker initiates a $1 transfer — succeeds (no approval required for small amount) |
| 10th April, 2026 ~8:17 p.m. | Attempt 2: Attacker initiates a $1,000 transfer — fails (requires policy approval, nobody approves) |
| 10th April, 2026 ~8:20 p.m. | Attempt 3: Attacker initiates a $45,000 transfer — blocked |
| 10th April, 2026 ~8:20 p.m. | Vivek notices unusual activity and asks Tushal: "Are you using your API user for this?" |
| 10th April, 2026 ~8:20 p.m. | Tushal confirms he is not — team recognises the account is under attack |
| 10th April, 2026 ~8:30 p.m. | All access tied to Tushal's user/email is immediately revoked |

---

## 3. Impact

- **Financial loss:** ~$1 (single successful micro-transfer before detection)
- **Prevented loss:** $46,000+ (blocked by approval policy and quick response)
- **Credential scope:** API signing key for one user — revoked immediately
- **Data exposure:** No customer data was accessed or exfiltrated

---

## 4. Root Cause

1. **No secret-scanning in CI or pre-commit** — The repository had no pre-commit hooks or CI pipeline checks to detect secrets before they reached a public branch.
2. **AI agent pushed directly to a public repo** — The AI coding agent had direct write access to the public repository and pushed a branch containing test credentials without human review.
3. **Branch visibility on public repos** — Even though the PR diff was clean, the underlying branch (with test files containing the key) was publicly browsable on GitHub. Any visitor could view the branch contents.
4. **No private/public repo separation** — There was no separation between development (private) and release (public) repositories. Code with test credentials was pushed to the same repo that external users can access.
5. **Real API key used in test fixtures** — The API key used in test cases was a real, active signing key rather than a dummy or environment-scoped token. A test-only key with no transaction permissions would have rendered the exposure harmless.

---

## 5. Why the Approval Policy Saved Us

PrimeVault's transaction approval policy requires multi-party sign-off for transfers above a configurable threshold. The attacker could only execute a $1 transfer autonomously. Both the $1,000 and $45,000 attempts required approvals that were never granted, buying the team time to detect and respond.

---

## 6. Immediate Actions Taken

### 6.1 Credential Revocation
- All API keys, sessions, and access tied to the compromised user were revoked immediately.
- Verified no other credentials were exposed in the repository history.

### 6.2 Gitleaks — Pre-commit & CI Secret Scanning
- Added gitleaks as a pre-commit hook across all SDK repos (Python & JS).
- Added gitleaks as a GitHub Actions workflow that runs on every push and PR.
- Known false positives (test UUIDs, example keys) are tracked in .gitleaksignore files.

### 6.3 Private Repo Workflow
- Created private mirror repos for both Python and JS SDKs.
- All development now happens in private repos.
- A manual-trigger GitHub Action (sync-to-public) pushes changes from private main to a PR on the public repo — no direct pushes to public.
- Workflow files from the private repo are excluded from sync to prevent leakage.

### 6.4 NPM Version Monitoring
- Added a scheduled GitHub Action that runs hourly to compare package.json version against the npm registry.
- Any mismatch triggers a Slack alert — catches unauthorized publishes.

### 6.5 IAM Role Separation
- Created separate IAM roles with least-privilege access.
- Python backend roles have no access to TSS or KMS.
- Agent (AI) access is restricted — limited to pushing branches/PRs, no direct main branch access.

---

## 7. Next Steps

### 7.1 Session Activity Logging
- Implement detailed session activity logging for all API users.
- Log every authentication event, transaction initiation, and approval action.

### 7.2 Slack Alerts on Privileged IAM Usage
- Set up real-time Slack notifications when IAM roles with elevated access are used.
- Covers: TSS access, KMS access, admin operations.

### 7.3 Deprecate Broad IAM Access
- Migrate all write operations to a super-user page with explicit audit trail.
- Deprecate current IAM roles that have write access once the super-user migration is complete.

### 7.4 Move Write Operations to Enclave
- Write operations will be deprecated from the current architecture.
- All sensitive write operations will move to an enclave-based execution model.

### 7.5 Alerts on User & Policy Changes
- Any addition of a new user or modification of an approval policy must trigger an alert.
- Alert channels: Slack + email to security team.

---

## 8. Lessons Learned

1. **Never push secrets to public repos, even on branches** — Branch content is as visible as merged code on public repositories.
2. **AI agents need guardrails** — Agents with repo write access must be scoped to private repos only, with human review before anything reaches public.
3. **Approval policies are a critical safety net** — The multi-party approval requirement prevented a $46K loss and gave the team time to respond.
4. **Defense in depth works** — No single control stopped the attack; it was the combination of transaction limits, approval policies, and human vigilance.
5. **Automate secret detection** — Manual review cannot reliably catch every secret; pre-commit hooks and CI scanning are essential.
