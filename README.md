# slop-guard

Anti-AI-slop rules, portable lint checks, decision preferences, and a self-updating scanner.

## What is AI slop?

AI coding assistants produce predictable anti-patterns: over-abstraction, unnecessary comments, defensive over-engineering, kitchen-sink dependencies, test files shipped to production, and scope creep into untouched files. Left unchecked, these patterns compound into bloated, fragile codebases.

This repo provides four things to fight it:

1. **[RULES.md](RULES.md)** -- Anti-slop rules with concrete do/don't examples, organized by category
2. **[PREFERENCES.md](PREFERENCES.md)** -- Architectural decision defaults (DRY, flat structure, typed exceptions, etc.) with caveats for when not to apply them
3. **[lint/slop_lint.py](lint/slop_lint.py)** -- Portable Python lint checks you can import into any project or CI pipeline
4. **[Scanner skill](.claude/skills/slop-scanner/)** -- A Claude Code skill that scans curated sources twice weekly for new patterns

## How it stays current

The scanner runs **twice weekly** (Monday + Thursday) across three tiers of curated sources:

| Tier | Sources | Frequency |
|------|---------|-----------|
| 1 -- Primary | Greptile Blog, Simon Willison, HN Algolia API | Every scan |
| 2 -- Secondary | r/ExperiencedDevs, Smithery.ai, general web sweep | Every scan |
| 3 -- Deep reads | ArXiv, Qodo Report, fast.ai | Monthly (first week) |

Every finding passes through a structured distillation pipeline (5 filtering criteria, mandatory do/don't examples, source provenance) and a MECE audit that checks category balance, overlap, and gaps. Nothing is auto-committed -- all proposals require human review.

See [SOURCES.md](SOURCES.md) for the full watchlist, provenance for every rule, and rationale for source selection.

## Quick start

### Use the rules

Reference `RULES.md` in your project's `CLAUDE.md`, `.cursorrules`, or equivalent AI assistant config:

```markdown
**Anti-slop rules**: See https://github.com/pj-costello/slop-guard/blob/main/RULES.md
**Decision preferences**: See https://github.com/pj-costello/slop-guard/blob/main/PREFERENCES.md
```

### Use the lint checks

Copy `lint/slop_lint.py` into your project, or run it standalone:

```bash
python lint/slop_lint.py /path/to/your/project
```

Or import individual checks:

```python
from slop_lint import check_trivial_docstrings, check_catch_log_reraise

results = check_trivial_docstrings("/path/to/project")
for severity, filepath, message in results:
    print(f"  {severity} [{filepath}]: {message}")
```

Checks included:
- **Trivial docstrings** (WARN) -- flags docstrings that just restate the function name
- **Catch-log-reraise** (WARN) -- flags try/except that only logs and re-raises
- **Test files outside tests/** (ERROR) -- flags test artifacts in production paths
- **Empty files** (WARN) -- flags files with no meaningful code

### Use the scanner

If you use Claude Code, the `/slop-scanner` skill searches curated sources for new AI code criticism and proposes additions to RULES.md.

### Fetch at lint time (auto-updating)

For projects that want to always run the latest checks without manual updates:

```python
import importlib, tempfile, urllib.request, os
SLOP_URL = "https://raw.githubusercontent.com/pj-costello/slop-guard/main/lint/slop_lint.py"
try:
    with urllib.request.urlopen(SLOP_URL, timeout=10) as r:
        code = r.read()
    tmp = tempfile.NamedTemporaryFile(suffix=".py", delete=False)
    tmp.write(code); tmp.close()
    spec = importlib.util.spec_from_file_location("slop_lint", tmp.name)
    slop = importlib.util.module_from_spec(spec); spec.loader.exec_module(slop)
    os.unlink(tmp.name)
    # Now use: slop.check_trivial_docstrings(root), slop.check_catch_log_reraise(root), etc.
except Exception:
    pass  # Graceful fallback -- skip slop checks if network unavailable
```

## Origins

Inspired by @Gregorein's viral audit of garryslist.org (2.7M views) which cataloged what 78K lines of AI-generated code looks like in production: 6.42 MB homepage, 169 requests, test files served to visitors, 78 unused controllers, and a rich text editor on a read-only page.

## Contributing

Open a PR to add new rules. Each rule must include:
- A concrete do/don't example
- The origin (link to the critique, incident, or thread that motivated it)

Rules must be actionable and specific. Vague platitudes like "write clean code" don't belong here.
