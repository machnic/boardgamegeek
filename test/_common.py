import logging
import pytest
import xml.etree.ElementTree as ET


from boardgamegeek import BGGClient, CacheBackendNone


# Kinda hard to test without having a "test" user
TEST_VALID_USER = "fagentu007"
TEST_VALID_USER_ID = 818216
TEST_USER_WITH_LOTS_OF_FRIENDS = "Solamar"        # user chosen randomly (..after a long search :)) ), just needed
                                                  # someone with lots of friends :D
TEST_INVALID_USER = "someOneThatHopefullyWontExistPlsGuysDontCreateThisUser"
TEST_INVALID_GAME_NAME = "blablablathisgamewonteverexist"
TEST_GAME_NAME = "Agricola"
TEST_GAME_ID = 31260

#TEST_GAME_NAME_2 = "Merchant of Venus (second edition)"
#TEST_GAME_ID_2 = 131646

TEST_GAME_NAME_2 = "Advanced Third Reich"
TEST_GAME_ID_2 = 283

TEST_GUILD_ID = 1229
TEST_GUILD_ID_2 = 930


@pytest.fixture
def xml():
    xml_code = """
    <root>
        <node1 attr="hello1" int_attr="1">text</node1>
        <node2 attr="hello2" int_attr="2" />
        <list>
            <li attr="elem1" int_attr="1" />
            <li attr="elem2" int_attr="2" />
            <li attr="elem3" int_attr="3" />
            <li attr="elem4" int_attr="4" />
        </list>
    </root>
    """
    return ET.fromstring(xml_code)


@pytest.fixture
def bgg():
    return BGGClient(cache=CacheBackendNone(), retries=2, retry_delay=1)


@pytest.fixture
def null_logger():
    # create logger
    logger = logging.getLogger("null")
    logger.setLevel(logging.ERROR)
    return logger
