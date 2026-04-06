# slop-guard

Anti-AI-slop rules, portable lint checks, and a scanner for discovering new patterns.

## What is AI slop?

AI coding assistants produce predictable anti-patterns: over-abstraction, unnecessary comments, defensive over-engineering, kitchen-sink dependencies, test files shipped to production, and scope creep into untouched files. Left unchecked, these patterns compound into bloated, fragile codebases.

This repo provides three things to fight it:

1. **[RULES.md](RULES.md)** -- A living catalog of anti-slop rules with concrete do/don't guidance
2. **[lint/slop_lint.py](lint/slop_lint.py)** -- Portable Python lint checks you can import into any project
3. **[Scanner skill](.claude/skills/slop-scanner/)** -- A Claude Code skill that discovers new patterns weekly

## Quick start

### Use the rules

Reference `RULES.md` in your project's `CLAUDE.md`, `.cursorrules`, or equivalent AI assistant config:

```markdown
**Anti-slop rules**: See https://github.com/pj-costello/slop-guard/blob/main/RULES.md
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

### Use the scanner

If you use Claude Code, the `/slop-scanner` skill searches the web for new AI code criticism and proposes additions to RULES.md.

## Origins

Inspired by @Gregorein's viral audit of garryslist.org (2.7M views) which cataloged what 78K lines of AI-generated code looks like in production: 6.42 MB homepage, 169 requests, test files served to visitors, 78 unused controllers, and a rich text editor on a read-only page.

See [SOURCES.md](SOURCES.md) for the full list of critiques and incidents behind each rule.

## Contributing

Open a PR to add new rules. Each rule must include:
- A concrete do/don't example
- The origin (link to the critique, incident, or thread that motivated it)

Rules must be actionable and specific. Vague platitudes like "write clean code" don't belong here.
