---
name: design-handoff
description: Turns a design (screenshots, a Figma link, or a description of a screen or flow) into a developer handoff spec covering states, behavior, edge cases, tokens and accessibility, with open questions listed instead of guessed. Use when someone asks for handoff notes, a spec for engineering, or "what am I missing" on a design.
---

# Design handoff

Write the spec an engineer needs to build a screen without coming back with questions. The value is in what static mockups leave out: states, edge cases, behavior and copy.

## Workflow

```
- [ ] 1. Look at everything you were given
- [ ] 2. Inventory the screen
- [ ] 3. Walk every state
- [ ] 4. Fill in template.md
- [ ] 5. List open questions
```

**1. Look at everything.** Screenshots, Figma frames (use the Figma tools if connected), and any notes. Write down what the screen is for in one sentence. If you can't, ask before going further.

**2. Inventory the screen.** List each element top to bottom: what it is, what it shows, and where its data comes from. Note any value that should come from design tokens (color, type size, spacing, radius) and use the token name if the project has tokens.

**3. Walk every state.** For the screen and for each interactive element, check what the design shows and what it leaves out:

- Empty, loading, partial, error, and success states
- Very long text, very short text, missing images, 1 item and 1,000 items
- Hover, focus, pressed and disabled for every control
- What happens on slow networks, on retry, and when the user leaves mid-way
- Small screens and large screens
- For AI features: what the user sees before the AI acts, while it works, when it's wrong, and how they undo it

**4. Fill in `template.md`.** Keep it short and scannable. Use tables for states and elements. Write exact copy for every string, including errors and empty states, following the ux-copy skill if it's available.

**5. List open questions.** Anything the design doesn't answer goes in Open questions with a suggested default, never a silent guess. Mark which ones block building.

## Rules

- Describe behavior, not implementation. Say "the list keeps its scroll position after saving", not which hook to use.
- Every interactive element has a keyboard path and a visible focus state. Every image has alt text or is marked decorative.
- Contrast for text is at least 4.5:1, or 3:1 for large text. Flag anything that misses.
- No em dashes in the spec.
