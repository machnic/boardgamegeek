import logging
import datetime

from ..objects.user import User
from ..exceptions import BGGItemNotFoundError
from ..utils import xml_subelement_attr


log = logging.getLogger("boardgamegeek.loaders.user")


def create_user_from_xml(xml_root, html_parser):
    # when the user is not found, the API returns an response, but with most fields empty. id is empty too
    try:
        data = {"name": xml_root.attrib["name"],
                "id": int(xml_root.attrib["id"])}
    except (KeyError, ValueError):
        raise BGGItemNotFoundError

    for i in ["firstname", "lastname", "avatarlink",
              "stateorprovince", "country", "webaddress", "xboxaccount",
              "wiiaccount", "steamaccount", "psnaccount", "traderating"]:
        data[i] = xml_subelement_attr(xml_root, i)

    data["yearregistered"] = xml_subelement_attr(xml_root, "yearregistered", convert=int, quiet=True)
    data["lastlogin"] = xml_subelement_attr(xml_root,
                                            "lastlogin",
                                            convert=lambda x: datetime.datetime.strptime(x, "%Y-%m-%d"),
                                            quiet=True)

    return User(data)


def add_user_hot_items_from_xml(user, xml_root):
    """
    Processes the XML and adds the user's hot items
    :param user: user object to add the hot items to
    :param xml_root: XML node
    :return:
    """
    for hot_item in xml_root.findall(".//hot/item"):
        user.add_hot_item({"id": int(hot_item.attrib["id"]),
                           "name": hot_item.attrib["name"]})


def add_user_top_items_from_xml(user, xml_root):
    """
    Processes the XML and adds the user's top items
    :param user: user object to add the top items to
    :param xml_root: XML node
    :return:
    """
    for hot_item in xml_root.findall(".//hot/item"):
        user.add_hot_item({"id": int(hot_item.attrib["id"]),
                           "name": hot_item.attrib["name"]})


def add_user_buddies_from_xml(user, xml_root):
    """
    Processes the XML and adds the user's buddies
    :param user: User object to add the buddies to
    :param xml_root: XML node
    :return:
    """

    # add the buddies from the first page
    added_buddy = False

    for buddy in xml_root.findall(".//buddy"):
        user.add_buddy({"name": buddy.attrib["name"],
                        "id": buddy.attrib["id"]})
        added_buddy = True

    return added_buddy


def add_user_guilds_from_xml(user, xml_root):

    # add the guilds from the first page
    added_guilds = False
    for guild in xml_root.findall(".//guild"):
        user.add_guild({"name": guild.attrib["name"],
                        "id": guild.attrib["id"]})
        added_guilds = True

    return added_guilds