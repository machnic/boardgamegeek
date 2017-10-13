# coding: utf-8
import datetime
import sys
import time

from _common import *
from boardgamegeek import BGGError, BGGItemNotFoundError, BGGValueError
from boardgamegeek.objects.games import BoardGameVideo, BoardGameVersion, BoardGameRank
from boardgamegeek.objects.games import PlayerSuggestion

if sys.version_info >= (3,):
    STR_TYPES_OR_NONE = [str, type(None)]
else:
    STR_TYPES_OR_NONE = [str, unicode, type(None)]


def setup_module():
    # more delays to prevent throttling from the BGG api
    time.sleep(15)


def test_get_unknown_game_info(bgg):

    with pytest.raises(BGGItemNotFoundError):
        game = bgg.game(TEST_INVALID_GAME_NAME)


def test_get_game_with_invalid_parameters(bgg):
    with pytest.raises(BGGError):
        bgg.game(name=None, game_id=None)

    for invalid in [None, ""]:
        with pytest.raises(BGGError):
            bgg.game(invalid)

    for invalid in [None, "", "asd"]:
        with pytest.raises(BGGError):
            bgg.game(None, game_id=invalid)


def check_game(game):
    assert game is not None
    assert game.name == TEST_GAME_NAME
    assert game.id == TEST_GAME_ID
    assert game.year == 2007
    assert game.mechanics == ['Card Drafting', 'Hand Management',
                              'Variable Player Powers', 'Worker Placement']
    assert game.min_players == 1
    assert game.max_players == 5
    assert game.thumbnail == "https://cf.geekdo-images.com/images/pic259085_t.jpg"
    assert game.image == "https://cf.geekdo-images.com/images/pic259085.jpg"
    assert game.playing_time > 100
    assert game.min_age == 12

    assert "Economic" in game.categories
    assert "Farming" in game.categories

    assert game.families == ['Agricola', 'Animals: Cattle', 'Animals: Horses',
                             'Animals: Pigs', 'Animals: Sheep', 'Harvest Series',
                             'Solitaire Games', 'Tableau Building']
    assert game.designers == ["Uwe Rosenberg"]

    assert "Lookout Games" in game.publishers
    assert u"Compaya.hu - Gamer Café Kft." in game.publishers

    assert u"Агрикола" in game.alternative_names
    assert u"아그리콜라" in game.alternative_names

    # some not so exact assertions
    assert game.users_rated >= 34000
    assert 0.0 <= game.rating_average <= 10.0
    assert 0.0 <= game.rating_bayes_average <= 10.0

    assert type(game.rating_stddev) == float
    assert type(game.rating_median) == float
    assert game.rating_num_weights >= 0
    assert type(game.rating_average_weight) == float

    assert type(game.boardgame_rank) == int


    # check for videos
    assert type(game.videos) == list
    assert len(game.videos) > 0
    for vid in game.videos:
        assert type(vid) == BoardGameVideo
        assert type(vid.id) == int
        assert type(vid.name) in STR_TYPES_OR_NONE
        assert type(vid.category) in STR_TYPES_OR_NONE
        assert type(vid.language) in STR_TYPES_OR_NONE
        assert type(vid.uploader) in STR_TYPES_OR_NONE
        assert vid.link.startswith("http")
        assert type(vid.uploader_id) == int
        assert type(vid.post_date) == datetime.datetime

    # check for versions
    assert type(game.versions) == list
    assert len(game.versions) > 0
    for ver in game.versions:
        assert type(ver) == BoardGameVersion
        assert type(ver.id) == int
        assert type(ver.name) in STR_TYPES_OR_NONE
        assert type(ver.language) in STR_TYPES_OR_NONE
        assert type(ver.publisher) in STR_TYPES_OR_NONE
        assert type(ver.artist) in STR_TYPES_OR_NONE
        assert type(ver.product_code) in STR_TYPES_OR_NONE
        assert type(ver.year) == int
        assert type(ver.width) == float
        assert type(ver.length) == float
        assert type(ver.depth) == float
        assert type(ver.weight) == float

    # check the ranks of the result, to make sure everything is returned properly
    assert type(game.ranks) == list
    for rank in game.ranks:
        assert type(rank) == BoardGameRank
        assert type(rank.type) in STR_TYPES_OR_NONE

    # check player suggestions were retrieved
    assert type(game.player_suggestions) == list
    for suggestion in game.player_suggestions:
        assert type(suggestion) == PlayerSuggestion
        assert type(suggestion.player_count) == str
        assert type(suggestion.best) == int
        assert type(suggestion.not_recommended) == int
        assert type(suggestion.recommended) == int


    # make sure no exception gets thrown
    repr(game)


def test_get_known_game_info(bgg, null_logger):

    # use an older game that's not so likely to change
    game = bgg.game(TEST_GAME_NAME, videos=True, versions=True)

    check_game(game)

    # for coverage's sake
    game._format(null_logger)

    assert type(game.data()) == dict


def test_get_known_game_info_by_id(bgg):
    game = bgg.game(None, game_id=TEST_GAME_ID, videos=True, versions=True)
    check_game(game)


def test_get_known_game_info_by_id_list(bgg):
    game_list = bgg.game_list(game_id_list=[TEST_GAME_ID, TEST_GAME_ID_2],
                              videos=True, versions=True)
    check_game(game_list[0])


def test_game_id_with_invalid_params(bgg):
    with pytest.raises(BGGValueError):
        bgg.get_game_id(TEST_GAME_NAME, choose="voodoo")


def test_get_game_id_by_name(bgg):
    game_id = bgg.get_game_id(TEST_GAME_NAME)
    assert game_id == TEST_GAME_ID

    # Use the game "Eclipse" to test the game choosing methods
    all_eclipse_games = bgg.games("eclipse")

    game_id = bgg.get_game_id("eclipse", choose="first")
    assert game_id == all_eclipse_games[0].id

    game_id = bgg.get_game_id("eclipse", choose="recent")
    recent_year = -100000
    recent_id = None
    for g in all_eclipse_games:
        if g.year > recent_year:
            recent_id = g.id
            recent_year = g.year
    assert game_id == recent_id

    game_id = bgg.get_game_id("eclipse", choose="best-rank")
    best_rank = 1000000000
    best_id = None
    for g in all_eclipse_games:
        if g.boardgame_rank is not None and g.boardgame_rank < best_rank:
            best_id = g.id
            best_rank = g.boardgame_rank
    assert game_id == best_id


def test_get_games_by_name(bgg, null_logger):
    games = bgg.games("coup")

    for g in games:
        assert g is not None
        assert type(g.id) == int
        assert g.name == "Coup"
        g._format(null_logger)

    assert len(games) > 1
