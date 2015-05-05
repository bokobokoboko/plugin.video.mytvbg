#!/usr/bin/python
# -*- coding: utf-8 -*-
#
#     Copyright (C) 2013-2015 mr.olix@gmail.com boris.todorov#gmail.com & contributors
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

from xbmcswift import xbmc, xbmcaddon

import urllib2
import cookielib
import os.path
import xbmcgui
import sys
import urlparse
import time

# set debug to generate log entries
DEBUG = True

#libname
LIBNAME = 'mytvbg'

_addon = xbmcaddon.Addon()
_addon_path = _addon.getAddonInfo('path')
_tempdir = os.path.join(_addon_path, '..', '..', 'temp')



#class handles html get and post for mytv.bg website
class mytv:
        
    #static values
    CLASSNAME = 'mytv'
    PLUGINID  = 'plugin.video.mytvbg'
     
    COOKIEFILE = 'cookies.lwp' #file to store cookie information    
    USERAGENT  = {'User-agent' : 'Mozilla/4.0 (compatible; MSIE 5.5; Windows NT)'}
    
    MAINURL    = 'http://mytv.bg' #main url
    LOGINURL   = MAINURL +'/in' #login url
    TVLISTURL  = MAINURL +'/channels' # URL to get list of all TV live stations
    CONTENTURL = MAINURL +'/channels' # Base URL of stream content for live chanels 
    TVSERIES   = MAINURL +'/shows-bg' # Series Library URL
    TVSERIESTVS   = MAINURL +'/tv/program/genre/series/?r=title' # Series Library URL
    ISLOGGEDINSTR = 'За да гледате, моля, регистрирайте се или влезте с потребителското си име и парола' #string to check if user is logged in
    #globals variables
    __cj__ = None
    __cookiepath__ = None
    __isLoggedIn__ = None
    __username__ = None
    __password__ = None    


#method for logging
    def __log(self, text):
        debug = None
        if (debug == True):
            xbmc.log('%s class: %s' % (self.CLASSNAME, text))
        else:
            if(DEBUG == True):
                xbmc.log('%s class: %s' % (self.CLASSNAME, text))
            
#default constructor initialize all class variables here
#called every time the script runs
    def __init__(self, username, password):
        self.__log('start __init__')
        self.__username__ = username
        self.__password__ = password
        self.initCookie()
        self.openSite(self.MAINURL)        
        self.__log('finished __init__')
        
#init the cookie handle for the class
#it loads information from cookie file
    def initCookie(self):
        self.__log('start initCookie')
        addon = xbmcaddon.Addon(self.PLUGINID)
        cookiepath = xbmc.translatePath(addon.getAddonInfo('profile')) 
        cookiepath = cookiepath + self.COOKIEFILE
        cookiepath = xbmc.translatePath(cookiepath)
        #set global
        self.__cookiepath__ = cookiepath
        self.__log('Cookiepath: ' + cookiepath)
        cj = cookielib.LWPCookieJar()
        opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))
        urllib2.install_opener(opener)
        #if exist load file and cookie information 
        if (os.path.isfile(cookiepath)):
            cj.load(cookiepath, False, False)
            self.__log('Cookies loaded from file: ' + cookiepath)
            for index, cookie in enumerate(cj):
                self.__log('cookies come here: ')                
        else:               
            self.__log('No cookie file found at: ' + cookiepath)
        #set global object
        self.__cj__ = cj   
        self.__log('Finished initCookie')
        
#updates the cookie to cookie file
    def updateCookie(self):
        self.__log('Start updateCookie')
        self.__cj__.save(self.__cookiepath__)
        self.__log('Finished updateCookie')
        
#opens url and returns html stream 
#also checks if user is logged in
    def openSite(self, url):   
        self.__log('Start  openSite')
        urlopen = urllib2.urlopen
        request = urllib2.Request
        theurl = url
        txtdata = ''
        req = request(theurl, txtdata, self.USERAGENT)
        # create a request object
        handle = urlopen(req)
        htmlstr = handle.read()
        startpoint = htmlstr.find(self.ISLOGGEDINSTR)
        #if not logged in
        if (startpoint != -1):            
            #login
            self.logIn()
            #open page again
            handle = urlopen(req)
            htmlstr = handle.read()
            startpoint = htmlstr.find(self.ISLOGGEDINSTR)
            if (0 != -1):
              dialog = xbmcgui.Dialog()
              dialog.ok("Error", 'Грешно потребителско име или парола за MyTV.bg'  )
        try:
         self.updateCookie()
        except:
          dialog = xbmcgui.Dialog()
          dialog.ok("Error", 'Failed to update session coockie.\nLogin error! Check username/password for MyTV.bg'  )
        #self.__log('htmlstr: ' + htmlstr)
        self.__log('Finished openSite: ' + theurl)
        return htmlstr

