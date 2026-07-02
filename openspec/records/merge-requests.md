# Merge request chronicle

Auto-generated chronicle of merged pull/merge requests. Each entry captures
when work landed and the reasoning recorded in the merge description.
Regenerate with:

```bash
python3 ~/Projects/skills/brain-bootstrap/generate-openspec-mr-chronicle.py \
  --repo-path /Users/patrick.costello/Projects/slop-guard
```

### 2026-05-22 — #4: Add context and proof guardrails
**Link:** https://github.com/pj-costello/slop-guard/pull/4
**Author:** pj-costello

- Add a Context & Proof rule category covering orphan diffs, proof/claim matching, scoped source authority, staleness triggers, and frame-mismatch escalation.
- Add a review packet template for non-trivial AI-generated changes.
- Extend the testing playbook and scanner skill to recognize proof obligations and workflow artifact examples.
- Fix linter review gaps: Python syntax errors now fail, catch-log-reraise allows translated exceptions, empty/scaffold Python files are detected, and duplicate test-file findings are deduplicated.
- Add regression coverage for the linter fixes and pin CI to Python 3.12.
- Reconcile scanner monthly cadence, local file reads, provenance indexing, and session-derived source handling.
- Add `/thermo-nuclear-code-quality-review` and document the MECE boundary across Slop Guard, review packets, scanner, comprehensive code review, and cleanup.
- Add `/deslop` as the focused remediation workflow for removing known slop without overlapping scanner or thermo-nuclear review responsibilities.
- Add `rules.json` as the machine-readable rule index and `scripts/validate_rule_index.py` to enforce RULES/SOURCES/index consistency in CI.
- Add lint checks for source-string slicing, generic error messages, speculative logging, and silent catches without `# INTENTIONAL:`.
- Split error-handling/observability rules into their own category to keep the rule taxonomy MECE.

### 2026-04-23 — #3: CI, tests, catch-log-reraise fix, and documentation/source alignment
**Link:** https://github.com/pj-costello/slop-guard/pull/3
**Author:** pj-costello

This change implements the review follow-ups: clearer boundaries between in-repo content and external automation, tighter source-to-rule traceability, stronger lint tests, and two Gregorein-backed rules that were only cited in SOURCES before.

### 2026-04-23 — #2: Add 6 lessons distilled from April 2026 session review
**Link:** https://github.com/pj-costello/slop-guard/pull/2
**Author:** pj-costello

Lessons distilled from a manual retrospective review of 32 session JSONL files across 21 worktrees (2026-04-01 to 2026-04-20). All entries trace to specific session evidence.

### RULES.md (2 new rules)
- **Don't extract Python strings via naive source slicing** — recurring production bug where `\\u2713` appears as literals instead of `✓` in output; user noted "I've seen this many times"
- **Don't assert exact counts of AI-generated items in tests** — non-deterministic outputs make exact-count assertions flaky without real regressions

### PREFERENCES.md (3 new preferences)
- **Share status at every pause** — strongest signal in all session data; every session showed 5–15 unprompted "status?" messages and explicit corrections
- **Execute plans end-to-end without mid-plan check-ins** — explicit correction across multiple sessions; don't pause between steps waiting for "go ahead"
- **Feature-flag risky experimental features during testing** — SI panel broke prod repeatedly requiring full reverts; distinct from the "no feature flags for stable features" rule

### LESSONS.md (1 new entry, seeds the file)
- **Verify a fix in production before declaring it done** — for cloud-deployed systems with auth/iframe/Apps Script dependencies that can't be replicated locally

### 2026-04-20 — #1: Add LESSONS.md — positive techniques catalog
**Link:** https://github.com/pj-costello/slop-guard/pull/1
**Author:** pj-costello

Companion to RULES.md (anti-patterns) and PREFERENCES.md (decision styles). Populated by the lessons-distiller scheduled task from raw session captures. Starts as a flat list; categories emerge from evidence after 10-15 entries.

---

_Generated 2026-07-02 20:56:07 UTC. 4 merged PR/MR(s) captured._
