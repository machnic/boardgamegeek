import logging

from ..objects.games import BoardGame
from ..exceptions import BGGApiError
from ..utils import xml_subelement_attr_list, xml_subelement_text, xml_subelement_attr, get_board_game_version_from_element


log = logging.getLogger("boardgamegeek.loaders.game")


def parse_language_dependence_poll(poll, data):
    """
    Parses a xml <poll name="language_dependece" /> node and store information in data

    :param poll: xml 'poll' node
    :param data: dictionary containing the data
    :return:
    """
    data["language_dependence"] = {}
    # TODO: do something with the total_votes too
    data["language_dependence"]["total_votes"] = poll.attrib.get("totalvotes", 0)
    data["language_dependence"]["results"] = {}

    results = poll.find("results")
    if not results:
        return

    d = {}

    for res in results.findall("result"):
        level = int(res.attrib["level"])
        numvotes = int(res.attrib.get("numvotes", 0))
        d[level] = {"description": res.attrib["value"], "num_votes": numvotes}

    data["language_dependence"]["results"] = d


def parse_suggested_numplayers_poll(poll, data):
    """
    Parses a xml <poll name="suggested_numplayers" /> node and store information in data

    :param poll: xml 'poll' node
    :param data: dictionary containing the data
    :return:
    """
    data["suggested_numplayers"] = {}
    # TODO: do something with the total_votes too
    data["suggested_numplayers"]["total_votes"] = poll.attrib.get("totalvotes", 0)
    data["suggested_numplayers"]["results"] = {}

    for result in poll.findall("results"):
        player_count = result.attrib.get("numplayers", "1")

        d = {"best": -1, "recommended": -1, "not_recommended": -1}

        for res in result.findall("result"):

            value = res.attrib.get("value")

            if value == "Best":
                d["best"] = int(res.attrib.get("numvotes", 0))
            elif value == "Recommended":
                d["recommended"] = int(res.attrib.get("numvotes", 0))
            elif value == "Not Recommended":
                d["not_recommended"] = int(res.attrib.get("numvotes", 0))
            else:
                log.warn('unexpected <result value="{}">'.format(value))

        data["suggested_numplayers"]["results"][player_count] = d


def parse_suggested_playerage_poll(poll, data):
    """
    Parses a xml <poll name="suggested_playerage" /> node and store information in data

    :param poll: xml 'poll' node
    :param data: dictionary containing the data
    :return:
    """

    data["suggested_playerage"] = {}
    data["suggested_playerage"]["total_votes"] = poll.attrib.get("totalvotes", 0)
    data["suggested_playerage"]["results"] = {}

    results = poll.find("results")

    if not results:
        return

    for res in results.findall("result"):
        player_age = res.attrib.get("value", "?")
        data["suggested_playerage"]["results"][player_age] = int(res.attrib.get("numvotes", 0))


