'''
Sharerepo urlresolver plugin
Copyright (C) 2013 Vinnydude

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program. If not, see <http://www.gnu.org/licenses/>.
'''

from t0mm0.common.net import Net
from urlresolver.plugnplay.interfaces import UrlResolver
from urlresolver.plugnplay.interfaces import PluginSettings
from urlresolver.plugnplay import Plugin
import re, xbmcgui
from urlresolver import common
from lib import jsunpack

net = Net()

class SharerepoResolver(Plugin, UrlResolver, PluginSettings):
    implements = [UrlResolver, PluginSettings]
    name = "sharerepo"


    def __init__(self):
        p = self.get_setting('priority') or 100
        self.priority = int(p)
        self.net = Net()


    def get_media_url(self, host, media_id):
        try:
            url = self.get_url(host, media_id)
            html = self.net.http_GET(url).content
            dialog = xbmcgui.DialogProgress()
            dialog.create('Resolving', 'Resolving Sharerepo Link...')       
            dialog.update(0)

            data = {}
            r = re.findall(r'type="(?:hidden|submit)?" name="(.+?)"\s* value="?(.+?)">', html)
            for name, value in r:
                data[name] = value
                
            html = net.http_POST(url, data).content
    
            dialog.update(50)
    
            sPattern = '''<div id="player_code">.*?<script type='text/javascript'>(eval.+?)</script>'''
            r = re.search(sPattern, html, re.DOTALL + re.IGNORECASE)
            
            if r:
                sJavascript = r.group(1)
                sUnpacked = jsunpack.unpack(sJavascript)
                sPattern  = '''("video/divx"src="|addVariable\('file',')(.+?)video[.]'''
                r = re.search(sPattern, sUnpacked)              
                if r:
                    link = r.group(2) + fname
                    dialog.close()
                    return link
    
            if not link:
                raise Exception("Unable to resolve Sharerepo")

        except Exception, e:
            common.addon.log('**** Sharerepo Error occured: %s' % e)
            common.addon.show_small_popup('Error', str(e), 5000, '')
            return False
            
    def get_url(self, host, media_id):
        return 'http://sharerepo.com/%s' % media_id 
        

    def get_host_and_id(self, url):
        r = re.search('//(.+?)/([0-9a-zA-Z]+)',url)
        if r:
            return r.groups()
        else:
            return False
        return('host', 'media_id')


    def valid_url(self, url, host):
        if self.get_setting('enabled') == 'false': return False
        return (re.match('http://(www.)?sharerepo.com/' +
                         '[0-9A-Za-z]+', url) or
                         'sharerepo' in host)
