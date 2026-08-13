import threading

import pytest
import requests
from click.testing import CliRunner

from ovos_docs_viewer import ovos_docs
from conftest import make_zip_bytes, make_root_tree_zip_bytes

import ovos_docs_viewer
assert "/home/miro/tmp/dv-wt" in ovos_docs_viewer.__file__


@pytest.fixture(autouse=True)
def isolated_xdg(tmp_path, monkeypatch):
    monkeypatch.setattr(ovos_docs, "xdg_data_home", lambda: str(tmp_path))
    return tmp_path


def test_interrupted_download_recovery(http_server, tmp_path, monkeypatch):
    """A folder left behind by a killed download (mkdir happened, write
    didn't) must not be treated as cached forever."""
    http_server.routes["/mydoc.md"] = b"real content"
    monkeypatch.setattr(ovos_docs, "DOCS_URLS", {"mydoc": f"{http_server.base_url}/mydoc.md"})
    monkeypatch.setattr(ovos_docs, "SKILLS", [])

    # simulate: mkdir happened, content write never did (process killed)
    stale = tmp_path / "ovos_docs" / "mydoc"
    stale.mkdir(parents=True)

    paths = ovos_docs.download_docs()

    docs_file = list((tmp_path / "ovos_docs" / "mydoc" / "docs").iterdir())
    assert len(docs_file) == 1
    assert docs_file[0].read_text() == "real content"