#opens url and returns html stream 
    def openContentStream(self,url,issue_id):        
        self.__log('Start openContentStream' + url)
        urlopen = urllib2.urlopen
        request = urllib2.Request
        theurl = url
        txtdata = '' #issue_id
        self.__log('txtdata:_ ' + txtdata)
        req = request(theurl, txtdata, self.USERAGENT)
        # create a request object
        handle = urlopen(req)
        htmlstr = handle.read()
        startpoint = htmlstr.find(self.ISLOGGEDINSTR)
        #if not logged in
        if (startpoint != -1):            
            #login
            self.logIn()
            #open page again
            handle = urlopen(req)
            htmlstr = handle.read()
        self.updateCookie()
        self.__log('Finished ContenStream: ' + theurl)
        return htmlstr
    

#login into the MyTV.bg webpage
#returns true if login successful
    def logIn(self):
        self.__log('Start logIn')
        isLoggedIn = False
        urlopen = urllib2.urlopen
        request = urllib2.Request
        theurl = self.LOGINURL
        self.__log('----URL request started for: ' + theurl + ' ----- ')
        txdata = 'email=' + self.__username__ + '&pass=' + self.__password__ + '&rmb=1'
        req = request(self.LOGINURL, txdata, self.USERAGENT)
        self.__log('----URL requested: ' + theurl + ' txdata: ' + txdata)
        # create a request object
        handle = urlopen(req)     
        link = handle.read() 
        self.__log(link)
        self.__log('----URL request finished for: ' + theurl + ' ----- ')
        self.updateCookie()
        startpoint = link.find(self.ISLOGGEDINSTR)
        if (startpoint != -1):
            isLoggedIn = True
        self.__log('Finished logIn')        
        return isLoggedIn
        

#    return list with TV Serials from VOYO
    def getTVSerials(self, html):        
        self.__log('Start getTVSerials')
        text  = html
        text  = text.replace('\r','')
        lines = text.split('\n')
        text = ''
        for line in lines:
            if ( line.find('" class="article')!=-1 ):
                text = text  + line                 
            if ( line.find('<h2 itemprop="name">')!=-1 ):
                text = text  + line                 
        self.__log('Serials List Links: ' + text)
        links = text.split('<a')
        items = []
        if links:
            for lnk in links:
                if ( lnk.find('" class="article')!=-1 ):
                     urlStartPoint = lnk.find('href="') +6
                     urlEndPoint   = lnk.find('"' , urlStartPoint) 
                     nameStartPoint  = lnk.find('"name">' ,urlEndPoint) +7
                     nameEndPoint    = lnk.find('</h2>' , nameStartPoint) 
                     ser_url   = lnk[urlStartPoint:urlEndPoint]#.decode('unicode_escape','ignore').encode('utf-8')
                     ser_name    = lnk[nameStartPoint:nameEndPoint]#.decode('unicode_escape','ignore').encode('utf-8')

                     items.append((ser_name, ser_url ))
        
        if 0 == len(items):
            items.append(('Error no TV station items found', 'Error'))   

        self.__log('Finished getTVSerials')
        return items


#    return list with TV Serials from TVs
    def getTVSerialsTVs(self, html):        
        self.__log('Start getTVSerials-TVs +++++')
        items = []
        numPages = 0
        pgStartPos = html.find('title="Ultimul" class="ppage" rel="') +35
        if ( pgStartPos != -1 ):
            pgEndPos   = html.find('"' , pgStartPos) 
            numPages   = html[pgStartPos:pgEndPos]#.decode('unicode_escape','ignore').encode('utf-8')

            for pg in range(1, int(numPages)):
                text  = self.openContentStream(self.TVSERIESTVS + '&page=' + str(pg),'')
                text  = text.replace('\r','')
                text  = text.replace('\n','')
                text  = text.replace('class="sparticle','\n##SRCH##')
                lines = text.split('\n')
                text = ''

                for line in lines:
                    startMarker = line.find('##SRCH##')
                    if ( startMarker!=-1 ):
                        endMarker = line.find('</a>' , startMarker)
                        text = line[startMarker:endMarker] ;
                        descStart = text.find('class="first-title">') +20
                        descEnd   = text.find('</span>', descStart)
                        urlStart  = text.find('onclick="location.href=') +25
                        urlEnd    = text.find("'", urlStart) ;
                        desc2Start= text.find('>', urlEnd) +1
                        desc2End  = text.find('</span>', desc2Start) ; 
                        self.__log(  text[urlStart:urlEnd]  + ' ' + text[descStart:descEnd] + ' ' + text[desc2Start:desc2End] )
                        items.append((text[descStart:descEnd] + ' ' + text[desc2Start:desc2End] , text[urlStart:urlEnd]))

        if 0 == len(items):
            items.append(('Error no TV series items found (from TVs) NumPg:' + numPages, 'Error'))   
    
        self.__log('Finished getTVSerials-TVs')
        return items


