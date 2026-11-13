from collections import deque
from html.parser import HTMLParser
from urllib.parse import urljoin, urlparse, urldefrag
from urllib.robotparser import RobotFileParser
import subprocess
import time

START_URL = "https://www.ilrc.org/"
DOMAIN = "www.ilrc.org"
USER_AGENT = "DerechoResearchSpider/0.1"
MAX_PAGES = 100
DELAY = 2


class LinkParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.links = set()

    def handle_starttag(self, tag, attrs):
        if tag == "a":
            href = dict(attrs).get("href")
            if href:
                self.links.add(href)


def fetch(url):
    return subprocess.check_output(
        [
            "curl", "-fsSL",
            "--max-time", "20",
            "-A", USER_AGENT,
            url
        ],
        text=True,
        timeout=25
    )


def main():
    print("Derecho Spider starting...")

    robots = RobotFileParser()

    try:
        robots_text = fetch(
            "https://www.ilrc.org/robots.txt"
        )
        robots.parse(robots_text.splitlines())
    except Exception as error:
        print("Cannot verify crawling rules:", error)
        return

    queue = deque([START_URL])
    visited = set()
    pdf_links = set()

    while queue and len(visited) < MAX_PAGES:
        url = queue.popleft()

        if url in visited:
            continue

        if not robots.can_fetch(USER_AGENT, url):
            print("Skipping restricted page:", url)
            continue

        visited.add(url)
        print(f"\nScanning page {len(visited)}: {url}")

        try:
            html = fetch(url)
            parser = LinkParser()
            parser.feed(html)

            def link_priority(href):
                href = href.lower()
                if any(word in href for word in (
                    "spanish", "espanol", "español",
                    "know-your-rights", "conozca"
                )):
                    return 0
                if "resources" in href:
                    return 1
                return 2

            for href in sorted(parser.links, key=lambda h: (link_priority(h), h)):
                link = urldefrag(urljoin(url, href)).url
                parsed = urlparse(link)

                if parsed.scheme != "https":
                    continue

                if parsed.netloc != DOMAIN:
                    continue

                if parsed.path.lower().endswith(".pdf"):
                    if robots.can_fetch(USER_AGENT, link):
                        pdf_links.add(link)

                elif (
                    link not in visited
                    and link not in queue
                    and "?" not in link
                    and any(
                        word in parsed.path.lower()
                        for word in (
                            "resource", "rights", "immigration",
                            "deportation", "ice", "spanish",
                            "asylum", "detention", "citizenship",
                            "families", "community"
                        )
                    )
                ):
                    queue.append(link)

        except Exception as error:
            print("Could not scan:", error)

        time.sleep(DELAY)

    print("\n--- RESULTS ---")
    print("Pages scanned:", len(visited))
    print("PDF links found:", len(pdf_links))

    from pathlib import Path

    review_dir = Path("data/legal_sources/spider_review")
    review_dir.mkdir(parents=True, exist_ok=True)

    report = review_dir / "discovered_pdfs.txt"
    report.write_text(
        "\n".join(sorted(pdf_links)) + "\n",
        encoding="utf-8"
    )

    print("PDF links saved to:", report)

    for link in sorted(pdf_links):
        label = "Possible Spanish PDF" if any(
            word in link.lower()
            for word in (
                "spanish", "espanol", "español",
                "_es", "-es", "esp%", "esp.", "esp_",
                "spa%", "spa.", "spa_"
            )
        ) else "PDF"

        print(f"[{label}] {link}")


if __name__ == "__main__":
    main()
