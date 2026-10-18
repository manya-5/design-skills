# [Screen or flow name]

**What it's for:** One sentence on the job this screen does for the user.
**Design:** Link to the frames
**Status:** Draft, ready for review, or ready to build

## Elements

| Element | Shows | Data from | Notes |
|---|---|---|---|
| Page title | "Projects" | Static | `--text-xl`, serif |
| Project list | Name, owner, last edited | `GET /projects` | Sorted by last edited |

## States

| State | When | What the user sees | Copy |
|---|---|---|---|
| Loading | First load | Skeleton rows, no spinner | None |
| Empty | No projects | Illustration and one button | "No projects yet. Create one to get started." Button: "Create project" |
| Error | Request fails | Inline message above the list | "Couldn't load projects. Check your connection and try again." Button: "Try again" |

## Behavior

- What happens on each action, in order, including what changes on screen.
- Anything that animates, with duration and what it communicates.
- What is kept or lost if the user leaves mid-way.

## Edge cases

- Long names truncate after one line with a tooltip showing the full name.
- 1,000+ items: the list paginates at 50.

## Accessibility

- Keyboard order:
- Focus states:
- Screen reader labels:
- Contrast issues found:

## Open questions

| Question | Suggested default | Blocks build? |
|---|---|---|
| What happens when a shared project is deleted by its owner? | Show it as removed with an explanation | Yes |