#    return list with TV Serial Seasons 
    def getTVSerialSeasons(self, html):        
        self.__log('Start getTVSerialSeasons')
        text  = html
        text  = text.replace('\r','')
        lines = text.split('\n')
        text = ''
        for line in lines:
            if ( line.find('class="tabs')!=-1 ):
                text = text  + line                 
        self.__log('Seasons List Links: ' + text)
        links = text.split('<a')
        items = []
        if links:
            for lnk in links:
                if ( lnk.find('href="')!=-1 ):
                     urlStartPoint = lnk.find('href="') +6
                     urlEndPoint   = lnk.find('"' , urlStartPoint) 
                     nameStartPoint  = lnk.find('itemprop=' ,urlEndPoint) +16
                     nameEndPoint    = lnk.find('</span>' , nameStartPoint) 
                     ses_url   = lnk[urlStartPoint:urlEndPoint]#.decode('unicode_escape','ignore').encode('utf-8')
                     ses_name    = lnk[nameStartPoint:nameEndPoint]#.decode('unicode_escape','ignore').encode('utf-8')

                     items.append((ses_name, ses_url ))
            
 
        if 0 == len(items):
            items.append(('Error no TV season items found', 'Error'))   

        self.__log('Finished getTVSerialSeasons')
        return items

#    returns list with Seasons  Episodes
    def getTVSeasonEpisodes(self, html):        
        self.__log('Start getTVSeasonEpisodes')
        text  = html
        text  = text.replace('\r','')
        text  = text.replace('\n',' ')
        lines = text.split('<a')
        text = ''
        for line in lines:
            if ( line.find('" class="episod"')!=-1 ):
                text = text  + '<aaa>' + line                 
        self.__log('Season Episodes List Links: ' + text)
        links = text.split('<aaa>')
        items = []
        if links:
            for lnk in links:
                if ( lnk.find('href="')!=-1 ):
                     urlStartPoint   = lnk.find('href="'                   ) + 6
                     urlEndPoint     = lnk.find('"'       , urlStartPoint  ) 
                     nameStartPoint  = lnk.find('itemprop="name'     , urlEndPoint    ) + 16
                     nameEndPoint    = lnk.find('<span'    , nameStartPoint ) 
                     nameStartPoint2  = nameEndPoint + 26
                     nameEndPoint2    = lnk.find('</span>'    , nameStartPoint ) 
                     titleStartPoint = lnk.find('title="' , nameEndPoint   ) + 7 
                     titleEndPoint   = lnk.find('"'       , titleStartPoint) 


                     ses_url   = lnk[urlStartPoint:urlEndPoint]#.decode('unicode_escape','ignore').encode('utf-8')
                     ses_name  = lnk[nameStartPoint:nameEndPoint] + lnk[nameStartPoint2:nameEndPoint2]#.decode('unicode_escape','ignore').encode('utf-8')
                     ses_title = lnk[titleStartPoint:titleEndPoint]#.decode('unicode_escape','ignore').encode('utf-8')

                     items.append((ses_name + ' - ' + ses_title, ses_url ))
            
 
        if 0 == len(items):
            items.append(('Error no TV Episode items found', 'Error'))   

        self.__log('Finished getTVSeasonEpisodes')
        return items

