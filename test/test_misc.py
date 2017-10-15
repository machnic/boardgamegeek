import os
import tempfile
import time

from _common import *
from boardgamegeek import BGGValueError, CacheBackendNone, CacheBackendSqlite


def setup_module():
    # more delays to prevent throttling from the BGG api
    time.sleep(15)

#
# Test caches
#
def test_no_caching():
    # test that we can disable caching
    bgg = BGGClient(cache=CacheBackendNone())

    user = bgg.user(TEST_VALID_USER)

    assert user is not None
    assert user.name == TEST_VALID_USER


def test_sqlite_caching():
    # test that we can use the SQLite cache
    # generate a temporary file
    fd, name = tempfile.mkstemp(suffix=".cache")

    # close the file and unlink it, we only need the temporary name
    os.close(fd)
    os.unlink(name)

    assert not os.path.isfile(name)

    with pytest.raises(BGGValueError):
        # invalid value for the ttl parameter
        BGGClient(cache=CacheBackendSqlite(name, ttl="blabla", fast_save=False))

    bgg = BGGClient(cache=CacheBackendSqlite(name, ttl=1000))

    user = bgg.user(TEST_VALID_USER)
    assert user is not None
    assert user.name == TEST_VALID_USER

    assert os.path.isfile(name)

    # clean up..
    os.unlink(name)


def test_invalid_parameter_values_for_bggclient():
    with pytest.raises(BGGValueError):
        BGGClient(retries="asd")

    with pytest.raises(BGGValueError):
        BGGClient(retry_delay="asd")

    with pytest.raises(BGGValueError):
        BGGClient(timeout="asd")