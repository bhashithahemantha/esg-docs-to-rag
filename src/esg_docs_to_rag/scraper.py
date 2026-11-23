import time
from urllib.parse import urlparse
from urllib.robotparser import RobotFileParser

import httpx

USER_AGENT = "esg-docs-to-rag/0.1 (+mailto:you@example.com)"
RETRY_STATUSES = {429, 500, 502, 503, 504}


def robots_allows(robots_txt: str, url: str) -> bool:
    rp = RobotFileParser()
    rp.parse(robots_txt.splitlines())
    return rp.can_fetch(USER_AGENT, url)


def fetch_robots(url: str) -> str:
    p = urlparse(url)
    r = httpx.get(f"{p.scheme}://{p.netloc}/robots.txt", headers={"User-Agent": USER_AGENT})
    return r.text if r.status_code == 200 else ""


class PoliteClient:
    def __init__(self, delay=2.0, max_tries=4, transport=None, sleep=time.sleep):
        self.http = httpx.Client(
            headers={"User-Agent": USER_AGENT},
            timeout=30,
            follow_redirects=True,
            transport=transport,
        )
        self.delay = delay
        self.max_tries = max_tries
        self.sleep = sleep
        self.last_visit: dict[str, float] = {}

    def _wait_turn(self, url: str) -> None:
        host = urlparse(url).netloc
        elapsed = time.monotonic() - self.last_visit.get(host, float("-inf"))
        if elapsed < self.delay:
            self.sleep(self.delay - elapsed)
        self.last_visit[host] = time.monotonic()

    def get(self, url: str) -> httpx.Response:
        for attempt in range(1, self.max_tries + 1):
            self._wait_turn(url)
            try:
                r = self.http.get(url)
            except httpx.TransportError:
                if attempt == self.max_tries:
                    raise
            else:
                if r.status_code not in RETRY_STATUSES or attempt == self.max_tries:
                    r.raise_for_status()
                    return r
            self.sleep(2**attempt)