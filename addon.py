#!/usr/bin/python
# -*- coding: utf-8 -*-
#
#     Copyright (C) 2013-2015 mr.olix@gmail.com, boris.todorov#gmail.com & contributors
#      
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program. If not, see <http://www.gnu.org/licenses/>.
#
#    I'm a starter on XBMC and Python and I have to thank you all the people 
#    who post examples and code on the internet. 
#    Many thanks goes to Tristan Fischer who wrote the myvideo.de XBMC plugin
#    I started my the plugin code based on his code.
# 

#imports
from xbmcswift import Plugin, xbmc, xbmcplugin, xbmcgui, clean_dict
import sys
#import from 
import resources.lib.mytvbg as mytvbg

DEBUG = False
REMOTE_DBG = False

print 'Start mytvbg plugin'

# append pydev remote debugger
if REMOTE_DBG:
    # Make pydev debugger works for auto reload.
    # Note pydevd module need to be copied in XBMC\system\python\Lib\pysrc
    try:
        import pysrc.pydevd as pydevd
    # stdoutToServer and stderrToServer redirect stdout and stderr to eclipse console
        pydevd.settrace('localhost', stdoutToServer=True, stderrToServer=True)
    except ImportError:
        sys.stderr.write("Error: " +
            "You must add org.python.pydev.debug.pysrc to your PYTHONPATH.")
        sys.exit(1)

__addon_name__ = 'MyTV.BG'
__id__ = 'plugin.video.mytvbg'

username = ""
password = ""
   
thisPlugin = int(sys.argv[1])

THUMBNAIL_VIEW_IDS = {'skin.confluence': 500,
                      'skin.aeon.nox': 551,
                      'skin.confluence-vertical': 500,
                      'skin.jx720': 52,
                      'skin.pm3-hd': 53,
                      'skin.rapier': 50,
                      'skin.simplicity': 500,
                      'skin.slik': 53,
                      'skin.touched': 500,
                      'skin.transparency': 53,
                      'skin.xeebo': 55}


class Plugin_mod(Plugin):

    def add_items(self, iterable, is_update=False, sort_method_ids=[],
                  override_view_mode=False):
        items = []
        urls = []
        for i, li_info in enumerate(iterable):
            items.append(self._make_listitem(**li_info))
            if self._mode in ['crawl', 'interactive', 'test']:
                print '[%d] %s%s%s (%s)' % (i + 1, '', li_info.get('label'),
                                            '', li_info.get('url'))
                urls.append(li_info.get('url'))
        if self._mode is 'xbmc':
            if override_view_mode:
                skin = xbmc.getSkinDir()
                thumbnail_view = THUMBNAIL_VIEW_IDS.get(skin)
                if thumbnail_view:
                    cmd = 'Container.SetViewMode(%s)' % thumbnail_view
                    xbmc.executebuiltin(cmd)
            xbmcplugin.addDirectoryItems(self.handle, items, len(items))
            for id in sort_method_ids:
                xbmcplugin.addSortMethod(self.handle, id)
            xbmcplugin.endOfDirectory(self.handle, updateListing=is_update)
        return urls

    def _make_listitem(self, label, label2='', iconImage='', thumbnail='',
                       path='', **options):
        li = xbmcgui.ListItem(label, label2=label2, iconImage=iconImage,
                              thumbnailImage=thumbnail, path=path)
        cleaned_info = clean_dict(options.get('info'))
        if cleaned_info:
            li.setInfo('video', cleaned_info)
        if options.get('is_playable'):
            li.setProperty('IsPlayable', 'true')
        if options.get('context_menu'):
            li.addContextMenuItems(options['context_menu'])
        return options['url'], li, options.get('is_folder', True)

plugin = Plugin_mod(__addon_name__, __id__, __file__)

