import importlib.util
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))   # yt_migrate imports yt_notion from next to it
spec = importlib.util.spec_from_file_location("yt_migrate", ROOT / "yt_migrate.py")
ym = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ym)


def toggle(id, text, kids=(), href=None, kind="toggle"):
    rich = [{"plain_text": text, "href": href}]
    return {"id": id, "type": kind, kind: {"rich_text": rich}, "has_children": bool(kids), "kids": list(kids)}


def code(text):
    return {"id": "c", "type": "code", "code": {"rich_text": [{"plain_text": text}]}, "has_children": False}


def video(id, title, vid, transcript=None):
    kids = [toggle(id + "t", "transcript", [code(transcript)])] if transcript is not None else []
    return toggle(id, title, kids, href=f"https://www.youtube.com/watch?v={vid}")


PAGE = [
    toggle("h1", "📥 resources inbox", [
        toggle("new", "🆕 new yt vids", [video("n1", "Fresh one", "NNNNNNNNNNN", "fresh words")]),
        toggle("wait", "⏳ new yt vids (no transcript)", [
            video("w1", "Pasted", "PPPPPPPPPPP", "pasted words"),
            video("w2", "Still empty", "EEEEEEEEEEE", ""),
        ]),
    ], kind="heading_3"),
    toggle("old", "yt vids", [
        video("o1", "Old video", "OOOOOOOOOOO", "old words"),
        toggle("o2", "a note without a link", [code("x")]),
    ]),
]


class FakeNotion:
    def __init__(self, in_db=()):
        self.blocks, self.created, self.in_db = {}, [], set(in_db)
        self._index(ym.PAGE_ID, PAGE)

    def _index(self, parent, blocks):
        self.blocks[parent] = blocks
        for b in blocks:
            self._index(b["id"], b.get("kids", []))

    def __call__(self, method, path, body=None):
        if method == "GET":
            kids = self.blocks[path.split("/")[2]]
            first = "start_cursor=" not in path   # serve 2 per page to exercise pagination
            page = kids[:2] if first else kids[2:]
            return {"results": page, "has_more": first and len(kids) > 2, "next_cursor": "next"}
        if path.endswith("/query"):
            return {"results": [1] if body["filter"]["url"]["equals"] in self.in_db else []}
        self.created.append(body)
        return {}


def test_plan_finds_every_video_with_the_right_status():
    rows, odd, missing = ym.plan(FakeNotion())
    assert {(t, s) for t, _, _, s in rows} == {
        ("Fresh one", "New"), ("Pasted", "New"), ("Still empty", "No transcript"), ("Old video", "Filed")}
    assert dict((t, tr) for t, _, tr, _ in rows)["Old video"] == "old words"
    assert odd == ["a note without a link"] and missing == []


def test_copy_creates_pages_and_skips_ones_already_in_the_database():
    notion = FakeNotion(in_db={"https://www.youtube.com/watch?v=OOOOOOOOOOO"})
    rows, _, _ = ym.plan(notion)
    results = {row[0]: ym.copy(row, notion) for row in rows}
    assert results == {"Fresh one": True, "Pasted": True, "Still empty": True, "Old video": False}
    empty = next(p for p in notion.created if p["properties"]["Name"]["title"][0]["text"]["content"] == "Still empty")
    assert "children" not in empty and empty["properties"]["Status"] == {"select": {"name": "No transcript"}}
