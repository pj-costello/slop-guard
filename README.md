# slop-guard

Anti-AI-slop rules, portable lint checks, decision preferences, lessons learned, review and cleanup workflows, and a self-updating scanner.

## What is AI slop?

AI coding assistants produce predictable anti-patterns: over-abstraction, unnecessary comments, defensive over-engineering, kitchen-sink dependencies, test files shipped to production, scope creep into untouched files, and plausible diffs whose requirement context and proof claims are missing. Left unchecked, these patterns compound into bloated, fragile codebases and force reviewers to reconstruct intent from output alone.

This repo provides ten things to fight it:

1. **[RULES.md](RULES.md)** -- Anti-slop rules with concrete do/don't examples, organized by category
2. **[rules.json](rules.json)** -- Machine-readable rule index used to keep rules, sources, lint coverage, and CI checks synchronized
3. **[PREFERENCES.md](PREFERENCES.md)** -- Architectural decision defaults (DRY, flat structure, typed exceptions, etc.) with caveats for when not to apply them
4. **[LESSONS.md](LESSONS.md)** -- Techniques proven effective across real sessions; complements RULES.md (what not to do) and PREFERENCES.md (how to decide)
5. **[TESTING.md](TESTING.md)** -- Reusable testing playbook: layered test patterns, starter templates, and a new-project checklist
6. **[REVIEW_PACKET_TEMPLATE.md](REVIEW_PACKET_TEMPLATE.md)** -- Trace requirement, source authority, assumptions, implementation map, proof claims, and staleness triggers for non-trivial AI-generated diffs
7. **[lint/slop_lint.py](lint/slop_lint.py)** -- Portable **Python** lint checks (stdlib only). [RULES.md](RULES.md) applies to any stack; the bundled linter is a small automated subset, not a full match to every rule.
8. **[Scanner skill](.claude/skills/slop-scanner/)** -- A Claude Code skill that runs the slop-scanner process (phased scan, distillation, MECE audit). **Schedule in your own environment** (e.g. twice weekly Mon + Thu); the repo only ships the skill, not a cron.
9. **[/thermo-nuclear-code-quality-review](.claude/commands/thermo-nuclear-code-quality-review.md)** -- A comprehensive review command for correctness, security, performance, operability, and maintainability.
10. **[/deslop](.claude/commands/deslop.md)** -- A focused cleanup command for removing known AI slop from an existing branch, diff, or file set.

## MECE review system

Use the tools together, but keep their responsibilities separate:

| Layer | Owns | Does not own | Primary artifact |
|-------|------|--------------|------------------|
| Slop Guard rules | AI-specific anti-patterns and generated-code failure modes | Full codebase architecture review | `RULES.md`, `lint/slop_lint.py` |
| Review packet | Requirement/source/proof/staleness traceability for a change | Finding new code-quality issues | `REVIEW_PACKET_TEMPLATE.md` |
| Thermo-nuclear review | Comprehensive engineering review of a branch or diff | Maintaining the anti-slop rule catalog or performing cleanup | `.claude/commands/thermo-nuclear-code-quality-review.md` |
| Deslop | Focused cleanup/remediation of known slop in an existing change | Discovering new rules or broad architecture review | `.claude/commands/deslop.md` |
| Slop scanner | Discovering and proposing new anti-slop rules from sources | Reviewing a specific PR's correctness or cleaning a branch | `.claude/skills/slop-scanner/` |

This keeps the system MECE: slop guard defines known AI slop, the review packet preserves context and proof, thermo-nuclear review audits the actual change, `/deslop` remediates known slop, and the scanner evolves the rule catalog.

## How it stays current

**In this repo** you get: versioned rules, machine-readable index, lint checks, review/cleanup commands, and the scanner skill. **Out of repo** you may add your own automations; nothing here runs on a server unless you wire it up.

Two complementary *conceptual* pipelines keep the content fresh:

**External scanner** (recommended schedule: **twice weekly, Mon + Thu** when using automation) -- searches curated web sources for new AI anti-patterns:

| Tier | Sources | Frequency |
|------|---------|-----------|
| 1 -- Primary | Greptile Blog, Simon Willison, HN Algolia API | Every scan |
| 2 -- Secondary | r/ExperiencedDevs, Smithery.ai, general web sweep | Every scan |
| 3 -- Deep reads | ArXiv, Qodo Report, fast.ai | Monthly (first week) |

**Session distiller** (manual or optional automation, not shipped in this repo) -- scans session transcripts for internal learnings: user corrections, production bugs, and techniques that worked. A daily cadence is one option; the implementation is not part of this repository.

