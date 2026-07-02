## Summary

<!-- What changed. This body becomes the permanent record in
     openspec/records/merge-requests.md — write for the future reader. -->

## Why

<!-- Motivation. For rules/lessons: which sessions or sources taught this.
     For linter changes: the false positive/negative being fixed. -->

## Test plan

- [ ] Rule index valid (`python3 scripts/validate_rule_index.py` — CI enforces)
- [ ] Self-lint green (`python3 lint/slop_lint.py .` — CI enforces)
- [ ] Unit suite green (`python3 -m unittest discover -s tests` — CI enforces)

## Deploy impact

<!-- Merge = publication: ship-it and review skills consume rules from main.
     Call out rule renames/removals that consumers reference. "None" is fine. -->
