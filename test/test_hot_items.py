import time

from boardgamegeek import BGGError, BGGValueError
from boardgamegeek.objects.hotitems import HotItems, HotItem

from _common import *


def setup_module():
    # more delays to prevent throttling from the BGG api
    time.sleep(15)


def test_get_hot_items_invalid_type(bgg):
    with pytest.raises(BGGValueError):
        bgg.hot_items("invalid type")


def test_get_hot_items_boardgames(bgg, null_logger):
    for item in bgg.hot_items("boardgame"):
        assert type(item.id) == int
        assert len(item.name) > 0
        assert type(item.rank) == int
        assert type(item.year) in [int, type(None)]
        # test that all thumbnails have been fixed (http:// added)
        # note: I guess this could fail if the boardgame has no thumbnail...
        assert item.thumbnail.startswith("https://")
        item._format(null_logger)


def test_get_hot_items_boardgamepersons(bgg, null_logger):
    for item in bgg.hot_items("boardgameperson"):
        assert type(item.id) == int
        assert len(item.name) > 0
        assert type(item.rank) == int
        assert item.year is None

        item._format(null_logger)


def test_hot_items_initial_data():

    # test that exception is raised if invalid initial data is given when trying to create a HotItems object
    with pytest.raises(BGGError):
        HotItems({"items": [{"id": 100, "name": "hotitem"}]})

    h = HotItems({"items": [{"id": 100, "name": "hotitem", "rank": 10}]})
    with pytest.raises(BGGError):
        h.add_hot_item({"id": 100, "name": "hotitem"})

    assert type(h[0]) == HotItem
    assert len(h) == 1
    assert h[0].id == 100
    assert h[0].name == "hotitem"
    assert h[0].rank == 10
