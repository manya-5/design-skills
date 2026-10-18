---
name: ux-copy
description: Reviews and rewrites interface copy (buttons, errors, empty states, toasts, onboarding) so it's clear, consistent and in sentence case, using a quick automated check plus a written review. Use when someone shares UI text, a screen, or a strings file and asks to improve the wording.
---

# UX copy review

Make interface text easier to understand and act on. The words are part of the design: each one should help someone know where they are, what will happen, or what to do next.

## Workflow

```
- [ ] 1. Collect the strings
- [ ] 2. Run the checker
- [ ] 3. Review by hand against the principles
- [ ] 4. Return a before and after table
```

**1. Collect the strings.** Use the user's file if there is one (plain text, a JSON strings file, or HTML/JSX). If they shared a screenshot, transcribe every visible string into `strings.txt`, one per line, in reading order.

**2. Run the checker.**

```bash
python scripts/check_copy.py strings.txt
```

It catches the mechanical problems: em dashes, Title Case, vague errors, apologies, "Click here", "Submit", exclamation marks, "please", three dots instead of an ellipsis. Treat its output as a starting list, not the whole review.

**3. Review by hand.** Read the strings as a person moving through the flow and check:

- **Name actions by their result.** A button says what happens: "Save changes", "Send invite". The same action keeps the same name through the flow, so "Publish" leads to a "Published" toast.
- **Errors say what happened and what to do.** "Card declined. Try another card or contact your bank." Not "Something went wrong."
- **Empty states invite action.** "No projects yet. Create one to get started" with a button that says "Create project".
- **Use the user's words, not the system's.** "Notifications", not "Webhook config".
- **Sentence case everywhere**, including buttons and headings.
- **Lead with the important part.** Cut "In order to", "Please note that", "Simply".
- **For AI features, say what will happen before it happens**, who it affects, and how to undo it.
- **No em dashes.** Use a period, comma, colon or parentheses.

Check consistency across the set: the same thing should never have two names.

**4. Return the review** as a table: Location, Before, After, Why (one short reason). Group by screen if there are several. Finish with any naming inconsistencies you found across screens. Don't rewrite strings that are already good; say they're fine.
