"""Seam A: every way a person or Claude might name a video or a channel."""
import pytest

from _common import YTError, parse_channel, parse_video_id

VID = "dQw4w9WgXcQ"


@pytest.mark.parametrize(
    "text",
    [
        VID,
        f"https://www.youtube.com/watch?v={VID}",
        f"https://www.youtube.com/watch?feature=share&v={VID}&t=42s",
        f"https://youtu.be/{VID}?si=abc",
        f"https://m.youtube.com/watch?v={VID}",
        f"https://music.youtube.com/watch?v={VID}&list=RD123",
        f"https://www.youtube.com/shorts/{VID}",
        f"https://www.youtube.com/live/{VID}?feature=share",
        f"https://www.youtube.com/embed/{VID}",
        f"youtube.com/watch?v={VID}",
        f"  {VID}  ",
    ],
)
def test_video_id_from_any_common_form(text):
    assert parse_video_id(text) == VID


@pytest.mark.parametrize(
    "text",
    ["", "hello", "https://www.youtube.com/@veritasium", "https://vimeo.com/12345678", "dQw4w9WgXc"],
)
def test_bad_video_input_is_a_clear_error(text):
    with pytest.raises(YTError) as err:
        parse_video_id(text)
    assert err.value.code == "BAD_INPUT"


@pytest.mark.parametrize(
    "text, expected",
    [
        ("@veritasium", ("handle", "@veritasium")),
        ("veritasium", ("handle", "@veritasium")),
        ("https://www.youtube.com/@veritasium", ("handle", "@veritasium")),
        ("https://www.youtube.com/@veritasium/videos", ("handle", "@veritasium")),
        ("youtube.com/@Kurzgesagt?si=x", ("handle", "@Kurzgesagt")),
        ("https://www.youtube.com/@3blue1brown.official", ("handle", "@3blue1brown.official")),
        ("UCHnyfMqiRRG1u-2MsSQLbXA", ("id", "UCHnyfMqiRRG1u-2MsSQLbXA")),
        ("https://www.youtube.com/channel/UCHnyfMqiRRG1u-2MsSQLbXA/videos", ("id", "UCHnyfMqiRRG1u-2MsSQLbXA")),
        ("https://www.youtube.com/user/1veritasium", ("user", "1veritasium")),
        ("https://www.youtube.com/c/veritasium", ("custom", "veritasium")),
    ],
)
def test_channel_from_any_common_form(text, expected):
    assert parse_channel(text) == expected


def test_video_url_given_as_channel_points_to_video_info():
    with pytest.raises(YTError) as err:
        parse_channel(f"https://www.youtube.com/watch?v={VID}")
    assert err.value.code == "BAD_INPUT"
    assert "video_info.py" in err.value.hint


@pytest.mark.parametrize("text", ["", "https://vimeo.com/user/abc", "two words"])
def test_bad_channel_input_is_a_clear_error(text):
    with pytest.raises(YTError) as err:
        parse_channel(text)
    assert err.value.code == "BAD_INPUT"
