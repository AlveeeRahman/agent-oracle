# Security policy

## Supported versions

The latest tagged release is the supported one. Fixes land on `main` and ship in the
next tag; there are no long-lived maintenance branches.

## Reporting a vulnerability

Report privately through GitHub's
[private vulnerability reporting](https://github.com/AlveeeRahman/agent-oracle/security/advisories/new)
rather than a public issue, and give it a few days for a first response.

Useful things to include: what an attacker gets, the smallest input that shows it, and
the Python version you saw it on.

## What this skill does with your data

agent-oracle is guidance plus two local CLIs. Nothing in it opens a network
connection: `scripts/evaluation/evaluator.py` and
`scripts/multi-agent-patterns/coordination.py` are standard-library only and run
offline.

`.github/repository-metadata.yml` records the same thing as
`network_surfaces: []`, so a change to what leaves the machine has a single place to
be written down.

## A note on what this skill advises

agent-oracle recommends harness controls for autonomous agents: locked surfaces,
approval boundaries, loop bounds, rollback paths. Following its advice does not make
an agent safe on its own. In particular:

- A loop bound only counts if it covers the feedback path that actually repeats, not
  just an inner retry.
- Approval boundaries are only real if the agent cannot route around them.
- An agent granted write access to its own harness can remove the controls you added.
  The self-improvement segment says this explicitly; treat acceptance gates on
  self-modifying systems as a hard requirement, not a suggestion.

## Scope

In scope: arbitrary code execution, path traversal, or credential disclosure from
running the bundled scripts on untrusted input.

Out of scope: the behaviour of agent systems you build using this guidance, the
accuracy of Claude's own output, and anything requiring an attacker who already has
write access to your machine.
