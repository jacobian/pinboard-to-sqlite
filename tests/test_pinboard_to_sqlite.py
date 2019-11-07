import pytest
import json
import pinboard_to_sqlite.cli
import sqlite_utils
import pathlib


@pytest.fixture
def db():
    return sqlite_utils.Database(memory=True)


@pytest.fixture
def posts():
    p = pathlib.Path(__file__).parent / "posts.json"
    return json.load(open(p))


def test_posts(db, posts):
    pinboard_to_sqlite.cli._save_posts(db, posts)
    assert ["posts"] == db.table_names()
    rows = list(db["posts"].rows)
    assert len(rows) == len(posts)
    assert set(p["href"] for p in posts) == set(r["href"] for r in rows)
