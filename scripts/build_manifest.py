"""Builds the _site folder that GitHub Pages publishes.

It scans every .html file in papers/, reads the paper details from the file,
writes _site/papers.json, and copies index.html and papers/ into _site.
Run automatically by .github/workflows/deploy.yml. No manual step needed.
"""
import json
import re
import shutil
from pathlib import Path

root = Path(__file__).resolve().parent.parent
site = root / "_site"
if site.exists():
    shutil.rmtree(site)
site.mkdir()

papers = []
for f in sorted((root / "papers").glob("*.html")):
    t = f.read_text(encoding="utf-8")

    def g(pat, cast=str, default=None):
        m = re.search(pat, t)
        return cast(m.group(1)) if m else default

    questions = len(re.findall(r"\{n:\d+,", t))
    plus = g(r"\bplus:\s*(\d+)", int, 4)
    title = g(r"\btitle:'([^']*)'") or g(r"<title>(.*?)</title>") or f.stem
    ch = re.search(r"Chapter\s+(\d+)", title)
    papers.append({
        "file": "papers/" + f.name,
        "id": g(r"\bid:'([^']*)'") or f.stem,
        "title": title,
        "series": g(r"\bseries:'([^']*)'", str, ""),
        "subject": g(r"\bsubject:'([^']*)'", str, ""),
        "minutes": g(r"\bdurationMin:\s*(\d+)", int, 60),
        "questions": questions,
        "marks": questions * plus,
        "_order": int(ch.group(1)) if ch else 9999,
    })

papers.sort(key=lambda p: (p["_order"], p["title"]))
for p in papers:
    del p["_order"]

(site / "papers.json").write_text(json.dumps(papers, indent=2), encoding="utf-8")
shutil.copy(root / "index.html", site / "index.html")
shutil.copytree(root / "papers", site / "papers")
(site / ".nojekyll").write_text("")
print("Listed %d paper(s):" % len(papers))
for p in papers:
    print(" -", p["file"], "|", p["title"])
