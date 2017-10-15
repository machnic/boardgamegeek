import time

from _common import *
from boardgamegeek import BGGValueError, BGGRestrictSearchResultsTo


def setup_module():
    # more delays to prevent throttling from the BGG api
    time.sleep(15)


def test_search(bgg):
    res = bgg.search("some invalid game name", exact=True)
    assert not len(res)

    res = bgg.search("Twilight Struggle", exact=True)
    assert len(res)

    # test that the new type of search works
    res = bgg.search("Agricola", search_type=[BGGRestrictSearchResultsTo.BOARD_GAME])
    assert type(res[0].id) == int

    with pytest.raises(BGGValueError):
        bgg.search("Agricola", search_type=["invalid-search-type"])


