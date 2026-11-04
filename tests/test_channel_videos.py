"""Seam B: channel_videos.py as Claude runs it - arguments in, JSON and exit code out."""
import pytest

import _common
import channel_videos
from fakes import QUOTA_EXCEEDED, FakeDataAPI, install_fake_ytdlp

CH = "UCabcdefghijklmnopqrstuv"


@pytest.fixture
def api(monkeypatch):
    """A demo channel with 60 regular videos (two pages), 2 shorts and 1 past stream."""
    fake = FakeDataAPI()
    fake.add_channel(CH, "@Demo", "Demo Channel")
    for n in range(60):
        day = 1 + n % 28
        month = 1 + n // 28  # 2026-01-01 .. 2026-03-04, video 59 is newest
        fake.add_video(CH, f"vid{n:08d}", f"Video {n}", f"2026-{month:02d}-{day:02d}T10:00:00Z",
                       views=1000 + n, duration="PT10M5S")
    fake.videos["vid00000007"]["statistics"]["viewCount"] = "999999"   # oldest-ish but most popular
    fake.videos["vid00000003"]["statistics"]["viewCount"] = "500000"
    fake.add_video(CH, "short000001", "A short", "2026-03-05T10:00:00Z", views=9_000_000, duration="PT45S",
                   kind="short")
    fake.add_video(CH, "short000002", "Another short", "2026-03-06T10:00:00Z", views=10, duration="PT30S",
                   kind="short")
    fake.add_video(CH, "live0000001", "A stream", "2026-02-15T18:00:00Z", views=2_000_000,
                   duration="PT1H2M3S", kind="live")
    monkeypatch.setenv("YT_API_KEY", "test-key")
    monkeypatch.setattr(_common, "fetch_json", fake)
    return fake


def test_latest_returns_newest_regular_videos_with_exact_dates(api, cli):
    code, out = cli(channel_videos, "@demo", "--latest", "3")
    assert code == 0
    assert out["source"] == "cloud"
    assert out["channel"] == {"id": CH, "title": "Demo Channel", "handle": "@demo",
                              "url": f"https://www.youtube.com/channel/{CH}"}
    assert [v["id"] for v in out["latest"]] == ["vid00000059", "vid00000058", "vid00000057"]
    assert out["latest"][0] == {
        "id": "vid00000059", "title": "Video 59", "url": "https://www.youtube.com/watch?v=vid00000059",
        "upload_date": "2026-03-04", "date_approximate": False, "views": 1059,
        "duration_seconds": 605, "duration": "10:05", "type": "video",
    }
    assert "popular" not in out


def test_popular_scans_every_page_and_sorts_by_views(api, cli):
    code, out = cli(channel_videos, "https://www.youtube.com/@Demo/videos", "--popular", "2")
    assert code == 0
    assert [v["id"] for v in out["popular"]] == ["vid00000007", "vid00000003"]
    assert out["popular_scanned"] == 60
    assert out["popular_complete"] is True
    assert "latest" not in out


def test_latest_and_popular_together(api, cli):
    code, out = cli(channel_videos, CH, "--latest", "1", "--popular", "1")
    assert code == 0
    assert [v["id"] for v in out["latest"]] == ["vid00000059"]
    assert [v["id"] for v in out["popular"]] == ["vid00000007"]


def test_no_flags_means_latest_50(api, cli):
    code, out = cli(channel_videos, "@demo")
    assert code == 0
    assert len(out["latest"]) == 50


def test_shorts_and_live_are_opt_in(api, cli):
    _, plain = cli(channel_videos, "@demo", "--popular", "60")
    assert {v["type"] for v in plain["popular"]} == {"video"}

    _, mixed = cli(channel_videos, "@demo", "--popular", "3", "--include", "shorts,live")
    assert [(v["id"], v["type"]) for v in mixed["popular"]] == [
        ("short000001", "short"), ("live0000001", "live"), ("vid00000007", "video")]
    assert mixed["popular"][1]["duration"] == "1:02:03"

    _, latest = cli(channel_videos, "@demo", "--latest", "2", "--include", "shorts")
    assert [v["id"] for v in latest["latest"]] == ["short000002", "short000001"]


def test_channel_without_shorts_is_not_an_error(api, cli):
    del api.playlists["UUSH" + CH[2:]]  # the real API answers 404 playlistNotFound
    code, out = cli(channel_videos, "@demo", "--latest", "1", "--include", "shorts")
    assert code == 0
    assert out["latest"][0]["id"] == "vid00000059"


def test_hidden_view_counts_sort_last(api, cli):
    for video in api.videos.values():
        video["statistics"].pop("viewCount")
    api.videos["vid00000010"]["statistics"]["viewCount"] = "5"
    _, out = cli(channel_videos, "@demo", "--popular", "2")
    assert out["popular"][0]["id"] == "vid00000010"
    assert out["popular"][1]["views"] is None


