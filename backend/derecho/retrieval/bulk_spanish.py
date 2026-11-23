import hashlib
import json
import re
import subprocess
from pathlib import Path
from urllib.parse import unquote, urlparse

BASE = Path("data/legal_sources")
REVIEW = BASE / "spider_review"
DOWNLOADS = REVIEW / "bulk_spanish"
URL_FILE = REVIEW / "spanish_bulk_urls.txt"
SOURCES = BASE / "sources.json"

REVIEW.mkdir(parents=True, exist_ok=True)
DOWNLOADS.mkdir(parents=True, exist_ok=True)

if not URL_FILE.exists():
    URL_FILE.write_text(
        "# Add one Spanish PDF URL per line\n",
        encoding="utf-8"
    )
    print("Created:", URL_FILE)
    print("Add Spanish PDF links to this file, then run again.")
    raise SystemExit

sources = json.loads(SOURCES.read_text(encoding="utf-8"))
known_urls = {s["source_url"] for s in sources if s.get("source_url")}

known_hashes = set()
for source in sources:
    path = BASE / source["local_file"]
    if path.is_file():
        known_hashes.add(
            hashlib.sha256(path.read_bytes()).hexdigest()
        )

urls = [
    line.strip()
    for line in URL_FILE.read_text(encoding="utf-8").splitlines()
    if line.strip() and not line.lstrip().startswith("#")
]

urls = list(dict.fromkeys(urls))

print(f"Spanish PDF candidates: {len(urls)}")

results = []

for index, url in enumerate(urls, 1):
    parsed = urlparse(url)

    if parsed.scheme != "https" or not parsed.path.lower().endswith(".pdf"):
        print("SKIP invalid PDF URL:", url)
        continue

    if url in known_urls:
        print("SKIP registered URL:", url)
        continue

    name = unquote(Path(parsed.path).name)
    safe_name = re.sub(r"[^a-zA-Z0-9._-]", "_", name)
    destination = DOWNLOADS / f"{index:03d}_{safe_name}"

    print(f"\nDownloading {index}/{len(urls)}: {name}")

    try:
        subprocess.run(
            [
                "curl", "-fLsS", "--max-time", "45",
                "--max-filesize", "40000000",
                "--output", str(destination), url
            ],
            check=True
        )
    except subprocess.CalledProcessError:
        print("FAILED:", url)
        destination.unlink(missing_ok=True)
        continue

    if destination.read_bytes()[:5] != b"%PDF-":
        print("SKIP not a PDF")
        destination.unlink()
        continue

    digest = hashlib.sha256(destination.read_bytes()).hexdigest()

    if digest in known_hashes:
        print("SKIP duplicate PDF")
        destination.unlink()
        continue

    known_hashes.add(digest)

    results.append({
        "url": url,
        "file": str(destination),
        "status": "needs Spanish-language and content review"
    })

    print("Saved for review:", destination.name)

report = REVIEW / "bulk_spanish_results.json"
report.write_text(
    json.dumps(results, indent=2, ensure_ascii=False),
    encoding="utf-8"
)

print("\n================================")
print("BULK DOWNLOAD COMPLETE")
print("================================")
print("Unique PDFs downloaded:", len(results))
print("Review report:", report)
print("No PDFs were imported into Derecho yet.")
