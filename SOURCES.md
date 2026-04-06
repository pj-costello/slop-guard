# Sources

Every rule in [RULES.md](RULES.md) traces back to a real-world critique, audit, or incident.
This file tracks the provenance.

---

## Primary Sources

### @Gregorein -- garryslist.org audit (Mar 31, 2026)

**Thread:** https://x.com/Gregorein/status/2038953944475472316 (2.7M views)

Audited garryslist.org after creator bragged about 37K LOC/day and a 72-day shipping streak.
Findings:
- 6.42 MB homepage, 169 HTTP requests (vs Hacker News: 12 KB, 7 requests)
- 28 test files shipped to production as HTTP 200 responses (300 KB)
- 78 unused Stimulus controllers (154 KB transferred, none used on homepage)
- Same logo served 8 times: 3 PNG, 2 WebP, 2 AVIF, 1 favicon -- including a 0-byte failed AVIF conversion
- Uncompressed PNGs: 2.07 MB + 1.99 MB despite browser requesting modern formats
- 520 KB Trix rich text editor loaded on a read-only page
- 47 images with empty alt tags
- Page content rendered twice in DOM, duplicate head tags
- Empty CSS file, Rails scaffold "Hello World" controller
- Analytics proxy to bypass ad blockers on a 501(c)(4) nonprofit site

**Rules informed:** No test artifacts in production, No kitchen-sink dependencies, No unoptimized assets, No dead code, Bundle size matters, Review every diff, Don't ship what you don't understand

### @bradgessler -- "AI slop is cope" response (Apr 3, 2026)

**Tweet:** https://x.com/bradgessler/status/2040218273510543571 (56.5K views)

Argued that "AI slop" criticism is cope -- AI just optimizes what you tell it. This actually reinforces the need for explicit rules: if AI optimizes your instructions, give it anti-slop instructions.

**Rules informed:** Framing of the entire ruleset -- tell AI what NOT to do

---

## Secondary Sources

### Greptile -- "AI Slopware" blog post
**URL:** https://www.greptile.com/blog/ai-slopware-future

Discusses the trajectory of AI-generated code quality and the "tragedy of the commons" where individual productivity gains create collective tech debt.

**Rules informed:** LOC is not a metric, Quality over velocity

### Variant Systems -- "10 Anti-Patterns in AI-Generated Codebases"
**URL:** https://variantsystems.io/blog/vibe-code-anti-patterns

Catalogs specific anti-patterns including over-abstraction, unnecessary wrapper classes, and speculative generality.

**Rules informed:** No over-abstraction, Don't create files for one-off functions

### Medium -- "Defensive Code, Dangerous Data"
**URL:** https://medium.com/data-mess/defensive-code-dangerous-data-the-hidden-bias-of-ai-coding-assistants-2336179ff51b

Analysis of how AI coding assistants are biased toward defensive programming patterns (excessive try/catch, redundant validation, 8x more I/O operations) because of training data skew toward web/API contexts.

**Rules informed:** No catch-log-reraise, No speculative logging

### Stack Overflow -- "Code Smells for AI Agents"
**URL:** https://stackoverflow.blog/2026/02/04/code-smells-for-ai-agents-q-and-a-with-eno-reyes-of-factory/

Q&A identifying AI-specific code smells including over-commenting, scope creep, and the tendency to add features nobody asked for.

**Rules informed:** Terse comments, Don't touch code outside scope, No feature flags for non-configurable things

### Jose Casanova -- AI Code Slop Reviewer Prompt
**URL:** https://www.josecasanova.com/prompts/ai-code-slop-reviewer

A reviewer prompt specifically designed to catch AI slop patterns in pull requests.

**Rules informed:** General review framework

---

## Adding Sources

When adding a new rule to RULES.md, add the source here with:
- URL and date
- Brief summary of the finding
- Which rules it informed
