# ADR: Job source adapters
**Status:** Accepted

## Context
HireMe AI needs a production-oriented but interview-defensible portfolio architecture.

## Decision
Source-specific behavior sits behind a stable adapter interface.

## Alternatives
Reasonable alternatives are documented in `docs/ARCHITECTURE.md` and component-specific docs.

## Why chosen
It gives the needed capability with the least unjustified complexity.

## Why alternatives were rejected
They add scope, operational burden, or weaker explicit control for the current scale.

## Consequences
The choice simplifies the MVP but creates explicit future migration triggers.

## When to reconsider
Reconsider when measured scale, UX, latency, reliability, or organizational requirements invalidate the present tradeoff.
