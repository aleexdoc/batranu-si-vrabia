"""Build the site from src/page.html.

Writes two files next to this script:
  index.html     full HTML document, for opening locally / hosting anywhere
  artifact.html  body-only form, for publishing as a claude.ai Artifact
                 (the Artifact host wraps it in its own doctype/head/body)

The logo marks are embedded as data URIs because CSS masks refuse
relative file URLs when the page is opened from disk (file:// is a null origin).
"""
import base64
import io
import sys
from pathlib import Path

from PIL import Image

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

ROOT = Path(__file__).resolve().parent
SRC = ROOT / "src" / "page.html"
MARKER = "<!-- /head -->"

MARKS = {
    "{{LOGO}}": ("img/logo.png", 900),
    "{{CAP}}": ("img/logo-cap.png", 160),
    "{{BIRD}}": ("img/vrabie.png", 240),
}


def data_uri(rel, width):
    im = Image.open(ROOT / rel)
    if im.width > width:
        im = im.resize((width, round(im.height * width / im.width)), Image.LANCZOS)
    buf = io.BytesIO()
    im.save(buf, format="PNG", optimize=True)
    return "data:image/png;base64," + base64.b64encode(buf.getvalue()).decode("ascii")


def main():
    src = SRC.read_text(encoding="utf-8")
    if src.count(MARKER) != 1:
        sys.exit(f"expected exactly one {MARKER!r} in {SRC}")
    for token, (rel, width) in MARKS.items():
        if token not in src:
            sys.exit(f"token {token} not used in {SRC}")
        src = src.replace(token, data_uri(rel, width))
    if "{{" in src:
        sys.exit("unreplaced {{...}} token left in output")

    head, body = src.split(MARKER)
    full = (
        "<!doctype html>\n<html lang=\"ro\">\n<head>\n"
        "<meta charset=\"utf-8\">\n"
        "<meta name=\"viewport\" content=\"width=device-width, initial-scale=1, viewport-fit=cover\">\n"
        + head.strip() + "\n</head>\n<body>\n" + body.strip() + "\n</body>\n</html>\n"
    )
    (ROOT / "index.html").write_text(full, encoding="utf-8", newline="\n")
    (ROOT / "artifact.html").write_text(head.strip() + "\n" + body.strip() + "\n", encoding="utf-8", newline="\n")
    print(f"index.html {len(full) // 1024} KB, artifact.html written")


if __name__ == "__main__":
    main()
