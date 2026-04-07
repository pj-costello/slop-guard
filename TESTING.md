# Testing Playbook

A reusable guide for setting up test harnesses on new projects, extracted from
production test suites across two different stacks (Python/GCP Cloud Functions
and TypeScript/Next.js/Vercel).

Not a framework — a set of patterns you can copy-paste and adapt.

---

## Philosophy

1. **Layer your tests.** Each layer catches different bug classes. Don't rely on one layer.
2. **Lint is the first gate.** It's fast, cheap, and catches the most common mistakes before deploy.
3. **Smoke tests verify the deploy, not the logic.** They answer: "is the thing alive and wired correctly?"
4. **E2E tests verify the user journey.** They answer: "does the full pipeline produce the right result?"
5. **Visual tests catch what APIs can't.** They answer: "does the UI actually render?"
6. **Tests are standalone scripts.** No test runner framework required for smoke/E2E. Keep dependencies minimal.

---

## Layer 1: Lint — Executable Guardrails

Run before every deploy. Exit 1 blocks the pipeline.

### What to check

| Check | Why | Example |
|-------|-----|---------|
| Syntax validation | Catches typos before deploy | `py_compile` all .py files, `tsc --noEmit` for TS |
| Silent catch detection | Bare `except: pass` hides bugs | AST-walk for empty handlers without `# INTENTIONAL:` |
| Auth/secret safety | Tokens in logs = breach | Regex for token values in log statements |
| File size limits | Giant files are untestable | Warn >500 lines, error >2500 lines |
| Function length | Long functions are hard to review | Warn >100 lines |
| Framework-specific gotchas | Each platform has traps | Absolute paths in iframes, hardcoded URLs |

### Pattern: Bug-driven lint rules

Every production bug gets a lint rule. The rule's comment references the incident:

```python
# Catches: deploy failures #96, #97 (unicode escape in triple-quoted strings)
def check_python_syntax():
    ...
```

This means your lint suite is an executable history of lessons learned. New project?
Start with syntax + silent catches. Add rules as bugs ship.

### Starter template (Python)

```python
#!/usr/bin/env python3
"""Lint checks. Exit 0 = pass, exit 1 = errors found."""
import ast, sys, re
from pathlib import Path

ROOT = Path(__file__).parent.parent
ERRORS, WARNINGS = [], []

def error(rule, file, msg):
    ERRORS.append(f"  ERROR [{rule}] {file}: {msg}")

def warn(rule, file, msg):
    WARNINGS.append(f"  WARN  [{rule}] {file}: {msg}")

# Add checks here. Each check calls error() or warn().

if __name__ == "__main__":
    print("Running lint checks...")
    # Call all check functions here
    if ERRORS:
        for e in ERRORS: print(e)
        sys.exit(1)
    print(f"PASSED ({len(WARNINGS)} warnings)")
```

---

## Layer 2: Smoke Tests — Is It Alive?

Run immediately after deploy. Fast (<30s). Hit real endpoints.

### What to check

| Check | Pattern | Why |
|-------|---------|-----|
| Health endpoint | `GET /health` or `/api/health` -> 200 | Confirms deploy succeeded |
| Static pages load | `GET /` -> 200, contains expected text | Catches broken builds |
| Auth rejection | `GET /api/protected` without token -> 401 | Confirms auth middleware is wired |
| Auth acceptance | `GET /api/protected` with valid token -> not 401 | Confirms tokens work |
| Database roundtrip | Write a test record, read it back | Catches permission/connectivity issues |
| Route existence | `POST /api/endpoint` -> not 404 | Catches missing route registrations |

### Pattern: Protected route sweep

List all protected API routes. Loop through them without auth. Assert 401 on each.
This catches routes that accidentally ship without auth middleware.

```typescript
// Playwright / TypeScript
const protectedRoutes = ['/api/matches', '/api/events', '/api/conversations']
for (const route of protectedRoutes) {
  const res = await request.get(`${BASE_URL}${route}`)
  expect(res.status(), `${route} should require auth`).toBe(401)
}
```

```python
# Python stdlib
PROTECTED = ["/api/review", "/api/edit", "/api/feedback"]
for route in PROTECTED:
    status, _ = get(route)
    assert status == 401, f"{route} should reject unauthenticated requests"
```

### Pattern: Database roundtrip

Write a canary record, then read it back. Catches Firestore/Supabase permission
issues that are silent until the first user hits them.

```python
# POST to create, GET to verify
post("/api/review", {"doc_url": "test://canary", ...})
# Poll until visible (eventual consistency)
deadline = time.time() + 30
while time.time() < deadline:
    status, body = get(f"/api/review/status/{key}")
    if status != 404:
        break
    time.sleep(2)
assert status != 404, "Firestore write never became visible"
```

### Pattern: Assertion wrapper (continue-on-failure)

Don't stop at the first failure. Collect all results and report at the end.

```python
PASSED, FAILED = [], []

def check(name, fn):
    try:
        fn()
        PASSED.append(name)
        print(f"  PASS  {name}")
    except Exception as e:
        FAILED.append((name, str(e)))
        print(f"  FAIL  {name}: {e}")

# Run all checks
check("health", test_health)
check("auth_rejection", test_auth_rejection)
# ...
sys.exit(1 if FAILED else 0)
```

---

## Layer 3: E2E Tests — Does the Pipeline Work?

Run after smoke passes. Slower (2-8 minutes). Test the full user journey.

### What to check

| Check | Why |
|-------|-----|
| Full pipeline execution | Start to finish, not just individual endpoints |
| Status progression | Verify intermediate states, not just final result |
| Result validation | Check that output has expected structure and content |
| Persistence verification | Confirm results are stored and retrievable |

### Pattern: Status progression tracking

