"""Flag common problems in interface copy.

usage: python check_copy.py strings.txt [more files...]

Reads plain text (one string per line), JSON string files (like en.json),
or HTML/JSX/TSX (visible text between tags and common text props).
Prints one line per finding: file:line, the rule, the text, and a suggestion.
Exits 1 if anything was flagged, so it can run in CI.
"""
import json, re, sys

SMALL = {"a", "an", "and", "as", "at", "but", "by", "for", "in", "of", "on", "or", "the", "to", "with", "vs"}

RULES = [
    ("em-dash", re.compile("\u2014"), "Use a period, comma, colon or parentheses instead."),
    ("vague-error", re.compile(r"\b(something went wrong|an error occurred|unknown error|oops)\b", re.I),
     "Say what happened and what to do next."),
    ("apology", re.compile(r"\b(sorry|we apologi[sz]e)\b", re.I), "Errors explain and direct. They don't apologize."),
    ("generic-action", re.compile(r"^\s*(submit|ok|okay|yes|no|click here|learn more|continue)\s*$", re.I),
     "Name what happens: 'Save changes', 'Send invite', 'Delete project'."),
    ("click-here", re.compile(r"\bclick here\b", re.I), "Make the link text describe where it goes."),
    ("exclamation", re.compile(r"!"), "Save exclamation marks for real celebration, and never in errors."),
    ("please", re.compile(r"\bplease\b", re.I), "Usually filler. Cut it unless you're asking for something unusual."),
    ("three-dots", re.compile(r"(?<!\.)\.\.\.(?!\.)"), "Use the ellipsis character, or cut it."),
    ("we-voice", re.compile(r"^\s*we('re| are| have|'ve)\b", re.I), "Lead with what the person can do, not what the system did."),
    ("double-space", re.compile(r"\S  +\S"), "One space between words and sentences."),
]


def is_title_case(s):
    words = re.findall(r"[A-Za-z][A-Za-z']*", s)
    if len(words) < 2 or len(s) > 60:
        return False
    big = [w for w in words if w.lower() not in SMALL]
    return len(big) >= 2 and all(w[0].isupper() for w in big) and not all(w.isupper() for w in big)


def strings_from(path):
    text = open(path, encoding="utf-8").read()
    if path.endswith(".json"):
        out = []

        def walk(v):
            if isinstance(v, str):
                line = text[: text.find(json.dumps(v)[1:-1])].count("\n") + 1 if v else 0
                out.append((line, v))
            elif isinstance(v, dict):
                for x in v.values():
                    walk(x)
            elif isinstance(v, list):
                for x in v:
                    walk(x)
        walk(json.loads(text))
        return out
    if re.search(r"\.(html?|jsx|tsx|vue|svelte)$", path):
        out = []
        for m in re.finditer(r">([^<>{}]*[A-Za-z][^<>{}]*)<|(?:label|title|placeholder|aria-label|alt)=\"([^\"]+)\"", text):
            s = (m.group(1) or m.group(2)).strip()
            if s:
                out.append((text[: m.start()].count("\n") + 1, s))
        return out
    return [(i + 1, line.rstrip("\n")) for i, line in enumerate(text.splitlines()) if line.strip()]


def main():
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    findings = 0
    for path in sys.argv[1:]:
        for line, s in strings_from(path):
            for name, rx, tip in RULES:
                if rx.search(s):
                    findings += 1
                    print(f"{path}:{line}  {name}  \"{s}\"\n    {tip}")
            if is_title_case(s):
                findings += 1
                print(f"{path}:{line}  title-case  \"{s}\"\n    Use sentence case: only the first word and proper nouns are capitalized.")
    print(f"\n{findings} finding(s)")
    sys.exit(1 if findings else 0)


if __name__ == "__main__":
    main()
