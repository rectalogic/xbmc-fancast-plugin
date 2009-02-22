import sys
import re
import urllib
import xmlhelper as xml
import xbmc, xbmcplugin, xbmcgui

def Main(params):
    EpisodePlayer(params['videoId'], params['title'])

class EpisodePlayer:
    def __init__(self, videoId, title):
        videoUrl = self.getVideoUrl(videoId)
        item = xbmcgui.ListItem(title)
        item.setProperty("SWFPlayer", "http://www.hulu.com/player.swf")
        # play won't accept unicode strings, so convert
        xbmc.Player(xbmc.PLAYER_CORE_DVDPLAYER).play(str(videoUrl), item)

    def getVideoUrl(self, videoId):
        """Get video URL for videoId"""
        try:
            doc = xml.loadXml("http://www.fancast.com/player.widget?videoId=%s" % videoId)
            root = xml.validateDocument(doc, 'entity')
            mediaUrl = xml.getChildData(root, None, 'mediaUrl')
            doc.unlink()

            doc = xml.loadXml(mediaUrl)
            root = xml.validateDocument(doc, 'playlist')
            # We may have multiple urls in playlist, look for rtmp
            # This may pick the wrong video
            urls = root.getElementsByTagName('url')
            for url in urls:
                rtmpUrl = url.firstChild.wholeText
                if (rtmpUrl.startswith("rtmp:")):
                    break

            huluBreak = rtmpUrl.find('<break>')
            if (huluBreak >= 0):
                # Hulu style rtmp URL
                return rtmpUrl[0:huluBreak]
            else:
                # Fancast style rtmp URL
                # Need to split application and filename out of rtmp url:
                #   rtmp://cp40359.edgefcs.net/ondemand/fancast/Comcast_CIM_Prod_Fancast_Partner/836/252/COMEDYCENTRAL_COLBERTREPORT_4125.flv
                # Changes to:
                #   rtmp://cp40359.edgefcs.net/ondemand?slist=fancast/Comcast_CIM_Prod_Fancast_Partner/836/252/COMEDYCENTRAL_COLBERTREPORT_4125
                match = re.compile('^(.*ondemand)/(.*).flv$').match(rtmpUrl)
                return "%s?slist=%s" % (match.group(1), match.group(2))
        finally:
            if (doc): doc.unlink()