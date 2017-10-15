# coding: utf-8

"""
:mod:`boardgamegeek.hotitems` - BoardGameGeek "Hot Items"
=========================================================

.. module:: boardgamegeek.hotitems
   :platform: Unix, Windows
   :synopsis: classes for handling hot items information

.. moduleauthor:: Cosmin Luță <q4break@gmail.com>
"""
from __future__ import unicode_literals

from copy import copy

from .things import Thing
from ..exceptions import BGGError
from ..utils import DictObject, fix_url


class HotItem(Thing):
    """
    A hot item from a list. Can refer to either an item (``boardgame``, ``videogame``, etc.), a person (``rpgperson``,
    ``boardgameperson``) or even a company (``boardgamecompany``, ``videogamecompany``), depending on the type of hot
    list retrieved.
    """

    def __init__(self, data):
        if "rank" not in data:
            raise BGGError("missing rank of HotItem")

        if "thumbnail" in data:
            data["thumbnail"] = fix_url(data["thumbnail"])

        super(HotItem, self).__init__(data)

    def __repr__(self):
        return "HotItem (id: {})".format(self.id)

    def _format(self, log):
        log.info("hot item id        : {}".format(self.id))
        log.info("hot item name      : {}".format(self.name))
        log.info("hot item rank      : {}".format(self.rank))
        log.info("hot item published : {}".format(self.year))
        log.info("hot item thumbnail : {}".format(self.thumbnail))

    @property
    def rank(self):
        """
        :return: Ranking of this hot item
        :rtype: integer
        """
        return self._data["rank"]

    @property
    def year(self):
        """
        :return: publishing year
        :rtype: integer
        :return: ``None`` if n/a
        """
        return self._data.get("yearpublished")

    @property
    def thumbnail(self):
        """
        :return: thumbnail URL
        :rtype: str
        :return: ``None`` if n/a
        """
        return self._data.get("thumbnail")


class HotItems(DictObject):
    """
    A collection of :py:class:`boardgamegeek.hotitems.HotItem`
    """
    def __init__(self, data):
        kw = copy(data)
        if "items" not in kw:
            kw["items"] = []

        self._items = []
        for data in kw["items"]:
            self._items.append(HotItem(data))

        super(HotItems, self).__init__(kw)

    def add_hot_item(self, data):
        """
        Add a new hot item to the container

        :param data: dictionary containing the data
        """
        self._data["items"].append(data)
        self._items.append(HotItem(data))

    @property
    def items(self):
        """
        :return: list of hotitems
        :rtype: list of :py:class:`boardgamegeek.hotitems.HotItem`
        """
        return self._items

    def __len__(self):
        return len(self._items)

    def __iter__(self):
        for item in self._data["items"]:
            yield HotItem(item)

    def __getitem__(self, item):
        return self._items.__getitem__(item)
