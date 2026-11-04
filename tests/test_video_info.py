"""Seam B: video_info.py as Claude runs it - arguments in, JSON and exit code out."""
import pytest

import _common
import video_info
from fakes import (QUOTA_EXCEEDED, SUPADATA_OUT_OF_CREDITS, FakeDataAPI, FakeSupadata, install_fake_transcripts,
                   install_fake_ytdlp, route)

CH = "UCabcdefghijklmnopqrstuv"
VID = "dQw4w9WgXcQ"
DESCRIPTION = """How bridges stand up.

0:00 Intro
1:30 - Arches
12:05 Suspension bridges
1:02:00 Outro

Thanks to our sponsor."""


@pytest.fixture
def api():
    fake = FakeDataAPI()
    fake.add_channel(CH, "@Demo", "Demo Channel")
    fake.add_video(CH, VID, "Bridges explained", "2026-03-04T10:00:00Z", views=123456, duration="PT1H5M",
                   description=DESCRIPTION, language="en")
    return fake


@pytest.fixture
def supadata():
    return FakeSupadata({"en": "Hello and welcome. Today: bridges.", "da": "Hej og velkommen."})


@pytest.fixture
def cloud(monkeypatch, api, supadata):
    monkeypatch.setenv("YT_API_KEY", "test-key")
    monkeypatch.setenv("SUPADATA_API_KEY", "supa-key")
    monkeypatch.setattr(_common, "fetch_json", route(googleapis=api, supadata=supadata))
    monkeypatch.setattr(video_info, "POLL_SECONDS", 0)


def test_cloud_metadata_and_chapters_from_description(cloud, cli, supadata):
    code, out = cli(video_info, f"https://youtu.be/{VID}", "--no-transcript")
    assert code == 0
    assert out == {
        "source": "cloud", "id": VID, "url": f"https://www.youtube.com/watch?v={VID}",
        "title": "Bridges explained", "channel": "Demo Channel", "channel_id": CH,
        "channel_url": f"https://www.youtube.com/channel/{CH}", "upload_date": "2026-03-04",
        "duration_seconds": 3900, "duration": "1:05:00", "views": 123456, "description": DESCRIPTION,
        "chapters": [
            {"start": "0:00", "start_seconds": 0, "title": "Intro"},
            {"start": "1:30", "start_seconds": 90, "title": "Arches"},
            {"start": "12:05", "start_seconds": 725, "title": "Suspension bridges"},
            {"start": "1:02:00", "start_seconds": 3720, "title": "Outro"},
        ],
    }
    assert supadata.calls == []


def test_description_without_real_chapters_gives_none(cloud, cli, api):
    api.videos[VID]["snippet"]["description"] = "Best part at 3:15, see also 7:40."
    _, out = cli(video_info, VID, "--no-transcript")
    assert out["chapters"] == []


def test_transcript_from_supadata_uses_existing_captions_only(cloud, cli, supadata):
    code, out = cli(video_info, VID)
    assert code == 0
    assert out["transcript"] == "Hello and welcome. Today: bridges."
    assert out["transcript_language"] == "en"
    assert out["transcript_auto_generated"] is None  # Supadata does not say
    assert out["transcript_source"] == "supadata"
    url, params, headers = supadata.calls[0]
    assert url == "https://api.supadata.ai/v1/transcript"
    assert params == {"url": f"https://www.youtube.com/watch?v={VID}", "lang": "en", "text": "true", "mode": "native"}
    assert headers["x-api-key"] == "supa-key"


def test_first_preferred_language_wins_with_one_credit(cloud, cli, supadata):
    _, out = cli(video_info, VID, "--lang", "da,en")
    assert out["transcript"] == "Hej og velkommen."
    assert supadata.langs_requested() == ["da"]


def test_second_preferred_language_is_fetched_when_first_is_missing(cloud, cli, monkeypatch, api):
    german_first = FakeSupadata({"de": "Hallo.", "en": "Hello."}, default="de")
    monkeypatch.setattr(_common, "fetch_json", route(googleapis=api, supadata=german_first))
    _, out = cli(video_info, VID, "--lang", "da,en")
    assert out["transcript"] == "Hello."
    assert german_first.langs_requested() == ["da", "en"]


