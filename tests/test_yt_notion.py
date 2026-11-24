import importlib.util
from pathlib import Path

spec = importlib.util.spec_from_file_location("yt_notion", Path(__file__).resolve().parent.parent / "yt_notion.py")
yn = importlib.util.module_from_spec(spec)
spec.loader.exec_module(yn)

SAMPLE = """Title: W2 Epi9   Part 1
URL: https://www.youtube.com/watch?v=3T5SZjlj2vI&t=42s

Okay, are you ready to give some feedback? Because as I said before.
"""


def test_parses_the_extension_format():
    assert yn.parse(SAMPLE) == ("W2 Epi9 Part 1", "https://www.youtube.com/watch?v=3T5SZjlj2vI",
                                "Okay, are you ready to give some feedback? Because as I said before.")


def test_ignores_other_clipboard_text():
    assert yn.parse("just some text https://www.youtube.com/watch?v=3T5SZjlj2vI") is None
    assert yn.parse("Title: x\nURL: https://example.com/page\n\ntext") is None
    assert yn.parse("Title: x\nURL: https://youtu.be/3T5SZjlj2vI\n\n") is None   # no transcript


def test_splits_long_transcripts_to_fit_notion_limits():
    blocks = yn.code_blocks("a" * (yn.CHUNK * 150 + 5))
    assert [len(b["code"]["rich_text"]) for b in blocks] == [100, 51]
    assert "".join(p["text"]["content"] for b in blocks for p in b["code"]["rich_text"]) == "a" * (yn.CHUNK * 150 + 5)


class FakeNotion:
    def __init__(self, existing=None):
        self.existing, self.calls = existing or [], []

    def __call__(self, method, path, body=None):
        self.calls.append((method, path, body))
        return {"results": self.existing} if path.endswith("/query") else {}


def page(status):
    return {"id": "p1", "properties": {"Status": {"select": {"name": status} if status else None}}}


def test_new_video_becomes_a_page_with_status_new():
    notion = FakeNotion()
    assert yn.file_video(SAMPLE, notion) == "✓ Added: W2 Epi9 Part 1 (13 words)"
    method, path, body = notion.calls[-1]
    assert (method, path) == ("POST", "/pages")
    assert body["properties"]["Link"] == {"url": "https://www.youtube.com/watch?v=3T5SZjlj2vI"}
    assert body["properties"]["Status"] == {"select": {"name": "New"}}


def test_title_only_row_gets_the_transcript():
    notion = FakeNotion([page("No transcript")])
    assert yn.file_video(SAMPLE, notion).startswith("✓ Transcript added")
    assert [(m, p) for m, p, _ in notion.calls[1:]] == [("PATCH", "/blocks/p1/children"), ("PATCH", "/pages/p1")]


def test_video_with_a_transcript_already_is_skipped():
    for status in ("New", "Filed", None):
        notion = FakeNotion([page(status)])
        assert yn.file_video(SAMPLE, notion).startswith("- Skipped")
        assert len(notion.calls) == 1


def test_non_transcript_text_makes_no_calls():
    notion = FakeNotion()
    assert yn.file_video("hello", notion) is None
    assert notion.calls == []
