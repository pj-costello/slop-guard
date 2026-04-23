# Lessons Learned

Living catalog of techniques, approaches, and patterns that have proven effective
across Claude Code sessions. Complements RULES.md (what NOT to do) and
PREFERENCES.md (how to make decisions).

Updated by the lessons-distiller scheduled task. All entries trace to real session
observations — nothing is invented.

---

<!-- Entries will be added below as the distiller proposes and human reviews them. -->
<!-- Categories will emerge from evidence after 10-15 entries accumulate. -->

---

## Verification

### Verify a fix in production before declaring it done

**Context:** After implementing a fix for a bug in a cloud-deployed system —
especially one with auth flows, iframe sandboxing, or external API integrations
that can't be fully replicated locally.

**Approach:**
1. Deploy the fix.
2. Exercise the exact broken scenario yourself: same document, same user flow,
   same edge case that originally failed.
3. Confirm the output is correct end-to-end.
4. Only then report "fixed and verified."

**Why it works:** Many bugs in cloud-deployed systems are invisible to local
testing — auth context, iframe sandboxing, Apps Script bridges, model
non-determinism. Claiming "fixed" before verifying in prod creates a frustrating
loop: "still broken" → patch → "still broken."

**Evidence:** Multiple sessions, 2026-04-01 to 2026-04-20. Explicit user
corrections: "don't tell me you've fixed it until you verify yourself that it
works"; "this has been a huge pain...frustrating that there are a lot of things
you're not catching during development."
