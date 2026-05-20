# JoJo Bot v2.0 Security Audit

**Date:** 2026-05-20
**Tester:** orchestrator (automated, session run)

---

## Dependency Audit (Python)

**Tool:** `pip-audit 2.10.0`
**Command:** `.venv/Scripts/pip-audit` (run against the `.venv` site-packages)

**Result:** 6 known vulnerabilities found in 4 packages. None are rated CRITICAL at
time of scan; all have available fixes. Remediation is recommended before production
deployment.

| Package | Installed | CVE | Fix Version | Severity notes |
|---|---|---|---|---|
| idna | 3.13 | CVE-2026-45409 | 3.15 | IDNA label decoding issue |
| pip | 26.0.1 | CVE-2026-3219 | (no fix yet) | pip internal |
| pip | 26.0.1 | CVE-2026-6357 | 26.1 | pip internal |
| python-multipart | 0.0.26 | CVE-2026-42561 | 0.0.27 | FastAPI file-upload |
| urllib3 | 2.6.3 | CVE-2026-44431 | 2.7.0 | HTTP library |
| urllib3 | 2.6.3 | CVE-2026-44432 | 2.7.0 | HTTP library |

**Skipped:** `jojo-bot 0.1.0` — local package, not on PyPI, not auditable by pip-audit.

**Recommended remediation:**

```
.venv/Scripts/pip install --upgrade idna pip python-multipart urllib3
```

**Blocker assessment:** No HIGH or CRITICAL CVEs found. `python-multipart` (FastAPI
file-upload) and `urllib3` (HTTP transport) are medium-severity and should be
patched before the next production push. `pip` CVEs affect the build toolchain only,
not the runtime application.

---

## Secret Scan

**Tool:** Python regex scan over `git log -p --all --since="2024-01-01"` output
**Pattern:** `(api_key|secret|token|password)\s*=\s*["'][^"']{8,}["']` (case-insensitive)
**Scanned:** ~40 MB of git diff output (2 commits in history)

**Result:** 4 candidate matches found — all are false positives (test fixtures and
config key constant names):

| Match | Classification | File context |
|---|---|---|
| `api_key="fake-key"` | test fixture | unit test mock |
| `API_KEY = "anthropic_api_key"` | config key name (not a value) | jojo_core/config.py |
| `TOKEN = "graph_access_token"` | config key name (not a value) | jojo_core/config.py |
| `TOKEN = "JOJO_GRAPH_ACCESS_TOKEN"` | env var name (not a value) | jojo_core/config.py |

**Verdict: CLEAN** — No real credentials committed to git history.

---

## Git Hooks

**Active hooks at `.git/hooks/`:** None (all files are `.sample` templates).

The following hooks are present as samples but NOT active:
`applypatch-msg`, `commit-msg`, `fsmonitor-watchman`, `post-update`,
`pre-applypatch`, `pre-commit`, `pre-merge-commit`, `pre-push`,
`pre-rebase`, `pre-receive`, `prepare-commit-msg`, `push-to-checkout`,
`sendemail-validate`, `update`

**Recommendation:** Install a `pre-commit` hook that runs the secret-scan regex
before every commit. A minimal script:

```bash
#!/usr/bin/env bash
# .git/hooks/pre-commit
set -e
git diff --cached -U0 | python3 -c "
import sys, re
diff = sys.stdin.read()
pat = re.compile(r'(api_key|secret|token|password)\s*=\s*[\"'"'"'][^\"'"'"']{16,}[\"'"'"']', re.I)
hits = pat.findall(diff)
if hits:
    print('pre-commit: potential credentials detected:', hits)
    raise SystemExit(1)
print('pre-commit secret scan: clean')
"
```

Install with:
```
cp .git/hooks/pre-commit.sample .git/hooks/pre-commit
# replace body with the script above
chmod +x .git/hooks/pre-commit
```

This is especially important before the `[cloud]` extras land (MSAL tokens,
Azure credentials) in Phase 7b.