'''
default method route to /
called when the script starts 
'''
@plugin.route('/', default=True)
def main_menu():
    __log('main_menu start')
        
    items=[]
    items.append({'label': u'Телевизии - на живо, високо качество',
                  'url': plugin.url_for('tvList',id_type='live_direct')})    
    items.append({'label': u'Телевизии - избор на качество и време',
                  'url': plugin.url_for('tvList',id_type='live')})
    items.append({'label': u'Сериали',
                  'url': plugin.url_for('tvList',id_type='series')})
   
    __log('main_menu finished')
    return plugin.add_items(items)

#    creates main level menu list on selected id_type=(live|series)
@plugin.route('/tvList/<id_type>')
def tvList(id_type):
    __log('tvlist start')
    
    menulist=[]
    items=[]
    if id_type =='live':  #get a list with the TV stations
        menulist=mytvbg.showTVStations(plugin.get_setting('username'), plugin.get_setting('password'))        
        if menulist:         
            for item in menulist:
                items.append({'label': item[0],
                              'url':   plugin.url_for('tvListResolution',ch_url=item[1]) })
    if id_type =='live_direct':  #get a list with the directly accessible TV stations
        menulist=mytvbg.showTVStations(plugin.get_setting('username'), plugin.get_setting('password'))        
        if menulist:         
            for item in menulist:
                items.append({'label': item[0],
                              'url':   plugin.url_for('directtvstation_playtv', ch_url=item[1]) }) 
    if id_type =='series':#get a list with TV serials
        menulist=mytvbg.showTVSerials(plugin.get_setting('username'), plugin.get_setting('password'))        
        if menulist:         
            for item in menulist:
                items.append({'label': item[0],
                              'url':   plugin.url_for('tvListSerialSeasons',ser_url=item[1]) })                     
    if not menulist:
            items.append({'label': 'Грешка - не са намерени елементи',
                          'url': 'error'})                
    __log('tvlist finished')
    return plugin.add_items(items)


#  creates second level menu LiveTV - list of resolutions for specific chanel
@plugin.route('/tvListResolution/<ch_url>')
def tvListResolution(ch_url):
    __log('tvListResolution start')
    #get a list with the TV stations
    menulist=[]
    items=[]

    menulist=mytvbg.showTVResolutions(plugin.get_setting('username'), plugin.get_setting('password'), ch_url)        
    if menulist:         
         for item in menulist:
                #tvstation_params = ch_url + '?&offset=0&q=' + item[1]
                items.append({'label': item[0],
                              'url':   plugin.url_for('tvstation_playtv', tvstation_params=item[1]) } )       
                  
    else:
         items.append({'label': 'Грешка - не са намерени елементи',
                       'url': 'error'})                
    __log('tvListResolution finished')
    return plugin.add_items(items)

#  creates second level menu for recordered TV series - list all season for specified serial
@plugin.route('/tvListSerialSeasons/<ser_url>')
def tvListSerialSeasons(ser_url):
    __log('tvListSerialSeasons start')
    #get a list with the TV stations
    menulist=[]
    items=[]

    menulist=mytvbg.showTVSerialSeasons(plugin.get_setting('username'), plugin.get_setting('password'), ser_url)        
    if menulist:         
         for item in menulist:
                items.append({'label': item[0],
                              'url':   plugin.url_for('tvListSeasonEpisodes', ses_url=item[1]) } )       
                  
    else:
         items.append({'label': 'Грешка - не са намерени елементи',
                       'url': 'error'})                
    __log('tvListSerialSeasons finished')
    return plugin.add_items(items)


    
#  creates third level menu for recordered TV series - list all episodes  for specified season
@plugin.route('/tvListSeasonEpisodes/<ses_url>')
def tvListSeasonEpisodes(ses_url):
    __log('tvListSeasonEpisodes start  ')
    #get a list with the TV stations
    menulist=[]
    items=[]

    menulist=mytvbg.showTVSeasonEpisodes(plugin.get_setting('username'), plugin.get_setting('password'), ses_url)        
    if menulist:         
         for item in menulist:
                #tvstation_params = ch_url + '?&offset=0&q=' + item[1]
                items.append({'label': item[0],
                              'url':   plugin.url_for('tvSeriePlayEpisode', episode_params=item[1]) } )  
                __log('tvListSeasonEpisodes start  '+item[1])     
                  
    else:
         items.append({'label': 'Грешка - не са намерени елементи',
                       'url': 'error'})                
    __log('tvListSeasonEpisodes finished')
    return plugin.add_items(items)

    

