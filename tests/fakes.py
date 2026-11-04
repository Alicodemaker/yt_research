"""Fakes for the network edge: the YouTube Data API, Supadata, yt-dlp and youtube-transcript-api.

They return the same JSON / objects the real services do (shapes from the public docs),
so the scripts run end to end with no network.
"""
from __future__ import annotations

import copy
import sys
import types


def _api_error(status, reason, message, detail_reason=None):
    body = {"error": {"code": status, "message": message,
                      "errors": [{"message": message, "domain": "global", "reason": reason}]}}
    if detail_reason:
        body["error"]["details"] = [{"@type": "type.googleapis.com/google.rpc.ErrorInfo", "reason": detail_reason}]
    return status, body


QUOTA_EXCEEDED = _api_error(403, "quotaExceeded",
                            "The request cannot be completed because you have exceeded your quota.")
KEY_INVALID = _api_error(400, "badRequest", "API key not valid. Please pass a valid API key.", "API_KEY_INVALID")
PLAYLIST_NOT_FOUND = _api_error(404, "playlistNotFound",
                                "The playlist identified with the request's playlistId parameter cannot be found.")

PLAYLIST_PREFIX = {"video": "UULF", "short": "UUSH", "live": "UULV"}


class FakeDataAPI:
    """In-memory YouTube Data API v3: channels, playlistItems and videos, with paging."""

    def __init__(self, key="test-key"):
        self.key = key
        self.channels = []
        self.playlists = {}
        self.videos = {}
        self.calls = []
        self.error = None  # (status, body) returned for every call when set

    def add_channel(self, channel_id, handle, title):
        self.channels.append({
            "kind": "youtube#channel", "id": channel_id,
            "snippet": {"title": title, "customUrl": handle.lower()},
            "contentDetails": {"relatedPlaylists": {"uploads": "UU" + channel_id[2:]}},
        })

    def add_video(self, channel_id, video_id, title, published, views, duration="PT10M5S", kind="video",
                  description="", language=None):
        self.playlists.setdefault(PLAYLIST_PREFIX[kind] + channel_id[2:], []).append(video_id)
        snippet = {"publishedAt": published, "channelId": channel_id, "title": title,
                   "description": description, "channelTitle": self._title(channel_id),
                   "liveBroadcastContent": "none"}
        if language:
            snippet["defaultAudioLanguage"] = language
        statistics = {"likeCount": "1"}
        if views is not None:
            statistics["viewCount"] = str(views)
        self.videos[video_id] = {"kind": "youtube#video", "id": video_id, "snippet": snippet,
                                 "contentDetails": {"duration": duration}, "statistics": statistics}

    def _title(self, channel_id):
        return next((c["snippet"]["title"] for c in self.channels if c["id"] == channel_id), "")

    def endpoints_called(self):
        return [url.rsplit("/", 1)[-1] for url, _ in self.calls]

    def __call__(self, url, params=None, headers=None, timeout=30):
        params = dict(params or {})
        self.calls.append((url, params))
        endpoint = url.rsplit("/", 1)[-1]
        assert endpoint != "search", "search costs 100 quota units and must never be called"
        if self.error:
            return self.error
        if params.get("key") != self.key:
            return KEY_INVALID
        if endpoint == "channels":
            return 200, {"kind": "youtube#channelListResponse", **self._channels(params)}
        if endpoint == "playlistItems":
            return self._playlist_items(params)
        if endpoint == "videos":
            ids = params["id"].split(",")
            assert len(ids) <= 50, "videos.list takes at most 50 ids"
            return 200, {"items": [copy.deepcopy(self.videos[i]) for i in ids if i in self.videos]}
        raise AssertionError(f"unexpected endpoint {endpoint}")

    def _channels(self, params):
        for channel in self.channels:
            if (params.get("id") == channel["id"]
                    or (params.get("forHandle") or "").lower() == channel["snippet"]["customUrl"]
                    or (params.get("forUsername") or "").lower() == channel["snippet"]["customUrl"].lstrip("@")):
                return {"pageInfo": {"totalResults": 1}, "items": [copy.deepcopy(channel)]}
        return {"pageInfo": {"totalResults": 0}}  # the real API omits "items" when nothing matches

    def _playlist_items(self, params):
        ids = self.playlists.get(params["playlistId"])
        if ids is None:
            return PLAYLIST_NOT_FOUND
        ids = sorted(ids, key=lambda i: self.videos[i]["snippet"]["publishedAt"], reverse=True)
        size = int(params.get("maxResults", 5))
        start = int(params.get("pageToken") or 0)
        page = ids[start:start + size]
        body = {"items": [{"kind": "youtube#playlistItem",
                           "contentDetails": {"videoId": i,
                                              "videoPublishedAt": self.videos[i]["snippet"]["publishedAt"]}}
                          for i in page],
                "pageInfo": {"totalResults": len(ids), "resultsPerPage": size}}
        if start + size < len(ids):
            body["nextPageToken"] = str(start + size)
        return 200, body


