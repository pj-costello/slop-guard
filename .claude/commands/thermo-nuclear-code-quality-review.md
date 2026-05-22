# /thermo-nuclear-code-quality-review

Run this command when you need a comprehensive engineering review of a branch, PR,
or substantial diff. It complements Slop Guard; it does not replace the slop rule
catalog or scanner.

## MECE boundary

- **Slop Guard owns:** known AI-generated-code anti-patterns, rule provenance, and
  portable lint checks.
- **Review packet owns:** requirement/source/proof/staleness traceability for a
  specific change.
- **Thermo-nuclear review owns:** whether the change is correct, safe, maintainable,
  operable, and fit for the product and architecture.
- **/deslop owns:** focused remediation of known slop after it has been identified.
- **Slop scanner owns:** proposing new anti-slop rules from external or internal
  evidence.

If a finding is known slop, report it and recommend `/deslop` for remediation. If
it is a recurring AI-slop pattern not covered by existing rules, separately propose
a Slop Guard rule through the scanner workflow.

## Review protocol

1. Identify the review target: current branch, merge-base diff, PR URL, or explicit
   file list.
2. Read the review packet if present. If absent for non-trivial work, flag that as
   a reviewability risk.
3. Inspect the diff and relevant surrounding code. Do not limit review to changed
   lines when behavior depends on nearby contracts.
4. Run the cheapest relevant checks available locally, such as unit tests, lint,
   type checks, or targeted smoke tests.
5. Produce findings first, ordered by severity. Include file/line references, the
   failure mode, and the concrete consequence.
6. Separate confirmed issues from open questions, residual risks, and optional
   cleanup.

## Review checklist

Use these categories exactly once; do not duplicate the same concern across
categories.

| Category | Review question |
|----------|-----------------|
| Requirement fit | Does the change implement the requested outcome and preserve non-goals? |
| Correctness | Are edge cases, state transitions, concurrency, and error paths handled? |
| Contracts | Are API, schema, type, permission, and persistence contracts preserved? |
| Security & privacy | Are secrets, auth boundaries, injection risks, data exposure, and auditability safe? |
| Reliability & operability | Are retries, timeouts, idempotency, observability, and rollback behavior adequate? |
| Performance & scale | Does the change avoid N+1 work, excess bundle size, slow paths, and avoidable resource use? |
| UX & accessibility | For user-facing changes, does the journey render correctly and remain accessible? |
| Test adequacy | Do tests prove the claims at the right layer, including failure modes? |
| Maintainability | Is the design simple, localized, and consistent with existing architecture? |
| Slop Guard compliance | Does the diff violate any rule in `RULES.md` or executable slop lint? |

## Output format

```markdown
# Thermo-Nuclear Code Quality Review

## Findings

### [Severity] Title
- Location: path:line
- Problem: ...
- Consequence: ...
- Recommendation: ...

## Open questions / assumptions

## Checks run

## Residual risk
```

If no issues are found, say so explicitly and list remaining test gaps or residual
risk.