#    plays the select live TV
@plugin.route('/tvstation_playtv/<tvstation_params>')
def tvstation_playtv(tvstation_params):
    
    __log('tvstation_playtv started with string=%s' % tvstation_params)
           
    mytvbg.playLiveStream(plugin.get_setting('username'), plugin.get_setting('password'),tvstation_params) 

#    plays directly the select live TV
@plugin.route('/directtvstation_playtv/<ch_url>')
def directtvstation_playtv(ch_url):
    
    __log('directtvstation_playtv started with string=%s' % ch_url)
           
    mytvbg.playDirectLiveStream(plugin.get_setting('username'), plugin.get_setting('password'),ch_url)   

#    plays the select episode from series library
@plugin.route('/tvSeriePlayEpisode/<episode_params>')
def tvSeriePlayEpisode(episode_params):
    
    __log('tvSeriePlayEpisode started with string=%s' % episode_params)
           
    mytvbg.playEpisodeStream(plugin.get_setting('username'), plugin.get_setting('password'),episode_params)    



def __add_items(entries):
    items = []
    sort_methods = [xbmcplugin.SORT_METHOD_UNSORTED, ]
    force_viewmode = plugin.get_setting('force_viewmode') == 'true'
    update_on_pageswitch = plugin.get_setting('update_on_pageswitch') == 'true'
    has_icons = False
    is_update = False
    for e in entries:
        if force_viewmode and not has_icons and e.get('thumb', False):
            has_icons = True
        if e.get('pagenination', False):
            if e['pagenination'] == 'PREV':
                if update_on_pageswitch:
                    is_update = True
                title = '<< %s %s <<' % (plugin.get_string(30000), e['title'])
            elif e['pagenination'] == 'NEXT':
                title = '>> %s %s >>' % (plugin.get_string(30000), e['title'])
            items.append({'label': title,
                          'iconImage': 'DefaultFolder.png',
                          'is_folder': True,
                          'is_playable': False,
                          'url': plugin.url_for('show_path',
                                                path=e['path'])})
        elif e['is_folder']:
            items.append({'label': e['title'],
                          'iconImage': e.get('thumb', 'DefaultFolder.png'),
                          'is_folder': True,
                          'is_playable': False,
                          'url': plugin.url_for('show_path',
                                                path=e['path'])})
        else:
            items.append({'label': e['title'],
                          'iconImage': e.get('thumb', 'DefaultVideo.png'),
                          'info': {'duration': e.get('length', '0:00'),
                                   'plot': e.get('description', ''),
                                   'studio': e.get('username', ''),
                                   'date': e.get('date'),
                                   'year': e.get('year'),
                                   'rating': e.get('rating'),
                                   'votes': e.get('votes'),
                                   'views': e.get('views')},
                          'is_folder': False,
                          'is_playable': True,
                          'url':e['url']})
                        
                        #'url': plugin.url_for('watch_video',
                        #                       video_id=e['video_id'])})
                                                
                                
    sort_methods.extend((xbmcplugin.SORT_METHOD_VIDEO_RATING,
                         xbmcplugin.SORT_METHOD_VIDEO_RUNTIME,))
    __log('__add_items end')
    return plugin.add_items(items, is_update=is_update,
                            sort_method_ids=sort_methods,
                            override_view_mode=has_icons)

'''
    log method
'''
def __log(text):
    xbmc.log('%s addon: %s' % (__addon_name__, text))


if __name__ == '__main__':
    plugin.run()
