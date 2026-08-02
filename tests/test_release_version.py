"""The release script's PyPI probe.

`verify` gates the release: it runs between the upload and the tag, so a false
negative fails a release that actually succeeded, and a false positive tags one
that never uploaded. Both directions matter, and neither is exercised by
anything else. No network here; urlopen is stubbed.
"""

import pathlib
import sys
import urllib.error

import pytest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent / "scripts"))

import release_version  # noqa: E402


class FakeResponse:
    def __init__(self, status):
        self.status = status

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        return False


def stub_urlopen(monkeypatch, behaviour):
    """Point release_version's urlopen at `behaviour(url)`."""
    monkeypatch.setattr(
        release_version.urllib.request, "urlopen", lambda url, timeout=None: behaviour(url)
    )


def test_present_version_is_found(monkeypatch):
    stub_urlopen(monkeypatch, lambda url: FakeResponse(200))
    assert release_version.is_on_pypi("2.3.0") is True


def test_missing_version_is_a_404_not_an_error(monkeypatch):
    def raise_404(url):
        raise urllib.error.HTTPError(url, 404, "Not Found", {}, None)

    stub_urlopen(monkeypatch, raise_404)
    assert release_version.is_on_pypi("99.99.99") is False


def test_it_asks_for_the_exact_version_not_the_cached_project_endpoint(monkeypatch):
    """The aggregate /pypi/<pkg>/json document is CDN-cached and lags behind.

    After 2.3.0 was published it kept reporting 2.2.0, so polling it can fail a
    release that already succeeded. The probe must use the per-version URL.
    """
    seen = []
    stub_urlopen(monkeypatch, lambda url: seen.append(url) or FakeResponse(200))
    release_version.is_on_pypi("2.3.0")
    assert seen == ["https://pypi.org/pypi/asciiquarium/2.3.0/json"]


def test_network_failure_reads_as_absent_rather_than_crashing(monkeypatch):
    def unreachable(url):
        raise urllib.error.URLError("no route to host")

    stub_urlopen(monkeypatch, unreachable)
    assert release_version.is_on_pypi("2.3.0") is False


def test_a_server_error_is_not_swallowed(monkeypatch):
    """A 500 means PyPI is unwell, not that the version is missing.

    Reporting "absent" for it would let verify burn all its attempts and then
    claim the upload failed, pointing at the wrong problem.
    """

    def raise_500(url):
        raise urllib.error.HTTPError(url, 500, "Server Error", {}, None)

    stub_urlopen(monkeypatch, raise_500)
    with pytest.raises(urllib.error.HTTPError):
        release_version.is_on_pypi("2.3.0")


def test_verify_gives_up_and_fails_loudly(monkeypatch):
    stub_urlopen(
        monkeypatch,
        lambda url: (_ for _ in ()).throw(urllib.error.HTTPError(url, 404, "Not Found", {}, None)),
    )
    monkeypatch.setattr(release_version.time, "sleep", lambda _: None)
    with pytest.raises(SystemExit, match="never served"):
        release_version.verify("99.99.99", attempts=3, delay=0)


def test_verify_retries_through_a_server_error_instead_of_dying(monkeypatch):
    """A transient 5xx must not abort a release that is otherwise fine."""
    calls = []

    def flaky(url):
        calls.append(url)
        if len(calls) == 1:
            raise urllib.error.HTTPError(url, 503, "Service Unavailable", {}, None)
        return FakeResponse(200)

    stub_urlopen(monkeypatch, flaky)
    monkeypatch.setattr(release_version.time, "sleep", lambda _: None)
    release_version.verify("2.3.1", attempts=5, delay=0)
    assert len(calls) == 2


def test_verify_still_fails_if_the_server_error_never_clears(monkeypatch):
    stub_urlopen(
        monkeypatch,
        lambda url: (_ for _ in ()).throw(
            urllib.error.HTTPError(url, 500, "Server Error", {}, None)
        ),
    )
    monkeypatch.setattr(release_version.time, "sleep", lambda _: None)
    with pytest.raises(SystemExit, match="never served"):
        release_version.verify("2.3.1", attempts=2, delay=0)


def test_verify_stops_as_soon_as_it_appears(monkeypatch):
    """Third attempt succeeds, so it must not keep polling afterwards."""
    calls = []

    def eventually(url):
        calls.append(url)
        if len(calls) < 3:
            raise urllib.error.HTTPError(url, 404, "Not Found", {}, None)
        return FakeResponse(200)

    stub_urlopen(monkeypatch, eventually)
    monkeypatch.setattr(release_version.time, "sleep", lambda _: None)
    release_version.verify("2.3.1", attempts=10, delay=0)
    assert len(calls) == 3