Every finding passes through a structured distillation pipeline (filtering criteria, mandatory do/don't examples, source provenance) and a MECE audit that checks category balance, overlap, and gaps. Nothing is auto-committed — all proposals require human review.

See [SOURCES.md](SOURCES.md) for the full watchlist, provenance for every rule, and rationale for source selection.

## Reproducible / pinned consumption

- **Slop-lint and rules in CI:** Point raw URLs at a **tag** or **commit SHA** instead of `main` when you need stable behavior across environments, e.g. `https://raw.githubusercontent.com/trisouro/slop-guard/v0.1.0/lint/slop_lint.py` after you [create a release](https://github.com/trisouro/slop-guard/releases) on the commit you want.
- **Loose / always current:** The examples below use `main` to track the latest rules and lint.

## Quick start

### Use the rules

Reference `RULES.md` in your project's `CLAUDE.md`, `.cursorrules`, or equivalent AI assistant config:

```markdown
**Anti-slop rules**: See https://github.com/trisouro/slop-guard/blob/main/RULES.md
**Decision preferences**: See https://github.com/trisouro/slop-guard/blob/main/PREFERENCES.md
```

### Validate the rule index

Run the rule/source/index consistency check before changing `RULES.md`, `SOURCES.md`, or `rules.json`:

```bash
python3 scripts/validate_rule_index.py
```

CI runs this check to ensure every `RULES.md` heading is represented in `rules.json` and referenced in `SOURCES.md`.

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
- **Python syntax validation** (ERROR) -- flags files that cannot be parsed as UTF-8 Python
- **Silent catches** (ERROR) -- flags `except: pass` / `except: ...` without `# INTENTIONAL: <reason>`
- **Test files outside test directories** (ERROR) -- flags test artifacts in production paths
- **Trivial docstrings** (WARN) -- flags docstrings that just restate the function name
- **Catch-log-reraise** (WARN) -- flags try/except that only logs and re-raises
- **Empty files** (WARN) -- flags Python files with no meaningful code
- **Source-string slicing** (WARN) -- flags triple-quote string slicing that extracts raw Python source
- **Generic error messages** (WARN) -- flags low-context messages such as `Invalid input`
- **Speculative logging** (WARN) -- flags routine `info`/`debug` narration such as `Entering ...`

### Rule coverage matrix

The bundled linter intentionally covers only portable, low-false-positive checks. Use `SOURCES.md` for the full rule/source/enforcement index.

| Enforcement | Rules |
|-------------|-------|
| Automated ERROR | Python syntax validation; silent catches; test files outside test directories |
| Automated WARN | trivial docstrings; catch-log-reraise; Python files with no meaningful code; source-string slicing; generic error messages; speculative logging |
| Review packet | Context & Proof rules: requirement traceability, source authority, proof matching, staleness |
| Manual review | architecture, scope, dependency, asset, accessibility, DOM, and quality-over-velocity rules |

### Use the scanner

If you use Claude Code, the `/slop-scanner` skill searches curated sources for new AI code criticism and proposes additions to RULES.md.

### Use /deslop

Use [`/deslop`](.claude/commands/deslop.md) when a branch or diff already contains known AI slop and needs focused cleanup against `RULES.md`. It should remove or simplify existing slop; it should not discover new rules or perform a full thermo-nuclear review.

### Use the review packet

For non-trivial AI-generated changes, copy [REVIEW_PACKET_TEMPLATE.md](REVIEW_PACKET_TEMPLATE.md) into your PR description or task handoff. The packet prevents review-by-reconstruction by making the requirement, admitted sources, assumptions, proof claims, and staleness triggers explicit.

### Fetch at lint time (auto-updating)

For projects that want to always run the latest checks without manual updates:

```python
import importlib, tempfile, urllib.request, os
SLOP_URL = "https://raw.githubusercontent.com/trisouro/slop-guard/main/lint/slop_lint.py"
try:
    with urllib.request.urlopen(SLOP_URL, timeout=10) as r:
        code = r.read()
    tmp = tempfile.NamedTemporaryFile(suffix=".py", delete=False)
    tmp.write(code); tmp.close()
    spec = importlib.util.spec_from_file_location("slop_lint", tmp.name)
    slop = importlib.util.module_from_spec(spec); spec.loader.exec_module(slop)
    os.unlink(tmp.name)
    # Now use: slop.check_trivial_docstrings(root), slop.check_catch_log_reraise(root), etc.
except Exception as e:
    print(f"Slop Guard remote fetch skipped: {e}")  # Optional remote checks unavailable.
```

## Origins

Inspired by @Gregorein's viral audit of garryslist.org (2.7M views) which cataloged what 78K lines of AI-generated code looks like in production: 6.42 MB homepage, 169 requests, test files served to visitors, 78 unused controllers, and a rich text editor on a read-only page.

## Contributing

Run `python3 scripts/validate_rule_index.py`, `python3 -m unittest discover -s tests`, and `python3 lint/slop_lint.py .` before you push; CI runs the same.

Open a PR to add new rules. Each rule must include:
- A concrete do/don't example
- The origin (external link or dated internal incident source that motivated it)

Rules must be actionable and specific. Vague platitudes like "write clean code" don't belong here.
