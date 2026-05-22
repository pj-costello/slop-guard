# /deslop

Run this command when a branch, diff, or file set already has suspected AI slop
and needs focused cleanup. It is a remediation workflow: remove known slop, keep
behavior stable unless a rule violation requires a small correctness fix, and prove
the cleanup with the cheapest relevant checks.

## MECE boundary

- **Slop Guard rules own:** the catalog of known anti-patterns and portable lint
  checks.
- **/deslop owns:** applying those rules to remove clutter, bloat, generated
  scaffolding, noisy comments/logs, misplaced tests, stale shims, and similar
  cleanup from an existing change.
- **Review packet owns:** requirement/source/proof/staleness traceability for a
  non-trivial change.
- **Thermo-nuclear review owns:** comprehensive engineering review and risk
  assessment.
- **Slop scanner owns:** discovering and proposing new rules from evidence.

If cleanup reveals a new recurring anti-pattern, finish the local cleanup and then
propose a separate scanner finding. Do not expand /deslop into rule-catalog
maintenance or full architecture review.

## Cleanup protocol

1. Identify the cleanup target: current diff, explicit files, or a review finding.
2. Read `RULES.md` and `PREFERENCES.md`; use `SOURCES.md` only when provenance is
   needed to interpret a rule.
3. Classify each issue under one existing rule. If it does not fit an existing
   rule, record it as a possible future scanner finding instead of inventing a new
   rule mid-cleanup.
4. Make minimal, behavior-preserving edits. Prefer deleting unnecessary code over
   wrapping it in compatibility shims.
5. Avoid unrelated formatting churn and broad refactors.
6. Run relevant checks, including `python3 lint/slop_lint.py .` when working in
   this repo or when the lint script is available.
7. Summarize what slop was removed, which rules were applied, and what checks ran.

## Cleanup checklist

| Category | Remove or simplify |
|----------|--------------------|
| Code bloat | Trivial docstrings, over-abstractions, log-and-reraise blocks, noisy comments |
| Scope creep | Unrelated edits, stale compatibility shims, one-off helper files |
| Production hygiene | Misplaced tests, empty/scaffold files, unused dependencies/assets, duplicate DOM/content |
| Quality over velocity | LOC bragging, unexplained modules, brittle AI-output assertions |
| Context & proof | Missing review packet fields, mismatched proof claims, unrecorded staleness triggers |

## Output format

```markdown
# Deslop Report

## Cleanup applied
- [Rule]: [files changed] -- [what was removed/simplified]

## Deferred scanner candidates
- [Pattern not covered by existing rules, if any]

## Checks run
- ...

## Residual risk
- ...
```
