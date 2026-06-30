# Keystone Research Module

## Core principle
Research is evidence gathering before action. Inspect available material first, preserve source quality, separate facts from assumptions, and stay read-only unless the user explicitly asks for a durable research artifact.

## Load when
Load when the user asks to read, inspect, summarize, inventory, extract, compare, explain, investigate options, gather technical or market context, validate claims, or answer “what is true here?” before a decision.

## Not for
- Implementing, refactoring, editing, or fixing code.
- Shaping product direction beyond evidence-backed options.
- Broad tooling risk audits; use `health`.
- Root-cause repair of a failure; use `debug` after initial context.
- Guessing when evidence can be inspected.

## Outcome contract
Deliver a research brief that states:
- question or decision being supported;
- sources inspected, with file paths, commands, URLs, or other citations;
- source-quality notes (primary vs secondary, current vs stale, authoritative vs anecdotal);
- findings separated from assumptions and unknowns;
- confidence level and why;
- recommended next module, or `none` if no Keystone handoff is warranted.

## Modes
- **Repository read:** inspect files, history, configs, tests, docs, and existing behavior. Prefer primary project evidence.
- **External research:** compare outside documentation, standards, issues, market examples, or APIs. Cite URLs and note recency.
- **Synthesis:** combine several sources into a decision-ready summary with tradeoffs and confidence.
- **Discovery scout:** map a large unknown area without drawing strong conclusions until evidence is sampled.

## Process
1. Restate the research question and the decision it informs.
2. Inspect before asking: search/read the repo, docs, logs, or provided sources before requesting more context.
3. Prefer primary evidence: source code, tests, product docs, official docs, reproducible commands, direct user-provided material.
4. Track citations as you go. Every important claim should point to evidence or be labeled as an assumption.
5. Evaluate source quality: age, authority, completeness, bias, and whether evidence is direct or inferred.
6. Compare alternatives when relevant, including costs, risks, constraints, and implications of taking no action.
7. State unknowns explicitly. Do not fill gaps with confident-sounding speculation.
8. Recommend the smallest next step: `shape`, `debug`, `health`, `breakdown`, `build`, `review`, or stop.

## Subagents and reasoning
Use read-only subagents when the search space is large or evidence can be gathered independently. Use lightweight analysis for narrow file summaries and deeper analysis when findings affect architecture, security, safety, release decisions, legal/market claims, or irreversible product direction. When delegation is available, encode required evidence depth and risk standard in the prompt. Subagents must remain read-only unless the user requested an artifact.

## Hard rules
- No mutation by default: do not edit files, run formatters, or alter state except harmless read-only commands.
- Durable artifact exception: if the user requests a research artifact, confirm the path and scope before writing; hand off to `build` when the artifact changes product/code behavior or touches broader project structure.
- Cite evidence for material claims; if evidence is unavailable, say so.
- Distinguish facts, interpretations, assumptions, and recommendations.
- Do not ask for information that can be inspected first.
- Do not present search results or model knowledge as authoritative without source-quality caveats.

## Failure modes
- **Context theater:** long summaries without citations or decision relevance.
- **Source laundering:** treating blogs, stale docs, or guesses as facts.
- **Premature shaping:** deciding product behavior before evidence is clear.
- **Mutation creep:** “just fixing” or rewriting while researching.
- **Hidden uncertainty:** omitting confidence, unknowns, or contradictory evidence.

## Worked example
Good research finding: “Official Stripe docs show idempotency keys apply per unique key and preserve the first result, including failures; this means retrying payment capture should reuse the original key, not generate a new one. Confidence: High — primary docs, current page.”

Bad research finding: “Stripe probably handles retries safely, so we can just retry the request.”

## Output format
```markdown
## Research brief
Question: ...

### Evidence inspected
- `path/or/source`: what it shows, quality note

### Findings
- Fact — citation
- Interpretation — citation + reasoning

### Assumptions / unknowns
- ...

### Options or implications
- ...

### Confidence
High/Medium/Low — why

### Recommended next step
Module or `none`, with rationale

### Checkpoint
- Current module: ...
- Completed gates/checks: ...
- Next required: `<module|none>`
- Next check: ...
- Action: continue now / ask user / pending pointer / stop
- Prompt or handoff pointer: ...

```
