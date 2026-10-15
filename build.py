"""src/deck.html -> 10퍼센트_발표.html : one offline file (fonts subset + images inlined).
Run again after editing src/deck.html:  python build.py
"""
import base64, re, subprocess, urllib.parse
from pathlib import Path

HERE = Path(__file__).parent
SRC = HERE / "src" / "deck.html"
OUT = HERE / "10퍼센트_발표.html"
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0 Safari/537.36"
MIME = {".png": "image/png", ".jpg": "image/jpeg", ".jpeg": "image/jpeg", ".webp": "image/webp"}


def get(url):
    # curl uses the Windows certificate store; some Python builds ship without one
    return subprocess.run(["curl", "-sfL", "-A", UA, url], capture_output=True, check=True).stdout


def data_uri(mime, raw):
    return f"data:{mime};base64,{base64.b64encode(raw).decode()}"


html = SRC.read_text(encoding="utf-8")

# fonts: ask Google Fonts for only the glyphs this deck uses, embed them
link = re.search(r'<link rel="stylesheet" data-inline-fonts href="([^"]+)">', html)
chars = "".join(sorted({c for c in html if c >= " "}))
css = get(link[1].replace("&amp;", "&") + "&text=" + urllib.parse.quote(chars)).decode()
css = re.sub(r"url\((https://[^)]+)\)", lambda m: f"url({data_uri('font/woff2', get(m[1]))})", css)
html = html.replace(link[0], f"<style>{css}</style>")

# images
html = re.sub(r"assets/[\w.-]+", lambda m: data_uri(MIME[Path(m[0]).suffix], (SRC.parent / m[0]).read_bytes()), html)

OUT.write_text(html, encoding="utf-8")
print(f"{OUT.name}: {OUT.stat().st_size / 1e6:.1f} MB")
