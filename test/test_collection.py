from __future__ import unicode_literals

import pytest

from _common import *
from boardgamegeek import BGGError, BGGValueError, BGGItemNotFoundError
from boardgamegeek.objects.collection import CollectionBoardGame, Collection
from boardgamegeek.objects.games import BoardGameVersion
import time


def setup_module():
    # more delays to prevent throttling from the BGG api
    time.sleep(15)


def test_get_collection_with_invalid_parameters(bgg):
    for invalid in [None, ""]:
        with pytest.raises(BGGValueError):
            bgg.collection(invalid)


def test_get_invalid_users_collection(bgg):
    with pytest.raises(BGGItemNotFoundError):
        bgg.collection(TEST_INVALID_USER)


def test_get_valid_users_collection(bgg, null_logger):
    collection = bgg.collection(TEST_VALID_USER, versions=True)

    assert collection is not None
    assert collection.owner == TEST_VALID_USER
    assert type(len(collection)) == int
    assert type(collection.items) == list

    # make sure we can iterate through the collection
    for g in collection:
        assert type(g) == CollectionBoardGame
        assert type(g.id) == int
        if g.version is not None:
            assert type(g.version) == BoardGameVersion
        repr(g)

    str(collection)
    repr(collection)

    # for coverage's sake
    collection._format(null_logger)
    assert type(collection.data()) == dict

    collection = bgg.collection(TEST_VALID_USER, versions=False)
    for g in collection:
        assert g.version is None

    # TODO: test the filters for the collection


def test_creating_collection_out_of_raw_data():
    # test raise exception if invalid items given
    with pytest.raises(BGGError):
        Collection({"items": [{"id": 102}]})

    # test that items are added to the collection from the constructor
    c = Collection({"owner": "me",
                    "items": [{"id": 100,
                               "name": "foobar",
                               "image": "",
                               "thumbnail": "",
                               "yearpublished": 1900,
                               "minplayers": 1,
                               "maxplayers": 5,
                               "minplaytime": 60,
                               "maxplaytime": 120,
                               "playingtime": 100,
                               "stats": {
                                    "usersrated": 123,
                                    "ranks": [{
                                        "id": "1", "type": "subtype", "name": "boardgame", "friendlyname": "friendly",
                                        "value": "10", "bayesaverage": "0.51"
                                    }]
                                }

                               }]})

    assert len(c) == 1
    assert c.owner == "me"

    ci = c[0]

    assert type(ci) == CollectionBoardGame
    assert ci.id == 100
    assert ci.name == "foobar"
    assert ci.year == 1900
    assert ci.min_players == 1
    assert ci.max_players == 5
    assert ci.min_playing_time == 60
    assert ci.max_playing_time == 120
    assert ci.playing_time == 100
    assert ci.bgg_rank == 10
    assert ci.users_rated == 123
    assert ci.rating_bayes_average is None

    with pytest.raises(BGGError):
        # raises exception on invalid game data
        c.add_game({"bla": "bla"})