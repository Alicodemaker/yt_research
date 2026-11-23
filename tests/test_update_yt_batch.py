import importlib.util
from pathlib import Path

spec = importlib.util.spec_from_file_location(
    "update_yt_batch", Path(__file__).resolve().parent.parent / "tools" / "update_yt_batch.py")
ub = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ub)

PAGE = """<toggle>
🆕 new yt vids
[<b>Has transcript</b>](https://www.youtube.com/watch?v=AAAAAAAAAAA)
</toggle>

<toggle>
⏳ new yt vids (no transcript)

<toggle>
[<b>First \\$29k video</b>](https://www.youtube.com/watch?v=-bv2xKQzZio)
</toggle>

<toggle>
[Second](https://youtu.be/BBBBBBBBBBB?si=x)
</toggle>

<toggle>
[<b>First \\$29k video</b>](https://www.youtube.com/watch?v=-bv2xKQzZio)
</toggle>
</toggle>

[<b>After the toggle</b>](https://www.youtube.com/watch?v=CCCCCCCCCCC)
"""


def test_only_videos_in_the_no_transcript_toggle_without_duplicates():
    assert ub.toggle_videos(PAGE) == [("-bv2xKQzZio", "First $29k video"), ("BBBBBBBBBBB", "Second")]


def test_reads_saved_notion_fetch_json():
    assert ub.page_text('{"text": "hi"}') == "hi"
    assert ub.page_text("plain markdown") == "plain markdown"


def test_replaces_only_the_video_list():
    script = "A = 1\nVIDEOS = [\n    ('old', 'Old'),\n]\n\nB = 2\n"
    assert ub.with_videos(script, [("x", "It's")]) == "A = 1\nVIDEOS = [\n    ('x', \"It's\"),\n]\n\nB = 2\n"
