import json
import sys
from pathlib import Path

import pytest

# The scripts are standalone files, not a package: put their folder on the path.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "yt-research" / "scripts"))

import _common  # noqa: E402


@pytest.fixture(autouse=True)
def offline(monkeypatch):
    """No test touches the network, real keys or real libraries unless it installs a fake."""
    for name in ("YT_API_KEY", "SUPADATA_API_KEY", "YT_PROXY"):
        monkeypatch.delenv(name, raising=False)

    def no_network(url, *args, **kwargs):
        raise AssertionError(f"unexpected network call to {url}")

    monkeypatch.setattr(_common, "fetch_json", no_network)
    for module in ("yt_dlp", "yt_dlp.utils", "youtube_transcript_api", "youtube_transcript_api.proxies"):
        monkeypatch.setitem(sys.modules, module, None)  # None makes `import` fail like a missing package


@pytest.fixture
def cli(capsys):
    """Run a script the way Claude does and return (exit code, parsed JSON from stdout)."""

    def invoke(script, *args):
        try:
            _common.run(script.main, list(args))
            code = 0
        except SystemExit as stop:
            code = stop.code
        return code, json.loads(capsys.readouterr().out)

    return invoke