def test_unknown_channel_is_final_and_does_not_fall_back(api, cli, monkeypatch):
    ytdlp = install_fake_ytdlp(monkeypatch, {})
    code, out = cli(channel_videos, "@nobody-here")
    assert code == 1
    assert out["error"]["code"] == "NOT_FOUND"
    assert ytdlp.calls == []


def test_never_uses_the_expensive_search_endpoint(api, cli):
    cli(channel_videos, "@demo", "--latest", "5", "--popular", "5", "--include", "shorts,live")
    assert "search" not in api.endpoints_called()


# ---------------------------------------------------------------- local backend (yt-dlp)

def flat_tab(title, entries):
    return {"_type": "playlist", "id": CH, "title": f"Demo Channel - {title}", "channel": "Demo Channel",
            "channel_id": CH, "uploader_id": "@Demo", "channel_url": f"https://www.youtube.com/channel/{CH}",
            "entries": entries}


def flat_entry(video_id, title, views, timestamp, duration=605.0):
    return {"_type": "url", "ie_key": "Youtube", "id": video_id, "url": f"https://www.youtube.com/watch?v={video_id}",
            "title": title, "duration": duration, "view_count": views, "timestamp": timestamp,
            "release_timestamp": None, "live_status": None}


LOCAL_TABS = {
    "https://www.youtube.com/@demo/videos": flat_tab("Videos", [
        flat_entry("vid00000002", "Newest", 10, 1772600000),     # 2026-03-04
        flat_entry("vid00000001", "Middle", 900, 1770000000),    # 2026-02-02
        flat_entry("vid00000000", "Oldest", 50, 1767300000),     # 2026-01-01
    ]),
    "https://www.youtube.com/@demo/shorts": "ERROR: [youtube:tab] @demo: This channel does not have a shorts tab",
}


def test_without_keys_uses_yt_dlp_with_approximate_dates(cli, monkeypatch):
    ytdlp = install_fake_ytdlp(monkeypatch, LOCAL_TABS)
    code, out = cli(channel_videos, "@demo", "--latest", "2", "--popular", "1", "--include", "shorts")
    assert code == 0
    assert out["source"] == "local"
    assert out["channel"] == {"id": CH, "title": "Demo Channel", "handle": "@Demo",
                              "url": f"https://www.youtube.com/channel/{CH}"}
    assert out["latest"][0] == {
        "id": "vid00000002", "title": "Newest", "url": "https://www.youtube.com/watch?v=vid00000002",
        "upload_date": "2026-03-04", "date_approximate": True, "views": 10,
        "duration_seconds": 605, "duration": "10:05", "type": "video",
    }
    assert [v["id"] for v in out["popular"]] == ["vid00000001"]
    assert ytdlp.calls[0][1]["extract_flat"] == "in_playlist"


def test_exact_dates_fetches_each_returned_video(cli, monkeypatch):
    tabs = dict(LOCAL_TABS)
    tabs["https://www.youtube.com/watch?v=vid00000002"] = {"id": "vid00000002", "upload_date": "20260303"}
    install_fake_ytdlp(monkeypatch, tabs)
    _, out = cli(channel_videos, "@demo", "--latest", "1", "--exact-dates")
    assert out["latest"][0]["upload_date"] == "2026-03-03"
    assert out["latest"][0]["date_approximate"] is False


def test_quota_exceeded_falls_back_to_local(api, cli, monkeypatch):
    api.error = QUOTA_EXCEEDED
    install_fake_ytdlp(monkeypatch, LOCAL_TABS)
    code, out = cli(channel_videos, "@demo", "--latest", "1")
    assert code == 0
    assert out["source"] == "local"


def test_both_backends_failing_reports_cloud_error_and_both_attempts(api, cli, monkeypatch):
    api.error = QUOTA_EXCEEDED
    code, out = cli(channel_videos, "@demo")  # yt-dlp is not installed in this test
    assert code == 1
    assert out["error"]["code"] == "QUOTA_EXCEEDED"
    assert "MISSING_DEPENDENCY" in out["error"]["message"]


def test_missing_yt_dlp_without_keys_says_how_to_install(cli):
    code, out = cli(channel_videos, "@demo")
    assert code == 1
    assert out["error"]["code"] == "MISSING_DEPENDENCY"
    assert "pip install" in out["error"]["hint"]


def test_bot_check_is_reported_as_ip_blocked(cli, monkeypatch):
    install_fake_ytdlp(monkeypatch, {
        "https://www.youtube.com/@demo/videos":
            "ERROR: [youtube:tab] @demo: Sign in to confirm you’re not a bot. Use --cookies-from-browser",
    })
    code, out = cli(channel_videos, "@demo")
    assert code == 1
    assert out["error"]["code"] == "IP_BLOCKED"
    assert "YT_API_KEY" in out["error"]["hint"]


def test_bad_arguments_are_json_errors_not_usage_text(cli):
    code, out = cli(channel_videos, "@demo", "--include", "podcasts")
    assert code == 1
    assert out["error"]["code"] == "BAD_INPUT"
    assert "shorts and live" in out["error"]["message"]