Track every status you see during a long-running operation. Assert you saw
intermediate states, not just the final "complete." If you only see "complete,"
the status writes are failing silently.

```python
statuses_seen = set()
deadline = time.time() + timeout
while time.time() < deadline:
    status, body = get(f"/api/status/{key}")
    if status == 200:
        current = body.get("status")
        if current not in statuses_seen:
            print(f"  Status: {current}")
            statuses_seen.add(current)
        if current == "complete":
            break
    time.sleep(5)

assert len(statuses_seen) > 1, "Only saw final status — intermediate writes may be failing"
```

### Pattern: Consecutive failure detection

If you get N consecutive failures (e.g., 404s), something is fundamentally broken.
Fail fast instead of waiting for the full timeout.

```python
consecutive_404s = 0
while time.time() < deadline:
    status, _ = get(f"/api/status/{key}")
    if status == 404:
        consecutive_404s += 1
        if consecutive_404s >= 3:
            fail("3 consecutive 404s — database writes are likely failing")
    else:
        consecutive_404s = 0
    time.sleep(5)
```

---

## Layer 4: Visual E2E — Does It Render?

Run conditionally (only when frontend changes). Uses Playwright with headless Chromium.

### What to check

| Check | Why |
|-------|-----|
| Page loads without JS errors | Catches broken imports, missing modules |
| Key elements render | Confirms components mount and display |
| Screenshots at key stages | CI artifacts for debugging failures |
| Console error capture | Non-fatal but logged for investigation |

### Pattern: Bridge mock for embedded UIs

If your UI runs inside another context (iframe, extension, embedded app), inject
a mock before the page loads that simulates the host environment.

```typescript
// Playwright: inject before page scripts run
await page.addInitScript(() => {
  window._TEST_MODE = true
  // Mock the host environment's API
  window.addEventListener('message', (e) => {
    if (e.data.type === 'auth_request') {
      e.source.postMessage({ type: 'auth_response', token: 'test-token' }, '*')
    }
  })
})
await page.goto('/sidebar')
```

### Pattern: Screenshot at key stages

Capture screenshots at auth, loading, progress, and final states. Upload as CI
artifacts with configurable retention.

```yaml
# GitHub Actions
- name: Upload screenshots
  if: always()
  uses: actions/upload-artifact@v4
  with:
    name: test-screenshots
    path: tests/screenshots/
    retention-days: 14
```

---

## Layer 5: Unit Tests — Does the Algorithm Work?

For pure functions with complex logic (text search, matching, scheduling).
Use the project's native test framework (vitest, unittest, pytest).

### Pattern: Dynamic import to avoid heavy dependencies

If your function lives in a file with heavy imports (Flask, Supabase client),
extract just the function body for testing without loading the framework.

```python
# Load only the functions we need, not the whole module
with open("api_endpoint.py") as f:
    source = f.read()
# Extract function definitions via exec()
namespace = {}
exec(source_subset, namespace)
build_index_map = namespace["_build_full_text_and_index_map"]
```

---

## CI Pipeline Structure

### Recommended flow

```
lint (always, fast)
  |
  v
deploy (if lint passes)
  |
  +---> smoke (always after deploy, <30s)
  +---> e2e (always after deploy, 2-8m)
  +---> visual-e2e (conditional: only if frontend changed)
```

### Conditional visual tests

Only run Playwright browser tests when frontend files change. Saves CI minutes.

```yaml
# In lint job: detect frontend changes
- name: Check frontend changes
  id: changes
  run: |
    if git diff HEAD~1 HEAD --name-only | grep -qE '\.(html|css|tsx|jsx)$|static/'; then
      echo "frontend_changed=true" >> $GITHUB_OUTPUT
    fi

# In visual-e2e job: skip if no frontend changes
visual-e2e:
  needs: [lint, deploy]
  if: needs.lint.outputs.frontend_changed == 'true'
```

### Parallel test jobs

Run smoke, E2E, and visual E2E in parallel (they're independent). Fail the
pipeline if any fails.

---

## Environment Variables

### Convention

| Variable | Purpose | Example |
|----------|---------|---------|
| `BASE_URL` or `CF_URL` | Target URL for tests | `https://app.example.com` |
| `API_KEY` or `SIDEBAR_API_KEY` | Auth token for protected routes | (from CI secrets) |
| `TEST_DOC_ID` / `TEST_USER_ID` | Stable test fixtures | (from CI secrets) |
| `E2E_TIMEOUT_S` | Configurable timeout | `360` (default) |
| `PLAYWRIGHT_BASE_URL` | Playwright-specific base URL | (falls back to prod URL) |

### Pattern: Environment-driven base URL with sensible default

```typescript
const BASE_URL = process.env.PLAYWRIGHT_BASE_URL || 'https://www.example.com'
```

```python
CF_URL = os.environ.get("CF_URL", "")
assert CF_URL, "CF_URL environment variable required"
```

---

## Checklist: New Project Test Setup

Copy this checklist when setting up tests for a new project.

- [ ] **Lint script** — syntax validation + silent catch detection (bare minimum)
- [ ] **Health endpoint** — `GET /health` returns 200 with status JSON
- [ ] **Smoke test** — hit health, static pages, and protected routes
- [ ] **Auth sweep** — list all protected routes, assert 401 without token
- [ ] **Database roundtrip** — write a canary record, read it back
- [ ] **CI pipeline** — lint -> deploy -> smoke -> e2e (parallel where possible)
- [ ] **Screenshots** — upload Playwright screenshots as CI artifacts
- [ ] **Conditional visual** — only run browser tests on frontend changes
- [ ] **Test email/user suppression** — prevent test runs from spamming real channels
- [ ] **Configurable timeouts** — env vars for all timeout values
