import sys
import os
import urllib
import xmlhelper as xml
import xbmc, xbmcplugin, xbmcgui
from episodelist import EpisodeList

FAVORITES_DIR = xbmc.translatePath(os.path.join(R"P:\plugin_data", "video", sys.modules["__main__"].__plugin__))
FAVORITES_PATH = os.path.join(FAVORITES_DIR, "favorites.xml")

def Main(params):
    Favorites(**params)

class Favorite:
    def __init__(self, title, feedUrl):
        self.title = title
        self.feedUrl = feedUrl

class Favorites:
    def __init__(self, title, feedUrl, action=None):
        self.loadFavorites()
        if (action == 'add'):
            self.addFavorite(title, feedUrl)
            self.saveFavorites()
            EpisodeList(title, feedUrl)
        elif (action == 'remove'):
            self.removeFavorite(feedUrl)
            self.saveFavorites()
            EpisodeList(title, feedUrl)
        else:
            # Render add/remove links depending if feed is already a favorite or not
            if (self.indexOfFavorite(feedUrl) >= 0):
                action = 'remove'
                label = 'Remove from'
            else:
                action = 'add'
                label = 'Add to'

            item = xbmcgui.ListItem("%s Favorites" %  label, iconImage="DefaultVideo.png")
            url = sys.argv[0] + "?" + urllib.urlencode({'module': 'favorites',
                                                        'action': action,
                                                        'title': title,
                                                        'feedUrl': feedUrl})
            ok = xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=url,
                                             listitem=item, isFolder=True)
            xbmcplugin.endOfDirectory(int(sys.argv[1]), succeeded=ok)

    def indexOfFavorite(self, feedUrl):
        index = 0
        for f in self.favorites:
            if (f.feedUrl == feedUrl):
                return index
            index += 1
        return -1

    def addFavorite(self, title, feedUrl):
        self.favorites.append(Favorite(title, feedUrl))

    def removeFavorite(self, feedUrl):
        index = self.indexOfFavorite(feedUrl)
        if (index >= 0):
            del self.favorites[index]

    def loadFavorites(self):
        self.favorites = []
        try:
            doc = None
            doc = xml.loadXml(FAVORITES_PATH)
            root = xml.validateDocument(doc, 'rss')
            items = root.getElementsByTagName('item')
            for item in items:
                self.favorites.append(Favorite(xml.getChildData(item, None, 'title'),
                                               xml.getChildData(item, None, 'link')))
        except:
            print "ERROR: %s::%s (%d) - %s" % (self.__class__.__name__, sys.exc_info()[2].tb_frame.f_code.co_name, sys.exc_info()[2].tb_lineno, sys.exc_info()[1])
        if (doc): doc.unlink()

    def saveFavorites(self):
        if (not os.path.isdir(FAVORITES_DIR)):
            os.makedirs(FAVORITES_DIR)
        doc = xml.createDocument()
        root = xml.appendChild(doc, doc, "rss")
        root = xml.appendChild(doc, root, "channel")
        for f in self.favorites:
            item = xml.appendChild(doc, root, "item")
            xml.appendChild(doc, item, "title", f.title)
            xml.appendChild(doc, item, "link", f.feedUrl)
        xml.writeXml(doc, FAVORITES_PATH)
