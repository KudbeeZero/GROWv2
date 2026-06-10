# Correctness & Anti-Rework Playbook for GROWv2

> Produced by the "board of advisors" research pass (2026-06-10). How elite engineering orgs achieve
> high correctness and low rework, and a prioritized plan to apply it here.

## Part 1 — What the best do
**A. Make correctness automatic (gates, not goodwill)**
- Layered, exhaustive automated testing is the foundation — SQLite ships ~590× more test code than
  core code at 100% branch coverage; the suite, not heroics, is what makes it trustworthy.
  (sqlite.org/testing.html)
- Property-based testing finds bugs example tests miss — assert invariants, the framework generates
  thousands of cases and *shrinks* failures to a minimal reproducer. (hypothesis.works)
- Fast, balanced CI feedback (DORA) — speed and stability rise together, not as a trade-off.
  (cloud.google.com/blog four-keys)

**B. Make illegal states impossible**
- Design by Contract (Meyer/Eiffel): explicit pre/postconditions + invariants surface violations at
  the boundary. (eiffel.com)
- Pure/functional style makes state explicit — Carmack: most flaws come from not understanding all
  possible states; pure functions bound inputs/outputs. (sevangelatos.com)
- NASA/JPL "Power of Ten": simple control flow, bounded loops, checked returns. (spinroot.com P10)

**C. Reduce variables you have to debug**
- "Choose Boring Technology" — spend innovation tokens sparingly; boring tech's failure modes are
  already understood. (mcfunley.com)
- Determinism kills rework — Google: ~16% of suite is flaky, 84% of pass→fail transitions are flaky;
  hermetic deterministic tests recovered ~8% of dev time. Flaky tests train engineers to ignore red.

**D. Catch defects at the cheapest moment**
- Small, single-purpose, fast-reviewed changes (Google's top review practice).
- Trunk-based dev + CI (short-lived branches) avoids merge-hell rework.
- Style/readability enforced automatically, not debated.

## Part 2 — Adopt in GROWv2 (prioritized by payoff/effort)
GROWv2 already does a lot right: hand-rolled property/invariant tests (`tests/test_properties.py`),
a ratcheting coverage gate (`pyproject.toml`, ~78%), deterministic mock providers + per-test isolated
SQLite (`conftest.py`), `balance.yaml` as a tuning surface, compute-on-read determinism, faucet/sink
named in `ledger.py`, single-Alembic-head check, memory-integrity gate. The gaps are about turning
good instincts into enforced gates.

1. **Make the lint gate real (High / ~1h).** CI + Makefile run only `ruff check --select=E9,F63,F7,F82`
   (syntax-only). Switch to ruff defaults + `I` (imports) + `B` (bugbear), checked-in `ruff.toml`.
2. **Adopt Hypothesis for ledger + genetics invariants (High / ~½d).** Port the 4 hand-rolled
   properties to `@given` for generation + shrinking + a saved-failure DB. Add `hypothesis` to
   `requirements-dev.txt`.
3. **Codify "every faucet has a sink" as a test (High / ~1d).** Assert every economy `LedgerEntryType`
   is classified faucet|sink (no unclassified), plus a long-run sim property: drive N random
   player-days and assert total money supply stays within bounds (no runaway inflation).
4. **Add a mypy gate, core-first (High / ~1d).** Start over `economy/`, `genetics/`, `simulation/`
   (`--ignore-missing-imports`, non-strict), ratchet scope like coverage. Consider
   `Money = NewType('Money', Decimal)` to stop raw floats reaching the ledger.
5. **Run CI smarter (Medium / ~30m).** Workflows trigger on push+PR to `**` (full suite twice per WIP
   push). Trigger full CI on PR + default-branch pushes; gate slow `e2e` behind `paths:`/label.
6. **Pre-commit config mirroring CI (Medium / ~30m).** ruff (lint+format), EOF/trailing-whitespace,
   `scripts/check_single_head.py` — catch before push.
7. **Harden e2e; treat flakes as bugs (Medium / ongoing).** `retries:2` can mask real regressions —
   surface retried-but-passed (flaky) tests and triage. Assert backend health deterministically in the
   start script. (We already hit and fixed one such flake — the dashboard pod-name strict-mode match.)
8. **Pre-merge checklist + keep PRs small (Medium / ~1h).** `.github/pull_request_template.md`: tests
   added, invariants considered (ledger/genetics), `balance.yaml` over code for tuning, memory docs
   updated, single Alembic head.
9. **Raise the coverage ratchet deliberately; prioritize branch coverage on core (Low–Med / ~15m+).**
   Bump the floor; report coverage on `economy/`/`genetics/`/`simulation/` specifically.

**Keep doing:** deterministic mock providers, isolated-DB fixtures, compute-on-read purity,
`balance.yaml`, single-Alembic-head check, memory-integrity gate.

### Suggested sequence
Today: 1, 5, 6, 9 (all <1h, pure setup). This week: 2 and 3 (highest correctness payoff for the
money/genetics core). Then 4 and 8. Treat 7 as ongoing hygiene.

> Practical note for *this* team: the biggest single correctness lever right now isn't on this list —
> it's not shipping while exhausted. Items 1–3 + 6 exist precisely so a tired human can't merge a
> regression the gates would have caught.