#    returns list with Seasons  Episodes from TVs
    def getTVSeasonEpisodesTVs(self, html):        
        self.__log('Start getTVSeasonEpisodesTVs')
        #self.__log('html')
        text  = html
        text  = text.replace('\r','')
        text  = text.replace('\n',' ') 
        text  = text.replace('<span class="se tick2"></span>','') # fix idiotic html
        lines = text.split('<a class="sparticle"')
        text = ''
        for line in lines:
            #self.__log('l: ' + line +'\n\n\n')
            if ( line.find('data-key')!=-1 ):
                text = text  + '<aaa>' + line                 
        #self.__log('Colection Episodes List Links: ' + text)
        links = text.split('<aaa>')
        items = []
        if links:
            for lnk in links:
                if ( lnk.find('data-index')!=-1 ):
                     urlStartPoint   = lnk.find('data-key="'                   ) +10
                     urlEndPoint     = lnk.find('"'       , urlStartPoint  ) 
                     nameStartPoint  = lnk.find('"first-title">'     , urlEndPoint    ) + 14
                     nameEndPoint    = lnk.find('</span'    , nameStartPoint ) 
                     nameStartPoint2 = lnk.find('<br'     , nameEndPoint    ) +6
                     nameEndPoint2   = lnk.find('</span>'  , nameStartPoint2 ) 

                     #self.__log(lnk)
                     ses_url   = lnk[urlStartPoint:urlEndPoint]#.decode('unicode_escape','ignore').encode('utf-8')
                     ses_name  = lnk[nameStartPoint:nameEndPoint] +' - ' + lnk[nameStartPoint2:nameEndPoint2]#.decode('unicode_escape','ignore').encode('utf-8')

                     #ToDO: find how to transform data-key and data-index to video-key
                     #      until then use HD DVR
                     ses_url = 'ch_' + ses_url
                     ses_url = ses_url.replace('_dvr','_hd_dvr')
                     ses_url = ses_url.replace('#','%23')

                     items.append((ses_name , ses_url ))
                     self.__log(ses_url + ' ' + ses_name)
            
 
        if 0 == len(items):
            items.append(('Error no TV Episode items found', 'Error'))   

        self.__log('Finished getTVSeasonEpisodesTVs')
        return items


#    returns list with TV stations/chanels 
    def getTVStations(self, html):        
        self.__log('Start getTVStations. Paramter html is: ' + html)
        text  = html
        text  = text.replace('\r','')
        lines = text.split('\n')
        text = ''
        for line in lines:
            if ( line.find('/channels/')!=-1 ):
                text = text  + line                 
        self.__log('CH List Links: ' + text)
        links = text.split('<a')
        items = []
        if links:
            for lnk in links:
                if ( lnk.find('/channels/')!=-1 ):
                     urlstartpoint = lnk.find('/channels/') +10
                     urlendpoint   = lnk.find('"' , urlstartpoint) 
                     idstartpoint  = lnk.find('class="tv_entry') +15
                     idendpoint    = lnk.find('"' , idstartpoint) 
                     ch_url   = lnk[urlstartpoint:urlendpoint].decode('unicode_escape','ignore').encode('utf-8')
                     ch_id    = lnk[idstartpoint:idendpoint].decode('unicode_escape','ignore').encode('utf-8')
                     ch_name  = ch_id.replace('_',' ').upper()
                     ch_img   = ''
                     items.append((ch_name, ch_url, ch_id, ch_img ))
       
 
        if 0 == len(items):
            items.append(('Error no TV station items found', 'Error'))   

        self.__log('Finished getTVStations')
        return items

# returns the highest possible resolution for a specific channel 
    def getHighestTVResolution(self, html, ch_url):        
        self.__log('Start getHighestTVResolution')
        text  = html
        text  = text.replace('\r','')
        lines = text.split('\n')
        text = ''
        for line in lines:
            if ( line.find('/channels/'+ch_url)!=-1 and line.find('q=')!=-1):
                text = text  + line                 
        self.__log('Res List: ' + text)
        links = text.split('<a')
        if links:
            for lnk in links:
                url_params = ''
                if ( lnk.find('q=')!=-1):
                    startpoint = lnk.find('q=') +2
                    endpoint   = lnk.find('"' , startpoint) 
                    res_id     = lnk[startpoint:endpoint].decode('unicode_escape','ignore').encode('utf-8')
                    if ( res_id=='hd' ):
                        self.__log('Found HD')
                        url_params = ch_url + '?&q=' + res_id
                    if ( res_id=='high' and url_params == '' ):				
                        self.__log('Found High')
                        url_params = ch_url + '?&q=' + res_id
                else: 
                    self.__log('No video qualty parameters found')
                    url_params = ch_url + '?' 
   
        self.__log('Finished getHighestTVResolution with url_params: ' + url_params)
        return url_params


# returns list of resolutions for specific channel 
    def getTVResolutions(self, html, ch_url):        
        self.__log('Start getTVResolutions')
        text  = html
        text  = text.replace('\r','')
        lines = text.split('\n')
        text = ''
        for line in lines:
            if ( line.find('/channels/'+ch_url)!=-1 and  line.find('q=')!=-1):
                text = text  + line                 
        self.__log('Res List: ' + text)
        links = text.split('<a')
        items = []
        if links:
            for lnk in links:
                if ( lnk.find('q=')!=-1 ):
                     startpoint = lnk.find('q=') +2
                     endpoint   = lnk.find('"' , startpoint) 
                     res_id     = lnk[startpoint:endpoint].decode('unicode_escape','ignore').encode('utf-8')
                     res_name   = res_id.upper()
                     url_params = ch_url + '?&q=' + res_id
                     items.append((res_name, url_params))

        if 0 == len(items):
            url_params = ch_url + '?' 
            items.append(('Default quality', url_params))   

   
        self.__log('Finished getTVResolutions')
        return items 
 