def create_game_from_xml(xml_root, game_id, html_parser):

    game_type = xml_root.attrib["type"]
    if game_type not in ["boardgame", "boardgameexpansion"]:
        log.debug("unsupported type {} for item id {}".format(game_type, game_id))
        raise BGGApiError("item has an unsupported type")

    data = {"id": game_id,
            "name": xml_subelement_attr(xml_root, "name[@type='primary']"),
            "alternative_names": xml_subelement_attr_list(xml_root, "name[@type='alternate']"),
            "thumbnail": xml_subelement_text(xml_root, "thumbnail"),
            "image": xml_subelement_text(xml_root, "image"),
            "expansion": game_type == "boardgameexpansion",       # is this game an expansion?
            "families": xml_subelement_attr_list(xml_root, "link[@type='boardgamefamily']"),
            "categories": xml_subelement_attr_list(xml_root, "link[@type='boardgamecategory']"),
            "implementations": xml_subelement_attr_list(xml_root, "link[@type='boardgameimplementation']"),
            "mechanics": xml_subelement_attr_list(xml_root, "link[@type='boardgamemechanic']"),
            "designers": xml_subelement_attr_list(xml_root, "link[@type='boardgamedesigner']"),
            "artists": xml_subelement_attr_list(xml_root, "link[@type='boardgameartist']"),
            "publishers": xml_subelement_attr_list(xml_root, "link[@type='boardgamepublisher']"),
            "description": xml_subelement_text(xml_root, "description", convert=html_parser.unescape, quiet=True)}

    expands = []        # list of items this game expands
    expansions = []     # list of expansions this game has
    for e in xml_root.findall("link[@type='boardgameexpansion']"):
        try:
            item = {"id": e.attrib["id"], "name": e.attrib["value"]}
        except KeyError:
            raise BGGApiError("malformed XML element ('link type=boardgameexpansion')")

        if e.attrib.get("inbound", "false").lower()[0] == 't':
            # this is an item expanded by game_id
            expands.append(item)
        else:
            expansions.append(item)

    data["expansions"] = expansions
    data["expands"] = expands

    # These XML elements have a numberic value, attempt to convert them to integers
    for i in ["yearpublished", "minplayers", "maxplayers", "playingtime", "minplaytime", "maxplaytime", "minage"]:
        data[i] = xml_subelement_attr(xml_root, i, convert=int, quiet=True)

    # Look for the videos
    # TODO: The BGG API doesn't take the page=NNN parameter into account for videos; when it will, paginate them too
    videos = xml_root.find("videos")
    if videos is not None:
        vid_list = []
        for vid in videos.findall("video"):
            try:
                vd = {"id": vid.attrib["id"],
                      "name": vid.attrib["title"],
                      "category": vid.attrib.get("category"),
                      "language": vid.attrib.get("language"),
                      "link": vid.attrib["link"],
                      "uploader": vid.attrib.get("username"),
                      "uploader_id": vid.attrib.get("userid"),
                      "post_date": vid.attrib.get("postdate")
                      }
                vid_list.append(vd)
            except KeyError:
                raise BGGApiError("malformed XML element ('video')")

        data["videos"] = vid_list

    # look for the versions
    versions = xml_root.find("versions")
    if versions is not None:
        ver_list = []

        for version in versions.findall("item[@type='boardgameversion']"):
            try:
                vd = get_board_game_version_from_element(version)
                ver_list.append(vd)
            except KeyError:
                raise BGGApiError("malformed XML element ('versions')")

        data["versions"] = ver_list

    # look for the statistics
    stats = xml_root.find("statistics/ratings")
    if stats is not None:
        sd = {
            "usersrated": xml_subelement_attr(stats, "usersrated", convert=int, quiet=True),
            "average": xml_subelement_attr(stats, "average", convert=float, quiet=True),
            "bayesaverage": xml_subelement_attr(stats, "bayesaverage", convert=float, quiet=True),
            "stddev": xml_subelement_attr(stats, "stddev", convert=float, quiet=True),
            "median": xml_subelement_attr(stats, "median", convert=float, quiet=True),
            "owned": xml_subelement_attr(stats, "owned", convert=int, quiet=True),
            "trading": xml_subelement_attr(stats, "trading", convert=int, quiet=True),
            "wanting": xml_subelement_attr(stats, "wanting", convert=int, quiet=True),
            "wishing": xml_subelement_attr(stats, "wishing", convert=int, quiet=True),
            "numcomments": xml_subelement_attr(stats, "numcomments", convert=int, quiet=True),
            "numweights": xml_subelement_attr(stats, "numweights", convert=int, quiet=True),
            "averageweight": xml_subelement_attr(stats, "averageweight", convert=float, quiet=True),
            "ranks": []
        }

        ranks = stats.findall("ranks/rank")
        for rank in ranks:
            try:
                rank_value = int(rank.attrib.get("value"))
            except:
                rank_value = None
            sd["ranks"].append({"id": rank.attrib["id"],
                                "name": rank.attrib["name"],
                                "type": rank.attrib["type"],
                                "friendlyname": rank.attrib.get("friendlyname"),
                                "value": rank_value})

        data["stats"] = sd

        # Parse polls
        for poll in xml_root.findall("poll"):
            poll_name = poll.attrib.get("name")
            if poll_name == "suggested_numplayers":
                parse_suggested_numplayers_poll(poll, data)
            elif poll_name == "suggested_playerage":
                parse_suggested_playerage_poll(poll, data)
            elif poll_name == "language_dependence":
                parse_language_dependence_poll(poll, data)

    return BoardGame(data)


def add_game_comments_from_xml(game, xml_root):

    added_items = False
    total_comments = 0

    # TODO: this is not working (API PROBLEM??)
    comments = xml_root.find("comments")
    if comments is not None:
        total_comments = int(comments.attrib["totalitems"])

        for comm in xml_root.findall("comments/comment"):
            comment = {
                "username": comm.attrib["username"],
                "rating": comm.attrib.get("rating", "n/a").lower(),
                "comment": comm.attrib.get("value", "n/a")
            }
            added_items = True
            game.add_comment(comment)

    return added_items, total_comments
