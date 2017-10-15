import datetime
import time

from _common import *
from boardgamegeek import BGGError, BGGValueError, BGGItemNotFoundError
from boardgamegeek.objects.plays import UserPlays, GamePlays, PlaySession, Plays


progress_called = False


def setup_module():
    # more delays to prevent throttling from the BGG api
    time.sleep(15)


def progress_cb(items, total):
    global progress_called
    logging.debug("progress_cb: fetched {} items out of {}".format(items, total))
    progress_called = True


def test_get_plays_with_invalid_parameters(bgg):
    with pytest.raises(BGGValueError):
        bgg.plays(name=None, game_id=None)

    with pytest.raises(BGGValueError):
        bgg.plays(name="", game_id=None)

    with pytest.raises(BGGValueError):
        bgg.plays(name=None, game_id="asd")


def test_get_plays_with_unknown_username_and_id(bgg):
    with pytest.raises(BGGItemNotFoundError):
        bgg.plays(name=TEST_INVALID_USER)

    with pytest.raises(BGGItemNotFoundError):
        bgg.plays(name=None, game_id=1928391829)


def test_get_plays_with_invalid_dates(bgg):
    # A string is invalid so should raise an error
    with pytest.raises(BGGValueError):
        bgg.plays(name=TEST_VALID_USER, min_date="2014-01-01")

    with pytest.raises(BGGValueError):
        bgg.plays(name=TEST_VALID_USER, max_date="2014-12-31")


def test_get_plays_with_valid_dates(bgg):
    min_date = datetime.date(2014, 1, 1)
    max_date = datetime.date(2014, 12, 31)
    plays = bgg.plays(TEST_VALID_USER, min_date=min_date, max_date=max_date)
    assert len(plays) > 0


def test_get_plays_of_user(bgg, null_logger):
    global progress_called

    plays = bgg.plays(name=TEST_VALID_USER, progress=progress_cb)

    assert type(plays) == UserPlays
    assert plays.user == TEST_VALID_USER
    assert plays.user_id == TEST_VALID_USER_ID

    for p in plays.plays:
        assert type(p.id) == int
        assert p.user_id == TEST_VALID_USER_ID
        assert type(p.date) == datetime.datetime
        assert p.quantity >= 0
        assert p.duration >= 0
        assert type(p.incomplete) == bool
        assert type(p.nowinstats) == int
        assert type(p.game_id) == int
        assert type(p.game_name) == str
        assert type(p.comment) in [type(None), str]

        assert type(p.players) == list
        if p.players:
            for player in p.players:
                assert hasattr(player, "startposition")
                assert hasattr(player, "username")
                assert hasattr(player, "user_id")
                assert hasattr(player, "name")
                assert hasattr(player, "score")
                assert hasattr(player, "new")
                assert hasattr(player, "win")
                assert hasattr(player, "rating")
                assert hasattr(player, "color")
                assert hasattr(player, "location")

    plays._format(null_logger)


def test_get_plays_of_game(bgg, null_logger):
    global progress_called

    plays = bgg.plays(game_id=TEST_GAME_ID_2, progress=progress_cb)

    assert type(plays) == GamePlays

    assert plays.game_id == TEST_GAME_ID_2

    for p in plays.plays:
        assert type(p.id) == int
        assert type(p.user_id) == int
        assert type(p.date) in [datetime.datetime, type(None)]
        assert p.quantity >= 0
        assert p.duration >= 0
        assert type(p.incomplete) == bool
        assert type(p.nowinstats) == int
        assert p.game_id == TEST_GAME_ID_2
        assert p.game_name == TEST_GAME_NAME_2

    plays._format(null_logger)


def test_create_plays_with_initial_data():

    with pytest.raises(BGGError):
        Plays({"plays": [{"user_id": 10}]})

    p = Plays({"plays": [{"id": 10, "user_id": 102, "date": "2014-01-02"}]})

    assert len(p) == 1
    assert type(p[0]) == PlaySession
    assert p[0].id == 10
    assert p[0].user_id == 102
    assert type(p[0].date) == datetime.datetime
    assert p[0].date.strftime("%Y-%m-%d") == "2014-01-02"

    # it also accepts datetime objects
    now = datetime.datetime.utcnow()
    p = Plays({"plays": [{"id": 10, "user_id": 102, "date": now}]})

    assert p[0].date == now