#    returns the stream to live TV
    def getTVStream(self,tvstation_params):
        self.__log('Start getTVStream')
        self.__log('TVStream:'+self.MAINURL +'/channels/' +tvstation_params )
        html = self.openContentStream(self.MAINURL + '/channels/' + tvstation_params ,'')
        clip_url = ''
        if ( html.find('video_key')!=-1 ):
           key_pos    = html.find('video_key')
           start      = html.find('"', key_pos  ) + 1
           end        = html.find('"', start  )
           video_key  = html[start:end] #    # --post-data 'video_key=ch_btvhd_high_dvr#1402361201'    http://mytv.bg/player_config_g/config
           #xbmc.log("vk - " + video_key )
           #xbmc.log("lt - %d" % time.time() )
           urlopen = urllib2.urlopen 
           request = urllib2.Request
           the_url = self.MAINURL + '/player_config_g/config'
           txdata = 'video_key=' + video_key  
           req = request(the_url, txdata, self.USERAGENT)
           handle = urlopen(req)     
           html = handle.read() 
     
           clip_pos   = html.find('clip')
           start      = html.find('\'url\':', clip_pos  ) + 8
           end        = html.find('\'', start  )
           clip_url   = html[start:end]
        self.__log('Finished getTVStream :' +clip_url)
        return clip_url

#    returns the stream based on data-key and data-index
    def getTVStreamDirect(self,tvstation_params):
        self.__log('Start getTVStreamDirect ' + tvstation_params)
        clip_url = ''
        urlopen = urllib2.urlopen 
        request = urllib2.Request
        the_url = self.MAINURL + '/player_config_g/config?video_key=ch_'+ tvstation_params
        self.__log('Conf URL: ' + the_url)
        txdata = 'video_key=' + tvstation_params  
        req = request(the_url, txdata, self.USERAGENT)
        handle = urlopen(req)     
        html = handle.read() 
        self.__log(html)
        clip_pos   = html.find('clip')
        start      = html.find('\'url\':', clip_pos  ) + 8
        end        = html.find('\'', start  )
        clip_url   = html[start:end]
        self.__log('Finished getTVStreamDirect :' +clip_url)
        return clip_url

#    returns the stream to  TV series episode
    def getEpisodeStream(self,episode_params):
        self.__log('Start getEpisodeStream ')
        self.__log('EpisodeStream:'+self.MAINURL +'/'+ episode_params )
        html = self.openContentStream(self.MAINURL + '/' + episode_params ,'')
        if ( html.find('video_key')!=-1 ):
           key_pos    = html.find('video_key')
           start      = html.find('"', key_pos  ) + 1
           end        = html.find('"', start  )
           #To DO: add current time
           video_key  = html[start:end]       # --post-data 'video_key=614f73fvkgny'    http://mytv.bg/player_config_g/config
           urlopen = urllib2.urlopen 
           request = urllib2.Request
           the_url = self.MAINURL + '/player_config_g/config'
           txdata = 'video_key=' + video_key  
           req = request(the_url, txdata, self.USERAGENT)
           handle = urlopen(req)     
           html = handle.read() 
     
           clip_pos   = html.find('\'bitrates\': [')
           start      = html.find('\'url\':', clip_pos  ) + 8
           end        = html.find('\'', start  )
           clip_url   = html[start:end]
        self.__log('EpisodeStream:'+video_key )
        self.__log('EpisodeStream:'+self.MAINURL +episode_params )
        self.__log('Finished getEpisodeStream :' +clip_url)
        return clip_url

#    returns list with ofsets for specified chanel
    def getTVChanelTimeShifts(self, html):        
        self.__log('Start getTVChanelTimeShifts')
        text  = html
        text  = text.replace('\r','')
        text  = text.replace('\n',' ')
        lines = text.split('<a')
        text = ''
        for line in lines:
            if ( line.find('offset')!=-1 or line.find('<span class="the-title"><span>')!=-1  ):
                text = text  +  line                 
        self.__log('Time shift links ' + text)
        links = text.split('<')
        items = []
        if links:
            for lnk in links:
                if ( lnk.find('offset=')!=-1 ):
                     ofStartPoint    = lnk.find('offset='                  ) + 7
                     ofEndPoint      = lnk.find('"'       , ofStartPoint   ) 
                     nameStartPoint  = lnk.find('>'       , ofEndPoint     ) + 1 
                     nameEndPoint    = lnk.find('<div'    , nameStartPoint ) 


                     of_val   = lnk[ofStartPoint:ofEndPoint]
                     of_name  = lnk[nameStartPoint:nameEndPoint]

                     items.append ( ( of_name ,  of_val) ) 
 
