"""Render a .pptx to one PNG per slide so every slide can be looked at.

usage: python render.py deck.pptx renders/

Needs LibreOffice (soffice) and poppler (pdftoppm) on the PATH.
"""
import os, shutil, subprocess, sys, tempfile


def main():
    if len(sys.argv) != 3:
        sys.exit(__doc__)
    deck, out = os.path.abspath(sys.argv[1]), os.path.abspath(sys.argv[2])
    for tool in ("soffice", "pdftoppm"):
        if not shutil.which(tool):
            sys.exit(f"{tool} not found. Install LibreOffice and poppler, or check the slides by opening the .pptx.")
    os.makedirs(out, exist_ok=True)
    with tempfile.TemporaryDirectory() as tmp:
        subprocess.run(["soffice", "--headless", "--convert-to", "pdf", "--outdir", tmp, deck],
                       check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        pdf = os.path.join(tmp, os.path.splitext(os.path.basename(deck))[0] + ".pdf")
        subprocess.run(["pdftoppm", "-png", "-r", "80", pdf, os.path.join(out, "slide")], check=True)
    files = sorted(f for f in os.listdir(out) if f.startswith("slide"))
    print(f"Rendered {len(files)} slides to {out}")


if __name__ == "__main__":
    main()
