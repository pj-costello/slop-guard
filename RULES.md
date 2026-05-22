# Slop Guard Rules

Concrete rules preventing common AI-generated code anti-patterns.
Each rule links to the real-world critique or incident that motivated it (see [SOURCES.md](SOURCES.md)).

---

## Code Bloat

### No docstrings on obvious functions

A function named `get_db` that returns a database client does not need `"""Get the database client."""`. Only add docstrings when the function has non-obvious behavior, the signature doesn't explain the args, or it's a public API called from other files.

```python
# BAD
def get_db():
    """Get the database client."""
    return _db

# GOOD
def get_db():
    return _db
```

### No over-abstraction

Don't create class hierarchies, strategy patterns, or factory methods for things that work as plain functions. Three similar lines of code is better than a premature abstraction.

```python
# BAD
class FixPolicyEvaluator:
    def __init__(self, config: FixConfig):
        self.config = config
    def evaluate(self, error_type, fix_type) -> FixDecision:
        ...

# GOOD
SAFE_CONFIG_VARS = {"TIMEOUT", "MODEL"}
def evaluate(error_type, fix_type, fix_proposal) -> dict:
    ...
```

### No feature flags for non-configurable things

Only use env vars / config for values that genuinely differ between environments. If a feature is always on, it's just code. For risky experimental features, use the separate feature-flag preference in `PREFERENCES.md` and remove the flag after validation.

```python
# BAD
ENABLE_ERROR_CLASSIFICATION = os.environ.get("ENABLE_ERROR_CLASSIFICATION", "true")

# GOOD -- just call it, it's always on
classify_error(e)
```

### Terse functional comments only

Comments explain WHY, not WHAT. No section headers, no emoji, no `TODO: Consider...`.

```python
# BAD
# ===== ERROR HANDLING SECTION =====
# TODO: Consider adding retry logic here
# This function processes the review and returns results

# GOOD
# Map Python log levels to Cloud Logging severity
```

---

## Error Handling & Observability

### No try/except that only logs and re-raises

Catching an exception just to log it and re-raise adds noise and defeats structured error handling. Let exceptions propagate to where they're actually handled.

```python
# BAD
try:
    result = store_review(data)
except Exception as e:
    logger.error(f"Failed to store review: {e}")
    raise

# GOOD
result = store_review(data)
```

Exception: Use try/except when you need a specific fallback, need to translate the exception type, or need to add context the handler wouldn't have.

### No speculative logging

Log errors and state transitions. Don't log routine operations.

```python
# BAD
logger.info("Entering evaluate_review")
logger.info("About to call Firestore")
logger.info("Successfully stored review")

# GOOD
logger.error("review_store_failed", extra={"doc_id": doc_id, "error": str(e)})
```

### No silent catches without an intentional reason

Do not swallow exceptions with `pass` or `...` unless the handler explains why the failure is safe to ignore. Use `# INTENTIONAL: <reason>` on the handler when silence is deliberate.

```python
# BAD
try:
    cleanup_temp_file(path)
except FileNotFoundError:
    pass

# GOOD
try:
    cleanup_temp_file(path)
except FileNotFoundError:  # INTENTIONAL: cleanup is idempotent; file may already be gone
    pass
```

### Preserve error specificity

Every error message should include concrete context: what was attempted, relevant IDs, the actual error. Generic messages defeat debugging.

```python
# BAD
raise ValueError("Invalid input")

# GOOD
raise ValueError(f"Could not parse document {doc_id}: expected JSON, got {content_type}")
```

---

## Scope Creep

### Don't touch code outside the task scope

If you're fixing a bug in `router.py`, don't add type hints to `client.py`, reorganize imports in `config.py`, or rename variables in unrelated files.

### Don't re-introduce removed code

If something was deleted, it was deleted deliberately. Don't create backwards-compat shims, re-export removed types, or add `# removed` comments.

### Don't create new files for one-off functions

Before creating `helpers.py`, `utils.py`, or `common.py`, check if the function belongs in an existing file. The bar for a new file: 3+ functions AND a distinct responsibility not covered by any existing file.

### LOC is not a metric of progress

A 5-line fix that eliminates a class is better than a 200-line refactor. Measure outcomes, not volume. Never brag about lines of code generated.

---

## Production Hygiene

### No test artifacts in production paths

Test files, fixtures, and mocks must stay in `tests/` or equivalent. Never ship test code to users.

*Origin: Gregorein audit found 28 test files served as HTTP 200 responses to visitors.*

### No kitchen-sink dependencies

Don't add libraries, controllers, or modules that the current page/endpoint doesn't use. Every dependency shipped to users must earn its place.

*Origin: Gregorein audit found 78 unused Stimulus controllers and a rich text editor loaded on a read-only page.*

### No unoptimized or duplicate assets

Don't add images without checking format and size. Don't duplicate assets in multiple formats without cleanup. Don't deploy failed conversions (0-byte files).

*Origin: Gregorein audit found the same logo served 8 times in different formats, including a 0-byte failed AVIF conversion, and uncompressed PNGs wasting 4 MB.*

### No dead code or empty files

Don't leave scaffold files, empty stylesheets, or unused modules. If you generate it, it must be used.

*Origin: Gregorein audit found an empty CSS file and a Rails scaffold "Hello World" controller (157 bytes) in production.*

### No empty alt on meaningful images

If an image is not purely decorative, give it a real `alt` (what a screen reader should hear). `alt=""` is only for ornaments; product shots, article figures, and UI that conveys information need descriptive text. Blank alts on content images is a common AI slop default.