def test_concurrent_download_safety_zip(http_server, tmp_path, monkeypatch):
    """Two threads racing to download the same zip doc set must not crash
    and must not leave a nested duplicate tree."""
    zip_bytes = make_zip_bytes("myrepo-master")
    http_server.routes["/myrepo/archive/refs/heads/master.zip"] = zip_bytes
    url = f"{http_server.base_url}/myrepo/archive/refs/heads/master.zip"
    monkeypatch.setattr(ovos_docs, "DOCS_URLS", {"zipdoc": url})
    monkeypatch.setattr(ovos_docs, "SKILLS", [])

    errors = []

    def run():
        try:
            ovos_docs.download_docs()
        except Exception as e:
            errors.append(e)

    threads = [threading.Thread(target=run) for _ in range(4)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    assert not errors, errors

    doc_folder = tmp_path / "ovos_docs" / "zipdoc"
    docs_dir = doc_folder / "docs"
    assert docs_dir.is_dir()
    assert (docs_dir / "readme.md").read_text() == "# hello\n"
    # no nested duplicate ("zipdoc/myrepo-master/docs/...")
    assert not (doc_folder / "myrepo-master").exists()
    # no leftover temp dirs
    leftovers = [p for p in (tmp_path / "ovos_docs").iterdir() if p.name.startswith(".zipdoc-")]
    assert leftovers == []


def test_invalid_docs_arg_clean_error():
    runner = CliRunner()
    result = runner.invoke(ovos_docs.launch, ["bogus"])
    assert result.exit_code != 0
    assert "Traceback" not in result.output
    assert "AssertionError" not in result.output


def test_network_failure_clean_error(tmp_path, monkeypatch):
    monkeypatch.setattr(ovos_docs, "DOCS_URLS", {"mydoc": "http://127.0.0.1:1/mydoc.md"})
    monkeypatch.setattr(ovos_docs, "SKILLS", [])

    def raise_conn_error(*a, **kw):
        raise requests.ConnectionError("boom")

    monkeypatch.setattr(ovos_docs.requests, "get", raise_conn_error)

    with pytest.raises(ovos_docs.click.ClickException) as exc_info:
        ovos_docs.download_docs()

    message = str(exc_info.value)
    assert "Traceback" not in message
    assert message.count("\n") == 0
    assert "mydoc.md" in message


def test_refresh_redownloads(http_server, tmp_path, monkeypatch):
    # http_server fixture serves fixed bytes per path; emulate a changing
    # response by swapping the route body before each download call
    http_server.routes["/mydoc.md"] = b"content-1"
    monkeypatch.setattr(ovos_docs, "DOCS_URLS", {"mydoc": f"{http_server.base_url}/mydoc.md"})
    monkeypatch.setattr(ovos_docs, "SKILLS", [])

    ovos_docs.download_docs()
    doc_file = tmp_path / "ovos_docs" / "mydoc" / "docs" / "mydoc.md"
    assert doc_file.read_text() == "content-1"

    # cached: unchanged even though the "server" content differs now
    http_server.routes["/mydoc.md"] = b"content-2"
    ovos_docs.download_docs()
    assert doc_file.read_text() == "content-1"

    # --refresh forces re-download
    ovos_docs.download_docs(force=True)
    assert doc_file.read_text() == "content-2"


def test_live_status_always_refreshes(http_server, tmp_path, monkeypatch):
    """live-status is documented to always re-fetch, even with force=False
    and an already-complete cache on disk."""
    http_server.routes["/live.md"] = b"STALE-MARKER-CONTENT"
    monkeypatch.setattr(ovos_docs, "DOCS_URLS", {"live-status": f"{http_server.base_url}/live.md"})
    monkeypatch.setattr(ovos_docs, "SKILLS", [])

    ovos_docs.download_docs()
    doc_file = tmp_path / "ovos_docs" / "live-status" / "docs" / "live-status.md"
    assert doc_file.read_text() == "STALE-MARKER-CONTENT"

    http_server.routes["/live.md"] = b"FRESH-CONTENT"
    ovos_docs.download_docs(force=False)
    assert doc_file.read_text() == "FRESH-CONTENT"


def test_root_tree_docs_set_downloads(http_server, tmp_path, monkeypatch):
    """A doc set whose markdown lives at the extracted repo root (like
    OpenVoiceOS/architecture) must resolve its tree path via DOCS_SUBDIR,
    not the hardcoded 'docs' subfolder."""
    zip_bytes = make_root_tree_zip_bytes("architecture-dev")
    http_server.routes["/architecture/archive/refs/heads/dev.zip"] = zip_bytes
    url = f"{http_server.base_url}/architecture/archive/refs/heads/dev.zip"
    monkeypatch.setattr(ovos_docs, "DOCS_URLS", {"architecture": url})
    monkeypatch.setattr(ovos_docs, "DOCS_SUBDIR", {"architecture": ""})
    monkeypatch.setattr(ovos_docs, "SKILLS", [])

    paths = ovos_docs.download_docs()

    doc_folder = tmp_path / "ovos_docs" / "architecture"
    assert paths["architecture"] == str(doc_folder)
    assert (doc_folder / "README.md").read_text() == "# root readme\n"
    assert (doc_folder / "pipeline-1.md").read_text() == "# pipeline spec\n"
    assert (doc_folder / "appendix" / "foo.md").read_text() == "# appendix foo\n"
    assert (doc_folder / "LICENSE").exists()


def test_root_tree_docs_set_cached_skip(http_server, tmp_path, monkeypatch):
    """Once downloaded, a root-tree doc set must be recognized as cached
    and skip re-download."""
    zip_bytes = make_root_tree_zip_bytes("architecture-dev")
    http_server.routes["/architecture/archive/refs/heads/dev.zip"] = zip_bytes
    url = f"{http_server.base_url}/architecture/archive/refs/heads/dev.zip"
    monkeypatch.setattr(ovos_docs, "DOCS_URLS", {"architecture": url})
    monkeypatch.setattr(ovos_docs, "DOCS_SUBDIR", {"architecture": ""})
    monkeypatch.setattr(ovos_docs, "SKILLS", [])

    hits = {"n": 0}
    real_get = ovos_docs.requests.get

    def counting_get(*a, **kw):
        hits["n"] += 1
        return real_get(*a, **kw)

    monkeypatch.setattr(ovos_docs.requests, "get", counting_get)

    ovos_docs.download_docs()
    assert hits["n"] == 1

    paths = ovos_docs.download_docs(force=False)
    assert hits["n"] == 1  # cache hit, no re-download
    assert paths["architecture"] == str(tmp_path / "ovos_docs" / "architecture")


def test_non_live_status_skips_when_cached(http_server, tmp_path, monkeypatch):
    """Non-live-status doc sets must NOT re-download once cached."""
    http_server.routes["/tech.md"] = b"tech content"
    monkeypatch.setattr(ovos_docs, "DOCS_URLS", {"technical": f"{http_server.base_url}/tech.md"})
    monkeypatch.setattr(ovos_docs, "SKILLS", [])

    hits = {"n": 0}
    real_get = ovos_docs.requests.get

    def counting_get(*a, **kw):
        hits["n"] += 1
        return real_get(*a, **kw)

    monkeypatch.setattr(ovos_docs.requests, "get", counting_get)

    ovos_docs.download_docs()
    assert hits["n"] == 1

    ovos_docs.download_docs(force=False)
    assert hits["n"] == 1  # no re-download, cache hit
