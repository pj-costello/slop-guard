---
name: slop-scanner
description: >
  Scan the web for new AI code anti-patterns and propose additions to RULES.md.
  Use this skill when the user says "scan for slop patterns", "check for new
  anti-patterns", "update slop guard", or invokes /slop-scanner. Also trigger
  on a weekly schedule to keep the rules current.
---

# Slop Scanner

You are updating the slop-guard repo, which maintains a living catalog of
AI-generated code anti-patterns. Your job is to find new patterns that have
emerged in public discourse and propose additions to RULES.md.

## When to use this skill

- User invokes `/slop-scanner`
- Scheduled weekly run (Monday mornings)
- User asks to check for new AI code criticism or anti-patterns

## Workflow

1. **Search** -- WebSearch for recent AI code criticism (last 7 days):
   - "AI generated code anti-patterns"
   - "AI code slop" OR "vibe coding problems"
   - "LLM code quality issues"
   - "AI coding assistant mistakes"
   - "claude copilot cursor code quality"

2. **Read current rules** -- Read `RULES.md` and `SOURCES.md` to understand
   what's already covered. Do not propose duplicates.

3. **Filter** -- For each finding, evaluate:
   - Is it a concrete, actionable pattern? (not a vague complaint)
   - Is it new? (not already in RULES.md)
   - Is it reproducible? (observed by multiple people or well-documented)
   - Does it have a clear do/don't example?
   Reject findings that fail any of these criteria.

4. **Propose** -- For each new pattern that passes filtering:
   - Draft the rule in the format of existing RULES.md entries
   - Include a do/don't code example
   - Note the origin (URL, author, date)
   - Draft the SOURCES.md entry

5. **Output** -- Present findings to the user as a summary:
   - Number of sources searched
   - Number of new patterns found
   - For each new pattern: the rule text, example, and source
   - Ask the user to review before committing

6. **Commit** (only with user approval) -- If the user approves:
   - Add new rules to RULES.md under the appropriate category
   - Add sources to SOURCES.md
   - Commit with message: "Add rule: [rule name] (source: [author/url])"

## Important constraints

- NEVER auto-commit rules without user review
- Each rule must have a concrete do/don't example
- Each rule must link to a real source
- Prefer quality over quantity -- 1 good rule > 5 vague ones
- If no new patterns are found, say so. Don't invent rules.
