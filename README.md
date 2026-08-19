# Agent Oracle: an AI agent orchestration design skill

[![CI](https://github.com/AlveeeRahman/agent-oracle/actions/workflows/ci.yml/badge.svg)](https://github.com/AlveeeRahman/agent-oracle/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org/downloads/)

<!-- seo:readme:begin  generated from .github/repository-metadata.yml by .github/seo/seo.py; edit the manifest, not this block -->
**Documentation**: [alveeerahman.github.io/agent-oracle](https://alveeerahman.github.io/agent-oracle/)

Python 3.10+ (tested on 3.10, 3.11, 3.12, 3.13) · 2 runnable scripts · no network access from any bundled script · MIT licensed

Part of a three-skill suite: [Skill Vision](https://alveeerahman.github.io/skill-vision/) · **Agent Oracle** (you are here) · [Research Hound](https://alveeerahman.github.io/research-hound/)

<!-- seo:readme:end -->

**agent-oracle** is an AI agent orchestration design skill — an [Agent Skill](https://code.claude.com/docs/en/skills) for Claude Code that governs how autonomous agent systems get built: how many agents a task actually needs, what stops a loop before it burns budget on nothing, and what a harness has to lock down before it can run unattended. Every invocation starts by answering those questions first, using evidence from published research and NVIDIA's own harness-engineering guidance, not by guessing.

## Get it running

```bash
# All your projects (personal skill):
git clone https://github.com/AlveeeRahman/agent-oracle.git ~/.claude/skills/agent-oracle

# Or one project only (shareable with your team through git):
git clone https://github.com/AlveeeRahman/agent-oracle.git .claude/skills/agent-oracle
```

Python 3.10+, standard library only, no network calls from the bundled scripts. Then ask Claude in your own words:

> *"Design the supervisor topology for this pipeline."*
> *"Write the launch prompt for this long-running research agent."*
> *"Build a regression suite before I ship this agent change."*
> *"agent-oracle: take this system from idea to production."*

## Why an orchestrator, not a prompt

Most agent guidance reads like a checklist a person is supposed to remember mid-build. agent-oracle enforces the checklist instead. Before any of the five segments below get touched, the request goes through a fixed orchestrator step that answers four questions and states the answers out loud:

1. **Scope**: does this belong to one segment, or does it span the whole pipeline?
2. **Agent count**: one agent, or several, and why?
3. **Loop design**: does this need a loop, and what actually stops it?
4. **Harness controls**: which surfaces are locked, and how is the budget enforced?

Each answer is grounded in a specific section of a specific guide, not improvised. A narrow request ("write my launch prompt") gets a one-line answer and moves straight into that guide. A long-running or multi-agent request gets a written decision citing the topology, the bound, and the budget, before a single worker starts. The orchestrator step itself is bounded: it produces one decision and hands off. It does not loop, and it does not spawn help to make up its mind, because a decision step that costs more than the task it's deciding about has failed at the one job it has.

## How it saves tokens

Two mechanisms do most of the work, both backed by outside sources rather than house opinion.

**Default to one agent.** Under a fixed thinking-token budget, splitting work across agents adds serialization and re-summarization steps that can only lose information relative to one agent reasoning over the same tokens directly. That's a Data Processing Inequality argument, not a rule of thumb (Tran and Kiela, arXiv 2604.02460). Multi-agent systems only became competitive when a single agent's context was already degraded, or when meaningfully more compute was spent on purpose. agent-oracle's orchestrator treats multi-agent as something you justify, not something you default to.

**Pass results by reference, not by value.** Tool results held as live objects in the execution environment, with the model reading a bounded, typed preview instead of a full serialized dump round-tripped through context on every turn, reported a near-halving of token cost at equal or better accuracy on SWE-bench Verified: 82.2% at roughly 1.1M tokens versus 78.2% at 2.2M tokens for a comparison harness (NVIDIA, "Six Agent Harness Capabilities for Higher Model Performance"). It also removes the need for context compaction, since the full result never enters context to begin with.

Resource budgets are treated as a formal contract, not a suggestion: token, tool-call, iteration, wall-clock, and cost limits, with a breach on any single dimension ending the run. Delegated budgets follow a conservation rule, where the sum of every child agent's budget cannot exceed the parent's (Ye and Tan, "Agent Contracts," arXiv 2601.08815).

## How it resolves loops

The failure mode this skill spends the most guidance on isn't a missing termination check. It's a termination check that exists but doesn't cover the actual feedback path: a retry cap on one tool call with nothing capping the outer loop that keeps calling it, growing message history with no cap on total tool calls. A static analysis of 6,549 repositories found 68 confirmed infinite-loop failures across 47 of them, and most trace back to exactly that shape: a local bound that never reaches the loop it was meant to stop (Hou, Wang, Zhao, and Wang, "When Agents Do Not Stop," arXiv 2607.01641).

agent-oracle's harness guide classifies every loop's continuation controller before trusting it: deterministic (a fixed count, a hard timeout), model-controlled, tool-controlled, external-state-controlled, exception-controlled, or mixed. Only the deterministic kind is a real bound. A visible exit conditioned on model output is not one, because the model is exactly the component known to drift, retry, or reinterpret "done."

Enforcement then splits into two modes, and anything that runs unattended needs the harder one. Soft enforcement is budget-aware prompting: cooperative, and documented to fail under "token elasticity," where agents ignore or exceed limits stated only in the prompt. Hard enforcement is an external monitor tracking consumption after every action, halting independent of whether the agent cooperates. In the paper's own experiment, an external monitor caught and halted an agent mid-run after it had consumed 56,000 tokens against a 40,000-token allocation. The paper's introduction also cites a third-party report, not its own data, as motivation: two agents stuck in a recursive clarification loop with no stop condition ran for eleven days and produced a \$47,000 bill before anyone noticed (arXiv 2601.08815).

## The five segments

| # | Segment | Guide | Answers |
|--:|---|---|---|
| 1 | Evaluation | `guides/evaluation.md` | What does success look like, and how do you measure it without a single number hiding the failure? |
| 2 | Multi-agent patterns | `guides/multi-agent-patterns.md` | Does this need more than one agent, and if so, what topology and what budget contract? |
| 3 | Harness engineering | `guides/harness-engineering.md` | What's locked, what's editable, what terminates the loop, and who has to approve what? |
| 4 | Long-horizon prompting | `guides/long-horizon-prompting.md` | How do you write a launch brief that survives a run long enough to need one? |
| 5 | Self-improvement loops | `guides/self-improvement-loops.md` | What happens when the harness itself is the thing being optimized? |

Evaluation comes first because every later segment optimizes against whatever metric segment 1 defines, gaps included. Multi-agent topology comes before the harness and the brief because both depend on how many agents are actually running. Self-improvement comes last because it's the only segment that edits the machinery the other four built, and it needs a locked signal and defined surfaces to edit against safely.

The sequence loops. An evaluation that can't distinguish two configurations is an evaluation problem, not a topology problem, and going back to fix it is the system working as intended, not a sign something went wrong.

## What's new in v1.1.1

**Both bundled scripts were demos, not CLIs.** They ignored `argv` and ran a hardcoded
scenario. Running `evaluator.py --help` printed a demo, not help text. The documentation
said to run these tools, and what shipped could only be read.

They are real tools now, built on the library that was already underneath them.
`evaluator.py` scores a JSON test set against a weighted rubric. It takes `--tests`,
`--demo`, `--json`, `--verbose`, and `--min-pass-rate` for use as a CI gate, and reports a
malformed test file by naming the bad field instead of raising a traceback.
`coordination.py` runs a deterministic scenario across supervisor registration, the handoff
protocol, weighted consensus, and retry-budget failure handling, with `--workers`,
`--voters`, `--failures`, `--max-retries` and `--json`. Both still run with no arguments if
you want to see the shape of the output first. Under `script_tester.py` they went from
PARTIAL to PASS.

**Every reference file is one link hop from SKILL.md.** All seven sat behind a guide.
Anthropic's authoring guidance calls that out, because past one hop an agent previews a
file with `head -100` instead of reading it, so the end never lands. A short index in
SKILL.md links each one directly, with a line on what it covers.

**Names in the guides that are not files here are marked as such.** The composed guides
route to `tool-design`, `hosted-agents`, `memory-systems` and others from the upstream
repository. None of them are bundled. An agent following that advice used to go looking for
a file that does not exist. SKILL.md now says plainly that anything written as a path is
bundled, and anything else is a separate skill to install.

**Description cut from 959 characters to roughly 530**, which is 94% of the hard limit down
to about half. That field loads into the system prompt of every session whether the skill
triggers or not, and it competes with every other skill's metadata for selection attention.
The segment names and trigger words are all still there.

Tables of contents were added to the five reference files over 100 lines. CI now audits
documentation claims against the code and checks that every CLI answers `--help`.

## What's in the box

- **`SKILL.md`**: the orchestrator logic and segment routing Claude loads on trigger.
- **`guides/`**: one guide per segment, each with Core Concepts, Detailed Topics, Guidelines, Gotchas, and cited External Resources.
- **`references/`**: dated evidence backing the guides: metrics, framework code, annotated prompts, and per-system research findings with citations.
- **`scripts/`**: two standard-library CLIs: `scripts/evaluation/evaluator.py` and `scripts/multi-agent-patterns/coordination.py`. Both take `--help` and `--json`, and run with no arguments for a worked example.

## License

[MIT License](LICENSE). The original composed guides carry their upstream copyright (Context Engineering Agent Skills Contributors, 2025). Local additions in this repository follow the same terms.