def test_original_language_when_no_preferred_language_exists(cloud, cli, monkeypatch, api):
    german = FakeSupadata({"de": "Hallo."})
    monkeypatch.setattr(_common, "fetch_json", route(googleapis=api, supadata=german))
    _, out = cli(video_info, VID, "--lang", "da,en")
    assert (out["transcript"], out["transcript_language"]) == ("Hallo.", "de")
    assert german.langs_requested() == ["da"]


def test_no_captions_keeps_metadata_and_does_not_waste_a_fallback(cloud, cli, monkeypatch, api):
    monkeypatch.setattr(_common, "fetch_json", route(googleapis=api, supadata=FakeSupadata({})))
    transcripts = install_fake_transcripts(monkeypatch, [("en", True, "never used")])
    code, out = cli(video_info, VID)
    assert code == 0
    assert out["title"] == "Bridges explained"
    assert out["transcript"] is None
    assert out["transcript_error"]["code"] == "NO_CAPTIONS"
    assert transcripts.created == []


def test_supadata_out_of_credits_falls_back_to_youtube_transcript_api(cloud, cli, monkeypatch, supadata):
    supadata.error = SUPADATA_OUT_OF_CREDITS
    install_fake_transcripts(monkeypatch, [("en", True, "Hello|from|YouTube")])
    _, out = cli(video_info, VID)
    assert out["transcript"] == "Hello from YouTube"
    assert out["transcript_source"] == "youtube-transcript-api"
    assert out["transcript_auto_generated"] is True


def test_ai_transcript_is_opt_in_and_waits_for_the_job(cloud, cli, supadata):
    supadata.job = True
    _, out = cli(video_info, VID, "--ai-transcript")
    assert out["transcript"] == "Hello and welcome. Today: bridges."
    assert supadata.calls[0][1]["mode"] == "auto"
    assert supadata.calls[1][0] == "https://api.supadata.ai/v1/transcript/job-1"


def test_private_video_is_an_error(cloud, cli, api):
    del api.videos[VID]  # the real API returns no items for private or deleted videos
    code, out = cli(video_info, VID)
    assert code == 1
    assert out["error"]["code"] == "PRIVATE_OR_UNAVAILABLE"


def test_quota_exceeded_falls_back_to_yt_dlp_for_metadata(cloud, cli, monkeypatch, api):
    api.error = QUOTA_EXCEEDED
    install_fake_ytdlp(monkeypatch, {f"https://www.youtube.com/watch?v={VID}": LOCAL_INFO})
    _, out = cli(video_info, VID, "--no-transcript")
    assert out["source"] == "local"
    assert out["title"] == "Bridges explained"


# ---------------------------------------------------------------- local backend

LOCAL_INFO = {
    "id": VID, "title": "Bridges explained", "channel": "Demo Channel", "channel_id": CH,
    "channel_url": f"https://www.youtube.com/channel/{CH}", "upload_date": "20260304", "duration": 3900,
    "view_count": 123456, "description": DESCRIPTION, "language": "en",
    "chapters": [{"start_time": 0.0, "end_time": 90.0, "title": "Intro"},
                 {"start_time": 90.0, "end_time": 3900.0, "title": "Arches"}],
}


def test_without_keys_uses_yt_dlp_and_its_chapters(cli, monkeypatch):
    install_fake_ytdlp(monkeypatch, {f"https://www.youtube.com/watch?v={VID}": LOCAL_INFO})
    code, out = cli(video_info, VID, "--no-transcript")
    assert code == 0
    assert out["source"] == "local"
    assert (out["upload_date"], out["duration"], out["views"]) == ("2026-03-04", "1:05:00", 123456)
    assert out["chapters"] == [{"start": "0:00", "start_seconds": 0, "title": "Intro"},
                               {"start": "1:30", "start_seconds": 90, "title": "Arches"}]


