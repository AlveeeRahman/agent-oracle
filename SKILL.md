---
name: agent-oracle
description: Context engineering for autonomous agent systems across five segments - evaluation (regression suites, rubrics, quality gates, baselines), multi-agent patterns (supervisor vs swarm, context isolation, handoffs), harness engineering (locked surfaces, durable logs, loop bounds, rollback, approval boundaries), long-horizon prompting (task briefs, success predicates, stop conditions), and self-improvement loops (meta-agent search, acceptance gates). Use when designing, launching, measuring, or debugging any long-running or multi-agent system.
license: MIT (upstream muratcankoylan/Agent-Skills-for-Context-Engineering, MIT)
allowed-tools: Read Edit Write Bash(python3 scripts/*)
compatibility: Python 3.10+ for the two bundled scripts, which are standard-library and run offline. The guidance itself is model- and framework-agnostic; individual segments name specific frameworks where relevant.
metadata:
  version: "1.1.1"
  composed-from: "harness-engineering, evaluation, long-horizon-prompting, multi-agent-patterns, self-improvement-loops (muratcankoylan/Agent-Skills-for-Context-Engineering)"
---

# Agent Oracle

Five segments covering the design of autonomous agent systems: how you measure them, how
you structure them, how you control them, how you launch them, and how you let them
improve themselves.

## Every invocation starts with an orchestrator

Before any segment work begins, hand the request to an orchestrator first — by name or by
segment, this step is not optional and not skippable for a request that looks simple. It is
a fixed, bounded decision that terminates in one answer and hands off; it is not a loop, and
it does not spawn help to decide.

The orchestrator decides four things, in order, each grounded in a specific guide section
rather than improvised:

1. **Scope.** Does the request name a segment or clearly belong to one — "design the
   supervisor topology", "write my launch prompt", "build a regression suite"? Read only
   that guide and do only that work; do not run the other four, do not walk the person
   through the sequence, do not append the next stage uninvited. Does it invoke
   **agent-oracle** generically, or span stages? Work the full sequence below, announcing
   each segment as you enter it, and do not skip one because it looks satisfied. If it is
   genuinely unclear which applies, ask once.
2. **Agent count.** One agent, or several? Default to one: multi-agent beats single-agent
   only when a single agent's context is already degraded, or more compute is deliberately
   spent (`guides/multi-agent-patterns.md`, "The Token Economics Reality" and "Resource
   Contracts for Delegated Budgets"). Multi-agent needs a stated reason, not a default.
3. **Loop design.** Does the work need a loop at all, and if so, what actually terminates
   it? Classify the continuation controller: deterministic, model-controlled,
   tool-controlled, external-state-controlled, exception-controlled, or mixed. State
   the bound before the loop starts, not after it stalls (`guides/harness-engineering.md`,
   "Loop Termination and Bound Coverage"). Only the deterministic kind is a verified bound.
   The rest depend on a component known to drift.
4. **Harness controls.** Which surfaces are locked, editable, append-only, or
   human-controlled, and what resource budget applies across tokens, tool calls,
   iterations, and wall-clock time? State whether enforcement is hard (an external monitor,
   required for anything that runs unattended) or soft (`guides/harness-engineering.md`,
   "Harness Boundary" and "Resource Contracts").

Ceremony scales with the request. A narrow single-segment ask gets a one-line decision — one
agent, no loop, ordinary caution — then proceeds straight into that guide. A long-running,
multi-agent, or self-modifying request gets a written decision citing the specific topology,
bound, and budget chosen, before any worker starts. Spending more tokens on the
orchestration decision than the task itself justifies is the failure this step exists to
prevent, not a side effect to tolerate.

## The sequence

```
1. EVALUATION → 2. MULTI-AGENT → 3. HARNESS → 4. LONG-HORIZON → 5. SELF-IMPROVEMENT
   Define the      Decide the        Build the      Write the         Let the loop
   success         topology, or      control        launch brief      rewrite itself
   predicate       reject it         surfaces       and stop rules    against a locked
                                                                      signal
        └──────────────────────────────────────────────────────────────────┘
              Every stage can invalidate an earlier one. Go back.
```

| # | Segment | Read | You are here when |
| - | ------- | ---- | ----------------- |
| 1 | **Evaluation** | [guides/evaluation.md](guides/evaluation.md) | Defining success, deterministic checks, regression suites, rubrics, quality gates, baselines, production monitoring |
| 2 | **Multi-agent patterns** | [guides/multi-agent-patterns.md](guides/multi-agent-patterns.md) | Deciding whether one agent suffices, supervisor vs swarm, context isolation, handoffs, parallel decomposition |
| 3 | **Harness engineering** | [guides/harness-engineering.md](guides/harness-engineering.md) | Locked vs editable surfaces, durable logs, novelty gates, pruning, rollback, PR preparation, approval boundaries |
| 4 | **Long-horizon prompting** | [guides/long-horizon-prompting.md](guides/long-horizon-prompting.md) | Writing the launch brief, success predicates, non-counting outcomes, persistence and stop conditions, effort floors, return gates |
| 5 | **Self-improvement loops** | [guides/self-improvement-loops.md](guides/self-improvement-loops.md) | The harness itself is the optimization target: RSI, meta-agent search, evolutionary scaffolds, acceptance gates for self-modifying systems |

### Reference material, linked directly

Each guide names these where relevant, but they are linked here too so any of them can
be opened in one step. A file reached only through another file tends to get skimmed
rather than read, and these are the ones whose detail matters:

- **Evaluation** — [metrics.md](references/evaluation/metrics.md): outcome vs process metrics, and what each fails to catch.
- **Multi-agent** — [frameworks.md](references/multi-agent-patterns/frameworks.md): LangGraph, CrewAI, AutoGen, Swarm compared on isolation and handoff.
- **Long-horizon** — [task-brief-template.md](references/long-horizon-prompting/task-brief-template.md): the fill-in brief · [cdc-prompt-annotated.md](references/long-horizon-prompting/cdc-prompt-annotated.md): a real long-horizon prompt, annotated · [research-evidence.md](references/long-horizon-prompting/research-evidence.md) · [vendor-guidance.md](references/long-horizon-prompting/vendor-guidance.md)
- **Self-improvement** — [loop-design-evidence.md](references/self-improvement-loops/loop-design-evidence.md): what published self-improving loops actually measured.

Scripts are run, not read: [evaluation/evaluator.py](scripts/evaluation/evaluator.py) scores runs against a rubric,
[multi-agent-patterns/coordination.py](scripts/multi-agent-patterns/coordination.py) simulates handoff and contention. Both take `--help`.

**Why evaluation comes first.** The segments themselves supply the argument: a
self-improving loop "optimizes whatever signal it is given, including the signal's own
weaknesses," and harness engineering exists partly to stop agents "gaming benchmarks,
weakening rubrics." You cannot lock a metric you have not defined, and every later stage
optimizes against it. Building first and measuring afterwards means discovering that the
thing you built well was the wrong thing.

**Why topology precedes the harness and the brief.** Both the control surfaces and the
launch prompt differ depending on whether one agent or sixty-four are running. Segment 2
also carries permission to answer "one agent is enough" — the cheapest multi-agent system
is the one you correctly decided not to build.

**Why self-improvement is last.** It is the only segment that edits the machinery built by
the others. It needs a locked signal from segment 1 and defined surfaces from segment 3;
run before those exist, it optimizes into a gap.

**The sequence is a loop.** An evaluation that cannot distinguish two configurations is an
evaluation problem, not a topology problem. A brief that keeps producing answer-shaped
near misses sends you back to the success predicate in segment 1. Going backwards is the
system working.

## Segment boundaries worth knowing

**Evaluation vs harness engineering.** Outcome metrics, regression suites, and quality
gates are segment 1. The *control surfaces* around those gates — which are locked, who may
edit them, what happens on rollback — are segment 3. The rubric is evaluation; making the
rubric untouchable by the agent is the harness.

**Harness engineering vs self-improvement loops.** Governing one autonomous loop is
segment 3. Letting a loop rewrite its own scaffold is segment 5. The question shifts from
"how do I control this loop" to "how do I let it modify itself without corrupting the
signal that steers it."

**The orchestrator's one-line decisions vs segments 2 and 3 in depth.** The orchestrator
states an agent count, a bound, a budget, and an enforcement mode in one line each, drawn
from segment 2's and segment 3's checklists without running either in full. Reach for
segment 2 itself to design the actual topology (supervisor vs swarm vs hierarchical,
handoff protocols, isolation mechanism). Reach for segment 3 itself to build a new harness,
add novelty gates and pruning to a research loop, or prepare PRs with an approval boundary.
The orchestrator decides what applies; segments 2 and 3 are where you build it.

**Long-horizon prompting vs multi-agent patterns.** Writing the orchestrator's brief is
segment 4; deciding how many workers there are and how they hand off is segment 2. The
brief assumes the topology is already settled.

## Conventions across all five segments

**Assume the optimizer finds every gap between metric and intent.** This is the load-bearing
principle in this whole domain. Anything you leave unspecified will be exploited, not
through malice but because that is what optimization does.

**Write the stop condition before the start condition.** Long-running systems fail by not
stopping — premature return, or burning hours on an answer-shaped artifact. Specify what
ends the run, what does not count as success, and what to return on failure.

**Durable state beats in-context state.** Anything that must survive compaction, restart,
or a crash belongs in a log or a file, not in the conversation.

**Irreversible actions need an approval boundary.** Decide explicitly which actions an
agent may take alone and which require a human. Silence here defaults to "anything," which
is rarely intended.

**Measure against a baseline, not against nothing.** A configuration that improves on its
own previous run may still be worse than the trivial approach. Keep the baseline runnable.

## What's bundled

```
agent-oracle/
├── guides/                        # one per segment — start here
│   ├── evaluation.md              multi-agent-patterns.md   harness-engineering.md
│   └── long-horizon-prompting.md  self-improvement-loops.md
├── references/
│   ├── evaluation/                # metrics
│   ├── multi-agent-patterns/      # frameworks
│   ├── long-horizon-prompting/    # annotated CDC prompt, task-brief template,
│   │                              # research evidence, vendor guidance
│   └── self-improvement-loops/    # loop-design evidence
└── scripts/
    ├── evaluation/evaluator.py
    └── multi-agent-patterns/coordination.py
```

`harness-engineering` ships as a guide only — it is design guidance with no references or
scripts of its own.

`scripts/evaluation/evaluator.py` and `scripts/multi-agent-patterns/coordination.py`
each take `--help` and `--json`, and both run on the standard library with no network
access. `evaluator.py --demo` and `coordination.py` run end to end with no arguments,
so you can see the shape of the output before wiring in your own data.

The repository also carries `.github/seo/seo.py`, which keeps this project's own README,
Pages site and GitHub metadata in agreement and talks to the GitHub and IndexNow APIs to
do it. It is build tooling, not part of the skill, and nothing here invokes it.

### Names in the guides that are not files here

The guides occasionally route to sibling skills from the upstream repository —
`advanced-evaluation`, `hosted-agents`, `tool-design`, `project-development`,
`memory-systems`, `context-compression`, `context-optimization`. **None of those are
bundled in this package**, and there is no file to open. Treat such a mention as a
suggestion to go and install that skill separately, and otherwise carry on with the
guidance in front of you — do not go looking for the file, and do not report a broken
reference. Anything written as a path (`guides/…`, `references/…`, `scripts/…`) *is*
bundled here.

## Attribution

Composed from five skills in `muratcankoylan/Agent-Skills-for-Context-Engineering`
(MIT): `harness-engineering`, `evaluation`, `long-horizon-prompting`,
`multi-agent-patterns`, and `self-improvement-loops`. Guide bodies are preserved from the
originals, with references to the other four rewritten as internal segment pointers. The
upstream copyright notice is retained in [LICENSE](LICENSE), as MIT requires; the CLI
entry points on both scripts are additions made here.
