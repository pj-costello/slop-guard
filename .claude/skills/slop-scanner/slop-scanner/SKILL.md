---
name: slop-scanner
description: >
  Scan curated high-signal sources for new AI code anti-patterns and propose
  additions to RULES.md. Runs a structured distillation pipeline and MECE audit.
  Use when the user says "scan for slop patterns", "check for new anti-patterns",
  "update slop guard", or invokes /slop-scanner. Scheduled weekly on Mondays.
---

# Slop Scanner

You maintain the slop-guard repo's living catalog of AI code anti-patterns.
Your job: find new patterns from curated sources, distill them rigorously,
and propose additions while keeping the ruleset MECE.

## Phase 1: Read Current State

1. Fetch the current RULES.md from https://raw.githubusercontent.com/pj-costello/slop-guard/main/RULES.md
2. Fetch the current SOURCES.md from https://raw.githubusercontent.com/pj-costello/slop-guard/main/SOURCES.md
3. Count rules per category. Note these counts for the MECE audit later.

## Phase 2: Scan Curated Sources

### Tier 1 — Primary (every run, direct fetch)

**Greptile Blog:**
- WebFetch https://www.greptile.com/blog
- Extract article titles and dates from the last 7 days
- For any new articles about AI code quality, fetch and analyze them
- If WebFetch fails, fall back to: WebSearch `site:greptile.com AI code quality`

**Simon Willison:**
- WebSearch `site:simonwillison.net AI code quality` (last 7 days)
- WebSearch `site:simonwillison.net cognitive debt vibe coding` (last 7 days)
- For any new relevant posts, WebFetch the URL and analyze

**Hacker News (Algolia API):**
- Compute the Unix timestamp for 7 days ago using Bash: `date -v-7d +%s` (macOS) or `date -d '7 days ago' +%s` (Linux)
- WebFetch `https://hn.algolia.com/api/v1/search_by_date?query=AI+code+quality&tags=story&numericFilters=points>10,created_at_i>{TIMESTAMP}`
- Also search: `query=AI+slop` and `query=vibe+coding+problems`
- For stories with >50 points, WebFetch the linked article for deeper analysis

### Tier 2 — Secondary (every run, web search)

**r/ExperiencedDevs:**
- WebSearch `site:reddit.com/r/ExperiencedDevs AI code quality OR AI slop OR vibe coding` (last 7 days)

**Smithery.ai:**
- WebSearch `site:smithery.ai anti-slop code quality`

**General sweep (catches sources not in the watchlist):**
- WebSearch `"AI code anti-pattern" OR "AI code slop" OR "LLM code quality" -site:reddit.com` (last 7 days)
- WebSearch `"AI generated code" problems quality 2026`

### Tier 3 — Quarterly deep reads

Only run if today is within the first 7 days of the month.
Check using Bash: `date +%d` and compare (01-07 = run).

If monthly:
- WebSearch `site:arxiv.org AI generated code quality 2026`
- WebFetch `https://www.qodo.ai/reports/state-of-ai-code-quality/`
- WebSearch `site:fast.ai vibe coding OR AI code`

## Phase 3: Distill Findings

For EVERY candidate finding, fill out this template. Do not skip fields.

```
PATTERN: [one sentence describing the anti-pattern]
OBSERVED BY: [author/source with URL]
FREQUENCY: [single observation / multiple independent / research-backed]
EXAMPLE:
  BAD: [concrete code snippet, 2-5 lines]
  GOOD: [concrete fix, 2-5 lines]
CATEGORY: [Code Bloat | Scope Creep | Production Hygiene | Quality over Velocity | NEW: ___]
EXISTING OVERLAP: [which existing rule(s) it overlaps, or "none"]
VERDICT: [ADD / MERGE with rule "X" / SKIP]
RATIONALE: [why]
```

**Filtering criteria — must pass ALL five:**
1. **Concrete** — describes a specific code pattern, not a vague complaint
2. **Not duplicate** — not already covered by an existing rule in RULES.md
3. **Has source** — links to a real, accessible URL
4. **Has example** — includes a do/don't code snippet
5. **Reproducible** — observed by 2+ people OR well-documented by one credible source

If a finding fails ANY criterion, set VERDICT to SKIP with the reason.

## Phase 4: Draft Proposals

For each finding with VERDICT = ADD:
- Write the full rule text in RULES.md format (heading, explanation, code block)
- Write the SOURCES.md entry (URL, date, summary, rules informed)
- Specify which category it goes under

For each finding with VERDICT = MERGE:
- Show the existing rule text
- Show the proposed merged text
- Explain what's being added

For NEW CATEGORY proposals:
- Must have at least 2 rules to justify a new category
- Propose the category name and description

## Phase 5: MECE Audit

Run this EVERY scan. It is cheap and prevents drift.

Read the full RULES.md (including any proposed additions from Phase 4) and produce:

**Category Balance:**
| Category | Current Rules | After Proposals | Status |
|----------|--------------|-----------------|--------|
| Code Bloat | N | N+X | OK / TOO LARGE (>8) / TOO SMALL (<2) |
| ... | ... | ... | ... |

**Mutual Exclusivity Check:**
- Compare every pair of rules. Flag any two rules that could be interpreted as saying the same thing.
- If found, propose consolidation.

**Collective Exhaustiveness Check:**
- Are there obvious gaps? Consider these domains:
  - Security (hardcoded secrets, injection patterns)
  - Accessibility (missing alt tags, ARIA)
  - Performance (N+1 queries, unoptimized assets)
  - Testing (test quality, not just test location)
  - Documentation (over-documenting vs under-documenting)
- Flag gaps as "potential future categories" — don't create rules for them unless a source supports it.

**Consolidation Opportunities:**
- Any rules that could be merged without losing specificity?

## Phase 6: Output Report

Produce this exact structure:

```
# Slop Scanner Report — [YYYY-MM-DD]

## Scan Summary
- Sources checked: [N]
- Findings before filtering: [N]
- Proposals after filtering: [N ADD + N MERGE]
- Tier 3 quarterly scan: [yes/no]

## Proposals

### Proposal 1: [rule name]
[Full distillation template from Phase 3]
[Drafted rule text from Phase 4]

### Proposal 2: ...

(If no proposals: "No new patterns found this week. All sources checked, nothing met the filtering criteria.")

## MECE Health Report
[Table and checks from Phase 5]

## Source Fetch Log
| Source | Tier | Status | New Findings |
|--------|------|--------|-------------|
| Greptile Blog | 1 | fetched / failed | N |
| Simon Willison | 1 | searched | N |
| HN Algolia | 1 | fetched | N |
| r/ExperiencedDevs | 2 | searched | N |
| Smithery.ai | 2 | searched | N |
| General sweep | 2 | searched | N |
| ArXiv | 3 | skipped (not quarterly) | - |
| Qodo | 3 | skipped (not quarterly) | - |
| fast.ai | 3 | skipped (not quarterly) | - |
```

## Critical Constraints

- **NEVER auto-commit.** All proposals require human review.
- **NEVER invent rules.** Every rule must trace to a real source.
- **"No new patterns" is a valid outcome.** Don't force findings.
- **Quality over quantity.** 1 good rule > 5 mediocre ones.
- **Graceful degradation.** If a source fails to fetch, log it and continue. Never abort the scan.