def install_fake_ytdlp(monkeypatch, responses):
    """Install a fake `yt_dlp` module. `responses` maps URL -> info dict, or -> str to raise DownloadError."""
    module = types.ModuleType("yt_dlp")
    utils = types.ModuleType("yt_dlp.utils")

    class DownloadError(Exception):
        pass

    utils.DownloadError = DownloadError
    module.utils = utils
    module.calls = []

    class YoutubeDL:
        def __init__(self, params=None):
            self.params = params or {}

        def __enter__(self):
            return self

        def __exit__(self, *exc):
            return False

        def extract_info(self, url, download=True):
            module.calls.append((url, self.params))
            result = responses.get(url, f"ERROR: [youtube] {url}: Video unavailable")
            if isinstance(result, str):
                raise DownloadError(result)
            result = copy.deepcopy(result)
            end = self.params.get("playlistend")
            if end and "entries" in result:
                result["entries"] = result["entries"][:end]
            return result

    module.YoutubeDL = YoutubeDL
    monkeypatch.setitem(sys.modules, "yt_dlp", module)
    monkeypatch.setitem(sys.modules, "yt_dlp.utils", utils)
    return module


class FakeSupadata:
    """Supadata GET /v1/transcript: falls back to `default` when the asked language is missing."""

    def __init__(self, tracks, default=None, key="supa-key"):
        self.tracks = tracks          # {"en": "plain text", ...}
        self.default = default or next(iter(tracks), None)
        self.key = key
        self.calls = []
        self.error = None             # (status, body) for every call when set
        self.job = False              # answer 202 + jobId first, like long or AI transcripts

    def __call__(self, url, params=None, headers=None, timeout=30):
        params = dict(params or {})
        self.calls.append((url, params, dict(headers or {})))
        if (headers or {}).get("x-api-key") != self.key:
            return 401, {"error": "unauthorized", "message": "Invalid API key"}
        if self.error:
            return self.error
        if url.endswith("/transcript/job-1"):
            return 200, {"status": "completed", **self._answer(self.default)}
        if not self.tracks:
            return 404, {"error": "transcript-unavailable", "message": "No transcript is available for this video"}
        if self.job:
            return 202, {"jobId": "job-1"}
        return 200, self._answer(params.get("lang") if params.get("lang") in self.tracks else self.default)

    def _answer(self, lang):
        return {"content": self.tracks[lang], "lang": lang, "availableLangs": list(self.tracks)}

    def langs_requested(self):
        return [params.get("lang") for _, params, _ in self.calls]


SUPADATA_OUT_OF_CREDITS = (429, {"error": "limit-exceeded", "message": "Monthly credit limit exceeded"})


def route(**fakes):
    """One fetch_json fake that sends each host to its fake service."""

    def fetch(url, params=None, headers=None, timeout=30):
        for host, fake in fakes.items():
            if host in url:
                return fake(url, params, headers, timeout)
        raise AssertionError(f"unexpected network call to {url}")

    return fetch


def install_fake_transcripts(monkeypatch, tracks=(), error=None):
    """Install a fake `youtube_transcript_api`.

    `tracks` are (language_code, is_generated, text) tuples; text segments are split on "|".
    `error` is an exception class name to raise from list(), e.g. "TranscriptsDisabled".
    """
    module = types.ModuleType("youtube_transcript_api")
    proxies = types.ModuleType("youtube_transcript_api.proxies")
    module.created = []

    class GenericProxyConfig:
        def __init__(self, http_url=None, https_url=None):
            self.http_url, self.https_url = http_url, https_url

    class Snippet:
        def __init__(self, text):
            self.text, self.start, self.duration = text, 0.0, 1.0

    class Fetched:
        def __init__(self, track):
            self.language_code, self.is_generated = track.language_code, track.is_generated
            self.snippets = [Snippet(part) for part in track.text.split("|")]

    class Track:
        def __init__(self, language_code, is_generated, text):
            self.language_code, self.is_generated, self.text = language_code, is_generated, text
            self.language = language_code

        def fetch(self):
            return Fetched(self)

    class YouTubeTranscriptApi:
        def __init__(self, proxy_config=None, http_client=None):
            self.proxy_config = proxy_config
            module.created.append(self)

        def list(self, video_id):
            if error:
                raise type(error, (Exception,), {})(
                    f"\nCould not retrieve a transcript for the video https://www.youtube.com/watch?v={video_id}!"
                    f" This is most likely caused by:\n\n{error} happened\n\nIf you are sure that the described"
                    " cause is not responsible for this error, please open an issue.")
            return iter([Track(*t) for t in tracks])

    proxies.GenericProxyConfig = GenericProxyConfig
    module.proxies = proxies
    module.YouTubeTranscriptApi = YouTubeTranscriptApi
    monkeypatch.setitem(sys.modules, "youtube_transcript_api", module)
    monkeypatch.setitem(sys.modules, "youtube_transcript_api.proxies", proxies)
    return module
