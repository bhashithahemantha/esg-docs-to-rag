from esg_docs_to_rag.scraper import robots_allows

ROBOTS = "User-agent: *\nDisallow: /private/\n"


def test_allowed_page():
    assert robots_allows(ROBOTS, "https://ex.com/report.pdf")


def test_blocked_page():
    assert not robots_allows(ROBOTS, "https://ex.com/private/report.pdf")


def test_no_robots_means_allowed():
    assert robots_allows("", "https://ex.com/anything.pdf")