#        if len(items) == 0:
#            items['Error'] = 'Error. No time ofsets'   

        self.__log('Finished getTVChanelTimeShifts')
        return items
    
#    returns ch  info 
    def getTVChanelInfo(self, html ,offset):        
        self.__log('Start getTVCnanelInfo')
        text  = html
        text  = text.replace('\r','')
        lines = text.split('\n')
        text = ''
        items=[]
        toFind = 'offset=%d' % offset
        for line in lines:
            if ( line.find( toFind)!=-1 or line.find('<span class="the-title"><span>')!=-1 or line.find('<span class="the-time">')!=-1  ):
                text = text  + line  
        self.__log('CH info: ' + text)
        pos_offset = text.find(toFind)
        if ( pos_offset !=-1 ):
             urlstartpoint   = text.find('data-screen="' , pos_offset) +13
             urlendpoint     = text.find('"' , urlstartpoint) 
             tmStart         = text.find('<span class="the-time">',urlendpoint) + 23
             tmEnd           = text.find('</span>')
             titstartpoint   = text.find('<span class="the-title"><span>', tmEnd) +30
             titendpoint     = text.find('</span>' , titstartpoint) 
             tit2startpoint  = text.find('<i>', titendpoint) +3
             tit2endpoint    = text.find('</i>' , tit2startpoint) 

             ch_img         = text[urlstartpoint:urlendpoint]
             ch_title_tm    = text[tmStart:tmEnd]
             ch_title_name  = text[titstartpoint:titendpoint] + ' >> '+ text[tit2startpoint:tit2endpoint]

             items.append( (ch_title_name, ch_img, ch_title_tm ) )
       
 
        if 0 == len(items):
            items.append(('', '',''))   

        self.__log('Finished getTVCnanelInfo')
        return items

'''
    end of mytv class
'''

from pyxbmct.addonwindow import *

import urllib

class TimeShiftDialog( AddonDialogWindow ):
    timeStamp = 0
    time = ''
    title = ''
    pic = ''
    ofsets = []
    MyTVbg = []
    selOffset =0 
    ch_url =''
    addon      = xbmcaddon.Addon()
    addon_path = addon.getAddonInfo('path')
    start = 0


    def __init__(self, shifts, ch_url, tv_username, tv_password):
        super(TimeShiftDialog, self).__init__('Time Offsets')
        numShifts = len( shifts )
        self.start = 0
        self.selOffset =0

        self.setGeometry(800, 600,  13, 12 )
        self.connect(ACTION_NAV_BACK, self.close)

        self.ofsets = shifts
        self.ch_url = ch_url
        self.list = List()
        self.placeControl(self.list, 0, 0, numShifts, 2)
        items=[]
        for index in range( 0, numShifts ):
            items.append(  shifts[index][0] ) 
        self.list.addItems(items)
        self.connect(self.list,  self.onSelectionChange )

        self.image = Image(os.path.join(_addon_path , 'resources', 'xbmc-logo.png'))
        self.placeControl(self.image, 0, 2, 8, 9)
        
        time_label = Label('Time:')
        self.placeControl(time_label, 8, 2)

        self.boxTime = TextBox()
        self.placeControl(self.boxTime, 8, 3, 1, 8)

        title_label = Label('Title:')
        self.placeControl(title_label, 9, 2)

        self.boxTitle = TextBox()
        self.placeControl(self.boxTitle, 9, 3, 2, 8)

        self.button = Button('Start')
        self.placeControl(self.button, 11, 2,2,8)
        self.connect(self.button, self.onClickButton )      
        
        self.button.setNavigation(self.list, self.list, self.list, self.list)
        self.list.controlLeft(self.button)
        self.list.controlRight(self.button)
        
        self.MyTVbg = mytv(tv_username, tv_password)
        self.onSelectionChange() # get title,image,rtime for offset=0
 
        self.boxTime.setText(  self.time  )
        self.boxTitle.setText( self.title)

        self.setFocus(self.button)

 
    def onSelectionChange(self):
        self.selOffset = self.list.getSelectedPosition()
        self.timeStamp = time.time() - 3600*self.selOffset
        self.time      = self.timeStampToString(self.timeStamp)
        dialog = xbmcgui.Dialog()

        chanel_info = mytv.MAINURL + '/channels/' + self.ch_url + '&offset=%d' % self.selOffset
        #xbmc.log( 'Time Offset Dialog (1)   ' +  chanel_info + ' sel=%d' % self.selOffset)
        res = self.MyTVbg.getTVChanelInfo( self.MyTVbg.openContentStream(chanel_info,'')  , self.selOffset) 

        #xbmc.log( 'Time Offset Dialog (2)  %s %s %s  ' %  res[0] )
        if (0 != len(res[0][0])) :
            self.title     = '[' + res[0][2] +'] ' +res[0][0]
            self.pic = res[0][1]
            self.boxTime.setText(  self.time  )
            self.boxTitle.setText( self.title)
            try:
             resource = urllib.urlopen(self.pic)
             output = open( os.path.join(_tempdir,'mytv-bg-tmp%d.jpg' %  self.selOffset),"wb")
             output.write(resource.read())
             output.close()
             self.image.setImage( os.path.join(_tempdir,'mytv-bg-tmp%d.jpg' %  self.selOffset) )
            except:
             dialog.ok("Error", 'Error opening chanel snapshot image.\n'+self.pic+'\nCheck login credentials.') 
             self.start = 0
             self.close()

        else:
            self.title = 'No title (DVR stream)'
            self.boxTitle.setText( self.title)

            
        #xbmc.log('%s class: %s' % ('Time Offset Dialog  (3 )mytv-bg-tmp%d.jpg' % self.selOffset, 'tmp pic:'+self.pic) )

        #lambda: xbmc.executebuiltin('Notification(Ofset:,%s selected.)' %   self.list.getListItem(self.list.getSelectedPosition()).getLabel())
        #dialog = xbmcgui.Dialog()
        #dialog.ok("DBG", 'Click ' + self.list.getListItem(self.list.getSelectedPosition()).getLabel() +  '%s ' % self.ofsets[self.list.getSelectedPosition()][1]  )
        #xbmc.sleep(2000)
        return
  
    def onClickButton(self):
        self.start = 1
        self.close()
        return

  
    def onClickButton(self):
        self.start = 1
        self.close()
        return

    def timeStampToString(self,tm):
        res = ' %s ( %d )' % ( time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime(tm) )   , tm    ) 
        return res
