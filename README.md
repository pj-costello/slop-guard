# slop-guard

Anti-AI-slop rules, portable lint checks, decision preferences, lessons learned, and a self-updating scanner.

## What is AI slop?

AI coding assistants produce predictable anti-patterns: over-abstraction, unnecessary comments, defensive over-engineering, kitchen-sink dependencies, test files shipped to production, scope creep into untouched files, and plausible diffs whose requirement context and proof claims are missing. Left unchecked, these patterns compound into bloated, fragile codebases and force reviewers to reconstruct intent from output alone.

This repo provides seven things to fight it:

1. **[RULES.md](RULES.md)** -- Anti-slop rules with concrete do/don't examples, organized by category
2. **[PREFERENCES.md](PREFERENCES.md)** -- Architectural decision defaults (DRY, flat structure, typed exceptions, etc.) with caveats for when not to apply them
3. **[LESSONS.md](LESSONS.md)** -- Techniques proven effective across real sessions; complements RULES.md (what not to do) and PREFERENCES.md (how to decide)
4. **[TESTING.md](TESTING.md)** -- Reusable testing playbook: layered test patterns, starter templates, and a new-project checklist
5. **[REVIEW_PACKET_TEMPLATE.md](REVIEW_PACKET_TEMPLATE.md)** -- Trace requirement, source authority, assumptions, implementation map, proof claims, and staleness triggers for non-trivial AI-generated diffs
6. **[lint/slop_lint.py](lint/slop_lint.py)** -- Portable **Python** lint checks (stdlib only). [RULES.md](RULES.md) applies to any stack; the bundled linter is a small automated subset, not a full match to every rule.
7. **[Scanner skill](.claude/skills/slop-scanner/)** -- A Claude Code skill that runs the slop-scanner process (phased scan, distillation, MECE audit). **Schedule in your own environment** (e.g. twice weekly Mon + Thu); the repo only ships the skill, not a cron.

## How it stays current

**In this repo** you get: versioned [RULES.md](RULES.md) and the scanner skill. **Out of repo** you may add your own automations; nothing here runs on a server unless you wire it up.

Two complementary *conceptual* pipelines keep the content fresh:

**External scanner** (recommended schedule: **twice weekly, Mon + Thu** when using automation) -- searches curated web sources for new AI anti-patterns:

| Tier | Sources | Frequency |
|------|---------|-----------|
| 1 -- Primary | Greptile Blog, Simon Willison, HN Algolia API | Every scan |
| 2 -- Secondary | r/ExperiencedDevs, Smithery.ai, general web sweep | Every scan |
| 3 -- Deep reads | ArXiv, Qodo Report, fast.ai | Monthly (first week) |

**Session distiller** (optional, run in *your* Claude Code or CI context if you set it up) -- scans session transcripts for internal learnings: user corrections, production bugs, and techniques that worked. A daily cadence is one option; the implementation is not part of this repository.

Every finding passes through a structured distillation pipeline (filtering criteria, mandatory do/don't examples, source provenance) and a MECE audit that checks category balance, overlap, and gaps. Nothing is auto-committed — all proposals require human review.

See [SOURCES.md](SOURCES.md) for the full watchlist, provenance for every rule, and rationale for source selection.

## Reproducible / pinned consumption

- **Slop-lint and rules in CI:** Point raw URLs at a **tag** or **commit SHA** instead of `main` when you need stable behavior across environments, e.g. `https://raw.githubusercontent.com/pj-costello/slop-guard/v0.1.0/lint/slop_lint.py` after you [create a release](https://github.com/pj-costello/slop-guard/releases) on the commit you want.
- **Loose / always current:** The examples below use `main` to track the latest rules and lint.

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

### Use the review packet

For non-trivial AI-generated changes, copy [REVIEW_PACKET_TEMPLATE.md](REVIEW_PACKET_TEMPLATE.md) into your PR description or task handoff. The packet prevents review-by-reconstruction by making the requirement, admitted sources, assumptions, proof claims, and staleness triggers explicit.

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

Run `python3 -m unittest discover -s tests` and `python3 lint/slop_lint.py .` before you push; CI runs the same.

Open a PR to add new rules. Each rule must include:
- A concrete do/don't example
- The origin (link to the critique, incident, or thread that motivated it)

Rules must be actionable and specific. Vague platitudes like "write clean code" don't belong here.
