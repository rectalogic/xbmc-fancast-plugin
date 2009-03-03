import sys
import urllib
import xmlhelper as xml
import xbmcplugin, xbmcgui
import favorites

def Main(params):
    SeriesList(**params)

class SeriesList:
    def __init__(self, seriesFeedUrl=favorites.FAVORITES_PATH):
        # All movies
        url = sys.argv[0] + "?" + urllib.urlencode({'module': 'episodelist',
                                                    'title': 'All Movies',
                                                    'filter': 'movies',
                                                    'episodeFeedUrl': 'http://fb1.fancast.com/rss/allvideos.xml'})
        item = xbmcgui.ListItem("All Movies...", iconImage="DefaultFolder.png")
        ok = xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=url,
                                         listitem=item, isFolder=True)

        # Add initial item to display master "feed of feeds"
        url = sys.argv[0] + "?" + urllib.urlencode({'module': 'serieslist',
                                                    'seriesFeedUrl': 'http://fb1.fancast.com/rss/video-index.xml'})
        item = xbmcgui.ListItem("All Series...", iconImage="DefaultFolder.png")
        ok = xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=url,
                                         listitem=item, isFolder=True)

        try:
            # Add individual feeds
            rssXml = xml.loadXml(seriesFeedUrl)
            ok = self.parseRss(rssXml)
        except:
            print "No feeds found for %s" % seriesFeedUrl

        xbmcplugin.endOfDirectory(int(sys.argv[1]), succeeded=ok)

    def parseRss(self, doc):
        """Parse RSS XML dom and populate display list."""
        try:
            root = xml.validateDocument(doc, 'rss')
            items = root.getElementsByTagName('item')
            totalItems = len(items)
            for item in items:
                try:
                    title = (xml.getChildData(item, None, 'title')).encode("utf-8")
                    feedUrl = xml.getChildData(item, None, 'link')
                    url = sys.argv[0] + "?" + urllib.urlencode({'module': 'episodelist',
                                                                'title': title,
                                                                'episodeFeedUrl': feedUrl})
                    item = xbmcgui.ListItem(title, iconImage="DefaultFolder.png",
                                            thumbnailImage="DefaultVideo.png")
                    if not xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=url,
                                                       listitem=item, totalItems=totalItems, isFolder=True):
                        return False
                except:
                    print "Skipping '%s' - %s" % (title.encode('utf-8'), sys.exc_info()[1])
            return True
        finally:
            if (doc): doc.unlink()