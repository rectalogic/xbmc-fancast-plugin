import sys
import urllib
import xbmcplugin, xbmcgui
import xmlhelper as xml
import time

def Main(params):
    EpisodeList(**params)

class EpisodeList:
    def __init__(self, title, episodeFeedUrl, filter=None):
        try:
            if (not filter):
                self.manageFavorites(title, episodeFeedUrl)
            rssXml = xml.loadXml(episodeFeedUrl)    
            ok = self.parseRss(rssXml, filter)
        except:
            ok = False
            print "ERROR: %s::%s (%d) - %s" % (self.__class__.__name__, sys.exc_info()[2].tb_frame.f_code.co_name, sys.exc_info()[2].tb_lineno, sys.exc_info()[1])
        xbmcplugin.endOfDirectory(int(sys.argv[1]), succeeded=ok)
        
    def manageFavorites(self, title, feedUrl):
        item = xbmcgui.ListItem("Manage Favorites...", iconImage="DefaultFolder.png",
                                thumbnailImage="DefaultVideo.png")
        url = sys.argv[0] + "?" + urllib.urlencode({'module': 'favorites',
                                                    'title': title,
                                                    'feedUrl': feedUrl})
        return xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=url,
                                           listitem=item, isFolder=True)

    def parseRss(self, doc, filter):
        """Parse RSS XML dom and populate display list."""
        if (filter == 'movies'):
            filterNS = 'http://search.yahoo.com/mrss/'
            filterName = 'category'
            filterValue = 'movies'

        try:
            mediaNS = 'http://search.yahoo.com/mrss/'
            cimNS = 'http://labs.comcast.net/'
            root = xml.validateDocument(doc, 'rss')
            items = root.getElementsByTagName('item')
            totalItems = len(items)
            for item in items:
                try:
                    # Skip element if filter supplied and element value does not match
                    if (filter):
                        tagValue = xml.getChildData(item, filterNS, filterName)
                        if (filterValue != tagValue):
                            next

                    title = (xml.getChildData(item, mediaNS, 'title')).encode("utf-8")
                    thumbnail = xml.getChildData(item, mediaNS, 'thumbnail', 'url')
                    pubDate = xml.getChildData(item, cimNS, 'origAirDate', isRequired=False)
                    if (not pubDate):
                        pubDate = xml.getChildData(item, None, 'pubDate', isRequired=False)
                    if (pubDate):
                        try:
                            # convert date to DD-MM-YYYY so sorting by date works correctly.
                            # I found this date format in the Apple Movie Trailers II plugin
                            sdate = time.strptime(pubDate[5:16], "%d %b %Y")
                            pubDate = "%02d-%02d-%04d" % (sdate.tm_mday, sdate.tm_mon, sdate.tm_year)
                        except:
                            pass
                    description = xml.getChildData(item, None, 'description', isRequired=False)
                    url = sys.argv[0] + "?" + urllib.urlencode({ 'module': 'episodeplayer',
                                                                 'videoId': xml.getChildData(item, cimNS, 'videoId'),
                                                                 'title': title})
                    item = xbmcgui.ListItem(title, iconImage="DefaultVideo.png", thumbnailImage=thumbnail)
                    item.setInfo(type="Video",
                                 infoLabels={ "Title": title,
                                              "Plot": description,
                                              "Date": pubDate })
                    if not xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=url,
                                                       listitem=item, totalItems=totalItems):
                        return False
                except:
                    print "Skipping '%s' - %s" % (title.encode('utf-8'), sys.exc_info()[1])
        finally:
            if (doc): doc.unlink()
        return True
