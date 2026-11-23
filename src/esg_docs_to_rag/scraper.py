from urllib.parse import urlparse
from urllib.robotparser import RobotFileParser

import httpx

USER_AGENT = "esg-docs-to-rag/0.1 (+mailto:bhashithahemantha@gmail.com)"


def robots_allows(robots_txt: str, url: str) -> bool:
    rp = RobotFileParser()
    rp.parse(robots_txt.splitlines())
    return rp.can_fetch(USER_AGENT, url)


def fetch_robots(url: str) -> str:
    p = urlparse(url)
    r = httpx.get(f"{p.scheme}://{p.netloc}/robots.txt", headers={"User-Agent": USER_AGENT})
    return r.text if r.status_code == 200 else ""