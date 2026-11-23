import httpx
import pytest

from esg_docs_to_rag.scraper import PoliteClient, robots_allows

ROBOTS = "User-agent: *\nDisallow: /private/\n"


def test_allowed_page():
    assert robots_allows(ROBOTS, "https://ex.com/report.pdf")


def test_blocked_page():
    assert not robots_allows(ROBOTS, "https://ex.com/private/report.pdf")


def test_no_robots_means_allowed():
    assert robots_allows("", "https://ex.com/anything.pdf")


def make_client(handler, **kwargs):
    return PoliteClient(transport=httpx.MockTransport(handler), sleep=lambda s: None, **kwargs)


def test_retries_on_503_then_succeeds():
    calls = []

    def handler(req):
        calls.append(req)
        return httpx.Response(503) if len(calls) == 1 else httpx.Response(200, text="ok")

    assert make_client(handler).get("https://ex.com/a").text == "ok"
    assert len(calls) == 2


def test_no_retry_on_404():
    calls = []

    def handler(req):
        calls.append(req)
        return httpx.Response(404)

    with pytest.raises(httpx.HTTPStatusError):
        make_client(handler).get("https://ex.com/missing")
    assert len(calls) == 1


def test_waits_between_visits_to_same_site():
    waits = []
    c = PoliteClient(
        delay=2.0,
        transport=httpx.MockTransport(lambda req: httpx.Response(200)),
        sleep=waits.append,
    )
    c.get("https://ex.com/a")
    c.get("https://ex.com/b")
    assert len(waits) == 1 and 1.5 < waits[0] <= 2.0