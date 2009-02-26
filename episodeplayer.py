import sys
import re
import urllib
import xmlhelper as xml
import xbmc, xbmcplugin, xbmcgui

def Main(params):
    EpisodePlayer(params['videoId'], params['title'])

class EpisodePlayer:
    def __init__(self, videoId, title):
        self.getVideoUrl(videoId, title)

    def getVideoUrl(self, videoId, title):
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
                #code to determine proper streaming url from
                #http://code.google.com/p/xbmc-addons/source/browse/trunk/plugins/video/Hulu/resources/lib/stream_hulu.py#75
                rtmpUrl=rtmpUrl.replace('&amp;','&').replace('&lt;','<').replace('&gt;','>')
                mainParts = rtmpUrl.split("?")
                queryStringParts = mainParts[1].split("&")
                v9 = queryStringParts[0]
                v6 = queryStringParts[1]

                if "<break>" in queryStringParts[2]:
                    breakParts = queryStringParts[2].split("<break>")
                    v3 = breakParts[0];
                    fileName = breakParts[1]
                else:
                    v3 = queryStringParts[2]
                    breakFilenameURL = mainParts[0].split("://");
                    breakFilenamedir = breakFilenameURL[1].split("/");
                    breakFilenames = breakFilenameURL[1].split(breakFilenamedir[1] + "/")
                    fileName = breakFilenames[1]

                newQueryString = v9 + "&" + v6 + "&" + v3

                protocolSplit = rtmpUrl.split("://")
                pathSplit = protocolSplit[1].split("/");
                serverPath = pathSplit[0] + "/" + pathSplit[1];
                server = pathSplit[0];
                appName = pathSplit[1];
                videoIdentIp = server

                protocol = "rtmp";
                port = "1935";
                newUrl =  protocol + "://" + videoIdentIp + ":" + port + "/" + appName + "?_fcs_vhost=" + server
                if newQueryString <> "":
                    newUrl += "&" + newQueryString
                SWFPlayer = 'http://www.hulu.com/player.swf'
                item = xbmcgui.ListItem(title)
                item.setProperty("SWFPlayer", SWFPlayer)
                item.setProperty("PlayPath", fileName)
                item.setProperty("PageURL", "http://www.fancast.com/player.widget?videoId=%s" % videoId)
                playlist = xbmc.PlayList(1)
                playlist.clear()
                playlist.add(newUrl, item)
                play=xbmc.Player().play(playlist)
                xbmc.executebuiltin('XBMC.ActivateWindow(fullscreenvideo)')
            else:
                # Fancast style rtmp URL
                # Need to split application and filename out of rtmp url:
                #   rtmp://cp40359.edgefcs.net/ondemand/fancast/Comcast_CIM_Prod_Fancast_Partner/836/252/COMEDYCENTRAL_COLBERTREPORT_4125.flv
                # Changes to:
                #   rtmp://cp40359.edgefcs.net/ondemand?slist=fancast/Comcast_CIM_Prod_Fancast_Partner/836/252/COMEDYCENTRAL_COLBERTREPORT_4125
                match = re.compile('^(.*ondemand)/(.*).flv$').match(rtmpUrl)
                videoUrl = "%s?slist=%s" % (match.group(1), match.group(2))
                item = xbmcgui.ListItem(title)
                item.setProperty("SWFPlayer", "http://www.hulu.com/player.swf")
                # play won't accept unicode strings, so convert
                xbmc.Player(xbmc.PLAYER_CORE_DVDPLAYER).play(str(videoUrl), item)
        finally:
            if (doc): doc.unlink()