'''
    Public methods in lib mytv::lib
    Note: These methods are not part of the mytv class
'''
#    plays live stream
def playLiveStream(tv_username, tv_password, tvstation_params):
    log('Start playLiveStream')
    MyTVbg = mytv(tv_username, tv_password)    
    ofsets = MyTVbg.getTVChanelTimeShifts(   MyTVbg.openContentStream(mytv.MAINURL + '/channels/' + tvstation_params ,'' )   )
    stream_url= ''
    startPressed = 0
    selectedPosition = 0
    selectedTime = ''
    try:
        MyOffset = TimeShiftDialog(ofsets,tvstation_params,tv_username, tv_password)
        MyOffset.doModal()
        startPressed = MyOffset.start
        selectedPosition = MyOffset.selOffset
        selectedTime = MyOffset.timeStamp
        del MyOffset

    except:
        xbmc.log('PyXbmcT not supported. Enable to display timeOffsets')
        ofsets = []
        stream_url= ''
        MyOffset = 0

    if len(ofsets) != 0: # real live stream
        if ( 1 == startPressed ): # play only if START was pressed
          stream_url=MyTVbg.getTVStream(tvstation_params + ('&offset=%d' % selectedPosition)  )
          stream_url = stream_url[0:stream_url.find('&time=')] 
          stream_url = stream_url  +  ('&time=%d&t1=%d&t2=%d' % (selectedTime, selectedTime, selectedTime + 10000)) 
          xbmc.Player().play(stream_url)    
    else: # not a live stream, but a recordered one which is placed in /channels url
      stream_url=MyTVbg.getTVStream( tvstation_params )
      st = urllib.unquote(stream_url).decode('utf8') 
      #xbmc.log('%s %s' % (stream_url, st) )
      xbmc.Player().play(st)
    
    log('URL: ' + stream_url)
    log('Finished playLiveStream')
    html=''
    return 

#    plays live stream directly without tomeshift selection
def playDirectLiveStream(tv_username, tv_password, ch_url):
    log('Start playDirectLiveStream')
    MyTVbg = mytv(tv_username, tv_password)    
    stream_url= ''
    ch_details = MyTVbg.openContentStream((mytv.MAINURL + '/channels/' +ch_url),'')
    tvstation_params = MyTVbg.getHighestTVResolution(ch_details, ch_url)
    
    if (ch_url == 'newschannel' or ch_url == 'bta'): # not real live streams, no offset parameters
        stream_url=MyTVbg.getTVStream( tvstation_params )
        st = urllib.unquote(stream_url).decode('utf8') 
        #xbmc.log('%s %s' % (stream_url, st) )
        xbmc.Player().play(st)
    else:
        stream_url=MyTVbg.getTVStream(tvstation_params + ('&offset=0')  )
        stream_url = stream_url[0:stream_url.find('&time=')] 
        stream_url = stream_url  +  ('&time=0&t1=0&t2=10000') 
        xbmc.Player().play(stream_url)    
    
    log('URL: ' + stream_url)
    log('Finished playDirectLiveStream')
    html=''
    return 



