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

Only use env vars / config for values that genuinely differ between environments. If a feature is always on, it's just code.

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

### Preserve error specificity

Every error message should include concrete context: what was attempted, relevant IDs, the actual error. Generic messages defeat debugging.

```python
# BAD
raise ValueError("Invalid input")

# GOOD
raise ValueError(f"Could not parse document {doc_id}: expected JSON, got {content_type}")
```

---

## Quality over Velocity

### Review every AI-generated diff before committing

AI tools amplify whatever process feeds them. Without review, they amplify mistakes.

*Origin: Gregorein: "nobody told them to stop."*

### Bundle size matters

Audit what ships to users. A newsletter site should not be 6.42 MB across 169 requests when Hacker News does the same job in 12 KB across 7 requests.

### Don't ship what you don't understand

If you can't explain why a module exists, delete it. If you can't explain what a function does, rewrite it or remove it.
