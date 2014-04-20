#!/usr/bin/env python

# Note: python 2.7
import urllib2
import xml.etree.ElementTree as ET
import logging

from libBGG.Boardgame import Boardgame
from libBGG.Guild import Guild

log = logging.getLogger(__name__)

class BGGAPI(object):

    def __init__(self):
        self.root_url = 'http://www.boardgamegeek.com/xmlapi2/'

    def _get_tree_by_id(self, bgg_id):
        url = '%sthing?id=%s' % (self.root_url, bgg_id)
        return ET.parse(urllib2.urlopen(url))

    def fetch_boardgame(self, name, bgid=None):
        '''Fetch information about a bardgame from BGG by name. If bgid is given,
        it will be used instead. bgid is the ID of the game at BGG. bgid should be type str.'''
        if bgid is None:
            log.info('fetching boardgame by name "%s"' % name)
            url = '%ssearch?query=%s&exact=1' % (self.root_url,
                                                  urllib2.quote(name))
            tree = ET.parse(urllib2.urlopen(url))
            game = tree.find("./*[@type='boardgame']")
            if game is None:
                log.warn('game not found: %s' % name)
                return None

            bgid = game.attrib['id'] if 'id' in game.attrib else None
            if not bgid:
                log.warning('BGGAPI gave us a game without an id: %s' % name)
                return None

        log.info('fetching boardgame by BGG ID "%s"' % bgid)
        tree = self._get_tree_by_id(bgid)
        root = tree.getroot()

        kwargs = dict()
        kwargs['bgid'] = bgid
        # entries that use attrib['value']. 
        value_map = {
            './/yearpublished': 'year',
            './/minplayers': 'minplayers',
            './/maxplayers': 'maxplayers',
            './/playingtime': 'playingtime',
            './/name': 'names',
            ".//link[@type='boardgamefamily']": 'families',
            ".//link[@type='boardgamecategory']": 'categories',
            ".//link[@type='boardgamemechanic']": 'mechanics',
            ".//link[@type='boardgamedesigner']": 'designers',
            ".//link[@type='boardgameartist']": 'artists',
            ".//link[@type='boardgamepublisher']": 'publishers',
            ".//link[@type='boardgamecategory']": 'categories',
        }
        for xpath, bg_arg in value_map.iteritems():
            els = root.findall(xpath)
            for el in els:
                if 'value' in el.attrib:
                    if bg_arg in kwargs:
                        # multiple entries, make this arg a list.
                        if type(kwargs[bg_arg]) != list:
                            kwargs[bg_arg] = [kwargs[bg_arg]]
                        kwargs[bg_arg].append(el.attrib['value'])
                    else:
                        kwargs[bg_arg] = el.attrib['value']
                else:
                    log.warn('no "value" found in %s for game %s' % (xpath, name))

        # entries that use text instead of attrib['value']
        value_map = {
            './thumbnail': 'thumbnail',
            './image': 'image',
            './description': 'description'
        }
        for xpath, bg_arg in value_map.iteritems():
            els = root.findall(xpath)
            if els:
                if len(els) > 0:
                    log.warn('Found multiple entries for %s, ignoring all but first' % xpath)
                kwargs[bg_arg] = els[0].text

        log.debug('creating boardgame with kwargs: %s' % kwargs)
        return Boardgame(**kwargs)

    def fetch_guild(self, gid):
        '''Fetch Guild information from BGG and populate a returned Guild object. There is
        currently no way to query BGG by guild name, it must be by ID.'''
        url = '%sguild?id=%s&members=1' % (self.root_url, gid)
        tree = ET.parse(urllib2.urlopen(url))
        root = tree.getroot()

        kwargs = dict()
        kwargs['name'] = root.attrib['name']
        kwargs['bggid'] = gid
        kwargs['members'] = list()

        el = root.find('.//members[@count]')
        count = int(el.attrib['count'])
        total_pages = 1+(count/25)   # 25 memebers per page according to BGGAPI
        if total_pages >= 10:
            log.warn('Need to fetch %d pages. It could take awhile.' % total_pages)
        for page in xrange(total_pages):
            url = '%sguild?id=%s&members=1&page=%d' % (self.root_url, gid, page+1)
            tree = ET.parse(urllib2.urlopen(url))
            root = tree.getroot()
            log.debug('fetched guild page %d of %d' % (page, total_pages))

            for el in root.findall('.//member'):
                kwargs['members'].append(el.attrib['name'])

            if page == 1:
                # grab initial info from first page
                for tag in ['description', 'category', 'website', 'manager']:
                    el = root.find(tag)
                    if not el is None:
                        kwargs[tag] = el.text
       
        return Guild(**kwargs)
