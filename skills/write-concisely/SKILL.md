---
name: write-concisely
description: Write or revise code, documentation, and user-facing replies to be brief, direct, and precise without losing meaning. Use when the user asks for concise, tightened, no-fluff, plain-language, or Elements of Style-inspired output.
metadata:
  layer: capability
---

# Write Concisely

Apply this guidance to all content authored during the task unless the user limits it to a specific file or deliverable.

## Standard

Communicate the complete meaning in the fewest words or lines that remain clear and maintainable.

- Preserve facts, behavior, requirements, constraints, caveats, tone, and intent.
- Put the main point, outcome, or action first.
- Prefer concrete words, active constructions, and direct statements.
- Remove repetition, filler, throat-clearing, empty transitions, and commentary that adds no information.
- Combine overlapping points. Delete a point only when the remaining text still carries its full meaning.
- Keep necessary context, evidence, warnings, examples, and qualifications.
- Match the audience's knowledge and the user's requested tone. Concise does not mean abrupt, vague, or impersonal.
- Favor easy comprehension over the smallest possible word or line count.

Correctness, safety, explicit user instructions, and required formats outrank brevity.

## Code

- Write the smallest clear implementation that fully meets the requirement.
- Prefer straightforward control flow, descriptive names, and existing project conventions.
- Remove dead code, duplication, unnecessary abstraction, and redundant comments when they are within scope.
- Keep comments that explain intent, tradeoffs, invariants, or non-obvious constraints. Do not narrate self-evident syntax.
- Do not compress code into clever expressions, dense one-liners, or premature abstractions.
- Preserve public behavior, error handling, validation, observability, compatibility, and tests unless the task explicitly changes them.
- Do not expand the refactor beyond the requested scope merely to make adjacent code shorter.

## Documentation

- Lead with what the reader needs to know or do.
- Use short sections and lists only when they improve scanning or expose structure.
- Replace abstract or inflated wording with specific language.
- Remove duplicated explanations and details already made obvious by the code, interface, or surrounding text.
- Preserve prerequisites, commands, examples, edge cases, warnings, ownership, and acceptance conditions when they affect correct use.
- Do not reduce precise technical language to a shorter but less accurate approximation.

## Chat Replies

- Answer the question or report the outcome in the opening sentence.
- Do not restate the user's request unless doing so resolves ambiguity.
- Include reasoning, steps, caveats, and tool details only when they help the user decide, verify, or act.
- Use the minimum formatting needed for readability. Avoid decorative headings and fragmented bullet lists.
- Omit generic praise, canned acknowledgements, repeated conclusions, and automatic offers to do more.
- Retain warmth and tact where the situation calls for them.

## Final Pass

Before delivering:

1. Remove every word, sentence, code path, comment, or section that contributes no distinct value.
2. Replace indirect phrasing with direct phrasing.
3. Compare the result with the source or request and restore anything whose removal changed meaning, behavior, scope, or tone.
4. Stop editing when further compression would reduce clarity, accuracy, maintainability, or usefulness.
