"""Seam B: every error code reaches Claude as JSON with a next step, and wrong keys fall back."""
import pytest

import _common
import channel_videos
import video_info
from fakes import KEY_INVALID, FakeDataAPI, FakeSupadata, install_fake_transcripts, install_fake_ytdlp, route

VID = "dQw4w9WgXcQ"
CH = "UCabcdefghijklmnopqrstuv"
INFO = {"id": VID, "title": "T", "channel": "C", "channel_id": CH, "upload_date": "20260101",
        "duration": 60, "view_count": 1, "description": ""}


def test_every_code_has_a_hint():
    codes = ["BAD_INPUT", "NOT_FOUND", "PRIVATE_OR_UNAVAILABLE", "NO_CAPTIONS", "RATE_LIMITED", "IP_BLOCKED",
             "QUOTA_EXCEEDED", "BAD_API_KEY", "MISSING_DEPENDENCY", "NETWORK_ERROR", "UNEXPECTED"]
    assert all(_common.HINTS.get(code) for code in codes)


def test_wrong_youtube_key_falls_back_to_yt_dlp(cli, monkeypatch):
    monkeypatch.setenv("YT_API_KEY", "wrong")
    api = FakeDataAPI()
    monkeypatch.setattr(_common, "fetch_json", api)
    install_fake_ytdlp(monkeypatch, {f"https://www.youtube.com/watch?v={VID}": INFO})
    code, out = cli(video_info, VID, "--no-transcript")
    assert (code, out["source"]) == (0, "local")
    assert api.calls  # the cloud backend really was tried first


def test_wrong_youtube_key_alone_is_reported_with_a_fix(cli, monkeypatch):
    monkeypatch.setenv("YT_API_KEY", "wrong")
    monkeypatch.setattr(_common, "fetch_json", lambda *a, **k: KEY_INVALID)
    code, out = cli(video_info, VID)
    assert (code, out["error"]["code"]) == (1, "BAD_API_KEY")
    assert "YT_API_KEY" in out["error"]["hint"]


def test_wrong_supadata_key_falls_back_to_youtube_transcript_api(cli, monkeypatch):
    monkeypatch.setenv("SUPADATA_API_KEY", "wrong")
    monkeypatch.setattr(_common, "fetch_json", route(supadata=FakeSupadata({"en": "never"})))
    install_fake_ytdlp(monkeypatch, {f"https://www.youtube.com/watch?v={VID}": INFO})
    install_fake_transcripts(monkeypatch, [("en", True, "local words")])
    _, out = cli(video_info, VID)
    assert (out["transcript"], out["transcript_source"]) == ("local words", "youtube-transcript-api")


def test_supadata_failing_in_the_cloud_explains_both_attempts(cli, monkeypatch):
    monkeypatch.setenv("SUPADATA_API_KEY", "wrong")
    monkeypatch.setattr(_common, "fetch_json", route(supadata=FakeSupadata({"en": "never"})))
    install_fake_ytdlp(monkeypatch, {f"https://www.youtube.com/watch?v={VID}": INFO})
    install_fake_transcripts(monkeypatch, error="RequestBlocked")
    code, out = cli(video_info, VID)
    assert code == 0
    error = out["transcript_error"]
    assert error["code"] == "BAD_API_KEY"
    assert "SUPADATA_API_KEY" in error["hint"]
    assert "IP_BLOCKED" in error["message"]


@pytest.mark.parametrize("message, code", [
    ("ERROR: [youtube:tab] @demo: HTTP Error 429: Too Many Requests", "RATE_LIMITED"),
    ("ERROR: [youtube:tab] @demo: This channel does not exist.", "NOT_FOUND"),
    ("ERROR: [youtube:tab] @demo: Unable to download API page: <urlopen error [Errno -2] Name or service not known>",
     "NETWORK_ERROR"),
    ("ERROR: [youtube:tab] @demo: Something new YouTube changed", "UNEXPECTED"),
])
def test_yt_dlp_failures_have_clear_codes(cli, monkeypatch, message, code):
    install_fake_ytdlp(monkeypatch, {"https://www.youtube.com/@demo/videos": message})
    exit_code, out = cli(channel_videos, "@demo")
    assert (exit_code, out["error"]["code"]) == (1, code)
    assert out["error"]["hint"]
    assert not out["error"]["message"].startswith("ERROR")


def test_age_restricted_is_not_mistaken_for_a_bot_check(cli, monkeypatch):
    install_fake_ytdlp(monkeypatch, {f"https://www.youtube.com/watch?v={VID}":
                                     f"ERROR: [youtube] {VID}: Sign in to confirm your age. This video may be inappropriate"})
    _, out = cli(video_info, VID)
    assert out["error"]["code"] == "PRIVATE_OR_UNAVAILABLE"