```html
<!-- BAD — figure carries information but no description -->
<img src="/editorial-shot.png" alt="">

<!-- GOOD — informative alt, or true decorative + empty with intent -->
<img src="/process-diagram.png" alt="User upload flow: select file, then confirm.">
```

*Origin: Gregorein audit found 47 images with empty alt tags.*

### No duplicate document shell or main content in the DOM

Ship one valid document outline: a single `head` with one title/meta set, and don't render the same page content twice in the tree. Duplicates bloat the DOM, confuse screen readers, and complicate styles.

*Origin: Gregorein audit found page content rendered twice in the DOM and duplicate head tags.*

### Don't extract string content from Python source via string slicing

Reading a Python source file and slicing out a triple-quoted string produces raw Python source, not the interpreted value. Escape sequences like `\\u2713` and `\\n` appear as literals in the output instead of `✓` and newline.

```python
# BAD — reads raw source; \\u2713 stays as two chars, not ✓
with open("sidebar_page.py") as f:
    src = f.read()
html = src.split('"""')[1]   # grabs literal \\u2713, \\n, etc.

# GOOD — import the value through Python, so escapes are interpreted
from sidebar_page import HTML

# BETTER — don't embed HTML in Python source at all; keep it in a .html file
```

*Origin: Recurring production bug across multiple sessions — user noted "I've seen you share this finding with double backslashes many times."*

---

## Quality over Velocity

### Review every AI-generated diff before committing

AI tools amplify whatever process feeds them. Without review, they amplify mistakes.

*Origin: Gregorein: "nobody told them to stop."*

### Bundle size matters

Audit what ships to users. A newsletter site should not be 6.42 MB across 169 requests when Hacker News does the same job in 12 KB across 7 requests.

### Don't ship what you don't understand

If you can't explain why a module exists, delete it. If you can't explain what a function does, rewrite it or remove it.

### Don't assert exact counts of AI-generated items in tests

AI outputs are non-deterministic. Asserting that a model returns exactly N items ties tests to one snapshot of one model's behavior, making CI flaky without any real regression.

```python
# BAD — breaks whenever the model returns 27 or 29 flags instead of 28
assert len(review_cards) == 28

# GOOD — assert existence and a sanity bound
assert len(review_cards) >= 1
assert len(review_cards) <= 100
```

*Origin: Visual E2E test asserted exactly 28 review cards; user correction: "the agent may return different findings each time it runs since its non deterministic."*

---

## Context & Proof

### No orphan diffs

Every non-trivial AI-generated change must ship with a review packet that ties the diff back to the larger object behind it: requirement, authoritative sources, assumptions, implementation mapping, proof claims, and staleness triggers. A reviewer should not have to reconstruct why the code exists from the diff alone.

```markdown
# BAD
Changed 7 files and added tests.

# GOOD
Requirement: R17 checkout should reject expired promo codes before payment intent creation.
Sources: PRD v3 section 4.2; checkout_api.md#promo-validation.
Assumptions: Promo expiration is evaluated in UTC.
Implementation: `validate_promo` now runs before `create_payment_intent`.
Proof: unit test for expired code; integration test verifies no payment intent is created.
Stale if: PRD v3 section 4.2 or checkout API promo contract changes.
```

### Match the proof to the claim

A passing check only proves the claim it actually exercises. Do not use backend unit tests to claim a user journey works, screenshots to claim durable state exists, or a 200 response to claim product intent is satisfied.

```markdown
# BAD
Claim: Users can complete onboarding.
Evidence: `POST /api/onboarding` returns 200.

# GOOD
Claim: Users can complete onboarding.
Evidence: E2E creates an account, completes the onboarding screens, verifies persisted profile state, and confirms the next-session resume path.
```

### Keep context bundles scoped and authoritative

More context is not automatically better. Before implementation, list the small set of admitted sources, mark which source wins on conflicts, and ignore stale or unauthoritative discussion unless it is promoted into the source set.

```markdown
# BAD
Context used: repo search, old Slack thread, two planning docs, README, and traces.

# GOOD
Authoritative sources:
1. Linear ENG-482 acceptance criteria (owns behavior)
2. `docs/billing-contract.md` (owns API contract)
3. `tests/billing/e2e.test.ts` (owns current proof surface)

Ignored: 2025 Slack brainstorm; superseded by ENG-482.
```

### Record staleness triggers

If the work depends on a requirement, contract, design decision, schema, or external behavior, record what would invalidate the result. When an admitted source changes materially, re-check the impacted work instead of patching around stale assumptions.

```markdown
# BAD
Assumption: The webhook payload always includes `customer.email`.

# GOOD
Assumption: The webhook payload includes `customer.email` because Stripe event contract 2026-04 says it is required.
Stale if: Stripe API version changes, webhook schema changes, or billing switches to customer IDs as the primary identity.
```

### Escalate frame mismatches before coding

Do not write code when the requirement conflicts with an architecture boundary, ownership rule, product promise, or existing source of authority. Surface the mismatch and propose the smallest decision needed before implementing.

```markdown
# BAD
Requirement says "sync invoices in the browser", so add Stripe secret-key calls to the frontend.

# GOOD
Escalation: Browser invoice sync conflicts with secret-key boundary. Need decision: move sync to backend job, or change requirement to client-safe invoice preview.
```

*Origin: Dhasan Dev article on the software factory trap: agents produce syntactically correct but semantically incomplete work when requirement context, source authority, proof obligations, and staleness are not encoded in the workflow.*