def test_private_video_locally(cli, monkeypatch):
    install_fake_ytdlp(monkeypatch, {
        f"https://www.youtube.com/watch?v={VID}":
            f"ERROR: [youtube] {VID}: Private video. Sign in if you've been granted access to this video"})
    code, out = cli(video_info, VID)
    assert code == 1
    assert out["error"]["code"] == "PRIVATE_OR_UNAVAILABLE"


@pytest.fixture
def local_meta(monkeypatch):
    install_fake_ytdlp(monkeypatch, {f"https://www.youtube.com/watch?v={VID}": LOCAL_INFO})


def test_auto_generated_beats_creator_captions_in_the_preferred_language(cli, monkeypatch, local_meta):
    install_fake_transcripts(monkeypatch, [("en", False, "creator text"), ("en-US", True, "auto|text")])
    _, out = cli(video_info, VID)
    assert out["transcript"] == "auto text"
    assert (out["transcript_language"], out["transcript_auto_generated"]) == ("en-US", True)


def test_languages_are_tried_in_order(cli, monkeypatch, local_meta):
    install_fake_transcripts(monkeypatch, [("en", True, "english"), ("da", False, "dansk")])
    _, out = cli(video_info, VID, "--lang", "da,en")
    assert out["transcript"] == "dansk"


def test_falls_back_to_the_original_spoken_language(cli, monkeypatch, local_meta):
    install_fake_transcripts(monkeypatch, [("fr", False, "sous-titres"), ("de", True, "gesprochen")])
    _, out = cli(video_info, VID, "--lang", "da,en")
    assert (out["transcript"], out["transcript_language"]) == ("gesprochen", "de")


@pytest.mark.parametrize("error, code", [
    ("TranscriptsDisabled", "NO_CAPTIONS"),
    ("NoTranscriptFound", "NO_CAPTIONS"),
    ("RequestBlocked", "IP_BLOCKED"),
    ("IpBlocked", "IP_BLOCKED"),
    ("VideoUnavailable", "PRIVATE_OR_UNAVAILABLE"),
    ("AgeRestricted", "PRIVATE_OR_UNAVAILABLE"),
])
def test_transcript_library_errors_have_clear_codes(cli, monkeypatch, local_meta, error, code):
    install_fake_transcripts(monkeypatch, error=error)
    exit_code, out = cli(video_info, VID)
    assert exit_code == 0
    assert out["transcript"] is None
    assert out["transcript_error"]["code"] == code
    assert f"{error} happened" in out["transcript_error"]["message"]
    assert "If you are sure" not in out["transcript_error"]["message"]


def test_proxy_is_used_by_both_local_libraries(cli, monkeypatch):
    monkeypatch.setenv("YT_PROXY", "http://user:pass@proxy.example:8080")
    ytdlp = install_fake_ytdlp(monkeypatch, {f"https://www.youtube.com/watch?v={VID}": LOCAL_INFO})
    transcripts = install_fake_transcripts(monkeypatch, [("en", True, "hi")])
    cli(video_info, VID)
    assert ytdlp.calls[0][1]["proxy"] == "http://user:pass@proxy.example:8080"
    assert transcripts.created[0].proxy_config.https_url == "http://user:pass@proxy.example:8080"


@pytest.mark.parametrize("error, code, falls_back", [
    ("SUPADATA_RATE_LIMITED", "RATE_LIMITED", True),
    ("SUPADATA_OUT_OF_CREDITS", "QUOTA_EXCEEDED", True),
    ("SUPADATA_RESTRICTED", "PRIVATE_OR_UNAVAILABLE", False),
])
def test_supadata_errors_follow_its_docs(cloud, cli, monkeypatch, supadata, error, code, falls_back):
    import fakes
    supadata.error = getattr(fakes, error)
    transcripts = install_fake_transcripts(monkeypatch, error="RequestBlocked")  # as in the cloud
    _, out = cli(video_info, VID)
    assert out["transcript_error"]["code"] == code
    assert bool(transcripts.created) is falls_back
