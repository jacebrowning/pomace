import pomace


def test_visit():
    page = pomace.visit("http://example.com", headless=True)
    assert "Example Domain" in page
