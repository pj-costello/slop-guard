# Decision Preferences

Defaults for architectural trade-offs where both sides are legitimate.
Unlike [RULES.md](RULES.md) (things AI should never do), these are preferences
that guide decisions when there's a genuine choice.

Reference this file in your project's `CLAUDE.md` or equivalent:
```markdown
**Decision preferences**: See https://github.com/pj-costello/slop-guard/blob/main/PREFERENCES.md
```

Override any preference in your project's own rules when the context demands it.

---

## Architecture

### Prefer DRY, but not before the third occurrence

Extract shared logic rather than duplicating it. But don't abstract prematurely --
duplication is far cheaper than the wrong abstraction (Sandi Metz). Wait until you
see the same pattern three times, and only extract when the duplicated things change
for the same reasons.

```python
# TWO occurrences -- tolerate the duplication
def handle_slack_event(event):
    user = event.get("user", "unknown")
    ...

def handle_api_request(request):
    user = request.get("user", "unknown")
    ...

# THREE occurrences, same shape, same reason to change -- now extract
def extract_user(data):
    return data.get("user", "unknown")
```

### Prefer flat file structure (with a size limit)

One directory, one file per responsibility. No `src/`, `lib/`, or nested packages.
Everything is one import away.

Caveat: this works well up to ~50 files. Beyond that, group by domain (not by type).
If you find yourself scrolling past 50 files, it's time to introduce subdirectories.

### Prefer plain functions and module constants over classes

Use module-level functions and constants when both approaches work. Reserve classes
for when you genuinely need state management, protocol implementations, or resource
lifecycle control.

```python
# PREFER this
SAFE_VARS = {"TIMEOUT", "MODEL"}
def evaluate(error_type, fix_type) -> dict:
    ...

# NOT this (when a function would suffice)
class PolicyEvaluator:
    def __init__(self, config):
        self.config = config
    def evaluate(self, error_type, fix_type) -> FixDecision:
        ...
```

---

## Error Handling

### Prefer typed exceptions over string matching

Define a typed exception hierarchy with `error_type` (machine-readable) and
`user_message` (plain English) baked in. Classify errors in one place.

```python
# PREFER this
class DocumentNotFoundError(ReviewAgentError):
    error_type = "doc_not_found"
    user_message = "Could not find this document. Check the sharing settings."

# NOT this
except Exception as e:
    if "404" in str(e):
        ...
```

### Separate user-facing messages from technical diagnosis

Every error should carry two narratives: what we tell the user (ELI5) and what
we tell ourselves (eng diagnosis with IDs, timestamps, stack context).

### Annotate every silent failure

If you swallow an exception, annotate it: `# INTENTIONAL: <reason>`. If you
can't articulate the reason, you shouldn't be swallowing it.

---

## Configuration

### Prefer env vars over config files

Pull configuration from `os.environ`. Secrets from your cloud provider's secret
manager. Operational parameters (timeouts, concurrency, chunk sizes) are env vars
with sensible defaults so they're tuneable per environment without code changes.

Caveat: if you exceed ~30 env vars, group related values into a single JSON secret
to avoid sprawl.

---

## Process

### Prefer empirical rules over theoretical guardrails

Don't add lint rules, policies, or guardrails preemptively. Add them after a real
bug ships. Each rule should trace to an actual incident. The bug history becomes
the executable spec.

```python
# Every lint rule has provenance
# Catches: deploy failures #96, #97 (unicode escape in triple-quoted strings)
def check_python_syntax():
    ...
```

### Review the plan before writing the code

For non-trivial work, write the plan first and review it (or have it reviewed)
before implementing. Catching a design flaw in a plan is 10x cheaper than catching
it in code review, and 100x cheaper than catching it in production.

### Prefer the simplest mechanism that works

When choosing between approaches, pick the one with fewer moving parts. Fetch at
runtime over git submodules. Push-to-main deploy over manual scripts. A flat
function over a class hierarchy.

Accept the trade-off: simpler systems have simpler failure modes, which are easier
to debug even when they do fail.

---

## Responsiveness

### Return immediately, process asynchronously

When integrating with external systems (Slack, webhooks, APIs with tight timeouts),
return the HTTP response immediately and process the work in a background thread.
Respect upstream SLAs -- don't make the caller wait for your internal work.
