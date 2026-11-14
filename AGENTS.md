# PinConv2 project rules

- Level 1 plans. It never generates, downloads, renders or publishes paid media.
- The machine-readable record is the source of truth; Markdown is rendered from it.
- Every plan output is bound to a revision and a content hash.
- Exact commercial fields (price, offer, code, pack art, logo, CTA, claims) bind to an
  exact-data record. Public observation is not approval.
- A named human approves Gate 1. Agents must never record approval on a human's behalf.
- Research separates observation, interpretation and proposed decision. Inaccessible
  channels are recorded as unknown.
- Run `python -m pytest` and `python -m ruff check .` before reporting a change complete.
- Do not add a UI, database, queue or provider integration until a measured need exists.