#    play episode stream
def playEpisodeStream(tv_username, tv_password, episode_params):
    log('Start playEpisodeStream ')
    MyTVbg = mytv(tv_username, tv_password)    
    stream_url=MyTVbg.getEpisodeStream(episode_params)
    st = urllib.unquote(stream_url).decode('utf8') 
    #xbmc.log('%s %s' % (stream_url, st) )
    xbmc.Player().play(st)
    log('URL: ' + stream_url)
    log('Finished playEpisodeStream')
    html=''
    return 

#    play episode stream TVs
def playEpisodeStreamTVs(tv_username, tv_password, episode_params):
    log('Start playEpisodeStreamTVs ')
    MyTVbg = mytv(tv_username, tv_password)    
    stream_url=MyTVbg.getTVStreamDirect(episode_params)
    st = urllib.unquote(stream_url).decode('utf8') 
    #xbmc.log('%s %s' % (stream_url, st) )
    xbmc.Player().play(st)
    log('URL: ' + stream_url)
    log('Finished playEpisodeStreamTVs')
    html=''
    return 


#    returns list of all live TV stations
def showTVStations(tv_username, tv_password):
    log('Start showMyTVStations')
    MyTVbg = mytv(tv_username, tv_password)
    items = MyTVbg.getTVStations(MyTVbg.openContentStream(mytv.CONTENTURL,''))
    log('Finished showMyTVStations')
    return items

#    returns list of resolutions for specific station/chanel
def showTVResolutions(tv_username, tv_password, ch_url):
    log('Start showMyTVresolutions')
    MyTVbg = mytv(tv_username, tv_password)
    items = MyTVbg.getTVResolutions(MyTVbg.openContentStream(mytv.CONTENTURL + '/'+ ch_url,''),ch_url)
    log('Finished showMyTVresolutions')
    return items

#    returns list of TV serial from VOYO
def showTVSerials(tv_username, tv_password):
    log('Start showTVSerials')
    MyTVbg = mytv(tv_username, tv_password)
    items = MyTVbg.getTVSerials(MyTVbg.openContentStream(mytv.TVSERIES,''))
    log('Finished showTVSerials')
    return items

#    returns list of TV serial that come TVs
def showTVSerialsFromTVs(tv_username, tv_password):
    log('Start showTVSerialsFromTVs ' + mytv.TVSERIESTVS)
    MyTVbg = mytv(tv_username, tv_password)
    #log( MyTVbg.openContentStream(mytv.TVSERIESTVS,'') )
    html =  MyTVbg.openContentStream(mytv.TVSERIESTVS,'') 
    items = MyTVbg.getTVSerialsTVs( html )   ##### Series from FVs
    log('Finished showTVSerialsFromTVs')
    return items

#    returns list of seasons for specific TV serial
def showTVSerialSeasons(tv_username, tv_password, ser_url):
    log('Start showTVSerialSeasons')
    MyTVbg = mytv(tv_username, tv_password)
    items = MyTVbg.getTVSerialSeasons( MyTVbg.openContentStream(mytv.MAINURL + '/'+ ser_url,'') )
    log('Finished showTVSerialSeasons')
    return items

#    returns list of series for specific season and TV serial from VOYO
def showTVSeasonEpisodes(tv_username, tv_password, ses_url):
    log('Start showTVSeasonEpisodes')
    MyTVbg = mytv(tv_username, tv_password)
    items = MyTVbg.getTVSeasonEpisodes(MyTVbg.openContentStream(mytv.MAINURL + '/'+ ses_url,''))
    log('Finished showTVSeasonEpisodes')
    return items

#    returns list of series for specific colection serials from TVs
def showTVSeasonEpisodesTVs(tv_username, tv_password, ses_url):
    log('Start showTVSeasonEpisodesTVs')
    MyTVbg = mytv(tv_username, tv_password)
    items = MyTVbg.getTVSeasonEpisodesTVs(MyTVbg.openContentStream(mytv.MAINURL + '/'+ ses_url,''))
    log('Finished showTVSeasonEpisodesTVs')
    return items


'''
    public log method
'''         
def log(text):
    debug = True
    if (debug == True):
        xbmc.log('%s libname: %s' % (LIBNAME, text))
    else:
        if(DEBUG == True):
            xbmc.log('%s libname: %s' % (LIBNAME, text))
            
