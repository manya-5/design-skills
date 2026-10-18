# Layouts

Every slide in `plan.json` has a `layout` and the fields listed here. Character counts are a guide for writing. The builder measures the real text and has the final say.

## title
Opening slide.

| Field | Required | Holds about |
|---|---|---|
| `title` | yes | 3 lines of 22 characters |
| `subtitle` | no | 2 lines of 70 characters |
| `byline` | no | 1 line, presenter and occasion |

## section
Divider before a new part of the talk.

| Field | Required | Holds about |
|---|---|---|
| `kicker` | no | A short label such as "Part 2" |
| `title` | yes | 2 lines of 34 characters |

## bullets
A short list. 2 to 6 bullets.

| Field | Required | Holds about |
|---|---|---|
| `title` | yes | 1 line of 50 characters |
| `bullets` | yes | 2 to 6 items, 1 to 2 lines of 80 characters each |

## two-column
A comparison, before and after, or two options.

| Field | Required | Holds about |
|---|---|---|
| `title` | yes | 1 line of 50 characters |
| `left.heading`, `right.heading` | yes | 1 line of 30 characters |
| `left.text`, `right.text` | yes | About 300 characters each |

## stats
3 or 4 numbers that matter. Only use real numbers from the content.

| Field | Required | Holds about |
|---|---|---|
| `title` | yes | 1 line of 50 characters |
| `stats[].value` | yes | 4 to 6 characters, like "38%" or "2.4x" |
| `stats[].label` | yes | 2 lines of 18 characters |
| `stats[].note` | no | About 100 characters |

## steps
A process or timeline. 3 to 5 steps, numbered automatically.

| Field | Required | Holds about |
|---|---|---|
| `title` | yes | 1 line of 50 characters |
| `steps[].heading` | yes | 2 lines of 18 characters |
| `steps[].text` | yes | About 120 characters |

## quote
One line people should remember. Write only the words; the quote mark is added.

| Field | Required | Holds about |
|---|---|---|
| `quote` | yes | About 140 characters |
| `attribution` | no | Who said it. Never invent one. |

## closing
The takeaway or the ask.

| Field | Required | Holds about |
|---|---|---|
| `title` | yes | 2 lines of 30 characters |
| `text` | no | 3 lines of 70 characters |
