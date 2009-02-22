"""
Plugin for streaming video from Fancast
"""

import sys
import cgi
import urllib
import xbmcplugin, xbmcgui


__plugin__ = "Fancast"
__credits__ = "Andrew Wason rectalogic@rectalogic.com"
__version__ = "1.1"

if (__name__ == "__main__"):
    if (sys.argv[2]):
        params = cgi.parse_qs(sys.argv[2][1:])
        for key, val in params.iteritems():
            params[key] = urllib.unquote_plus(params[key][0])
    else:
        params = { 'module': 'serieslist' }

    mod = __import__(params['module'], globals(), locals())
    del params['module']
    mod.Main(params)