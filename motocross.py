import sys
import xbmcplugin, xbmcgui, xbmcaddon, xbmc
import re, os, time
import urllib, urllib2
import json

ROOTDIR = xbmcaddon.Addon(id='plugin.video.amaproracing').getAddonInfo('path')
ROOTURL = 'http://www.promotocross.com'
FANART = ROOTDIR+'/images/fanart_motocross.jpg'
ICON = ROOTDIR+'/images/icon_motocross.png'
MAIN_URL = 'http://www.promotocross.com'
USER_AGENT = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2272.104 Safari/537.36'

class motocross():

    def categories(self):
        #http://www.promotocross.com/media-block-get-filter-options-ajax/ajax/filter-category/all/16/video/all/all/all/all/all
        url = 'http://www.promotocross.com/media-block-get-filter-options-ajax/ajax/filter-category/all/16/video/all/all/all/all/all'
        #self.optionsToDir(url)

        self.addDir('Full Motos On Demand','/GET_YEAR',100,'')    
        self.addDir('Showcase','/GET_HIGHLIGHTS',101,'')        
        self.setLiveLink(MAIN_URL+'/mx/live') 
        #self.addDir('Test Archive','http://www.promotocross.com/mx/event/hangtown-2015/video/2015-hangtown-250-moto-1-full-race',106,'')


    def optionsToDir(url):        
        req = urllib2.Request(url)      
        req.add_header('User-Agent', ' Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.9.0.3) Gecko/2008092417 Firefox/3.0.3')
        response = urllib2.urlopen(req)        
        json_source = json.load(response)
        response.close()

        options = json_source['options']
        for option in options:
            #start = link.find('"')
            #end = link.find("Load More Posts")
            #link = link[start:end]
            xbmc.log(option)
            xbmc.log(options[option])
            self.addDir(options[option],option,100,'')


    def fullMotoYears(self):
        url = 'http://www.promotocross.com/media-block-get-filter-options-ajax/ajax/filter-year/451/16/video/all/all/all/all/all'
        req = urllib2.Request(url)      
        req.add_header('User-Agent', ' Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.9.0.3) Gecko/2008092417 Firefox/3.0.3')
        response = urllib2.urlopen(req)        
        json_source = json.load(response)
        response.close()

        options = json_source['options']                
        year_dict = {}
        for option in  options:           
            year_dict[option] = options[option]
            
        for key in sorted(year_dict, reverse=True):            
            self.addDir(year_dict[key],key,103,'')


    def fullMotosOnDemand(self, url):        
        n=0
        found_stream = True        
        while found_stream:
            xbmc.log(url+str(n*11))
            req = urllib2.Request(url+str(n*11))      
            req.add_header('User-Agent', ' Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.9.0.3) Gecko/2008092417 Firefox/3.0.3')
            response = urllib2.urlopen(req)        
            json_source = json.load(response)
            response.close()

            xbmc.log(str(json_source))

            link = json_source[1]['data']
            link = link.decode('utf-8')
            link = link.replace('\n',"")            
            
            match = re.compile('<img typeof="foaf:Image" src="(.+?)"(.*?)/></a>(.*?)<a href="(.*?)">(.+?)Full Race', re.IGNORECASE).findall(link)         
            found_stream = False
            for image_url, junk, junk2, temp_url, title in match:                
                found_stream = True
                title = title.replace('(','')
                title = title.replace(':','')                
                stream = MAIN_URL+temp_url
                #self.addDir(title,MAIN_URL+url,104,image_url)                
                self.addStream(title,stream,106,image_url)

            n = n+1
    

    

    def scrapeStream(self,url,video_name,image_link):        
        req = urllib2.Request(url)
        req.add_header('User-Agent', ' Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.9.0.3) Gecko/2008092417 Firefox/3.0.3')
        response = urllib2.urlopen(req)
        link=response.read()
        response.close()        
        url = link.replace('\n',"")
        #######################################################################
        #Search for vplayer hyper-link in url code
        #######################################################################
        #print "INCOMING URL:"+url
        #build_button('http://vplayer.nbcsports.com/p/BxmELC/allisports/select/IXBYA0ptkIA6?autoPlay=true');            
        #start = url.find('http://vplayer.nbcsports.com')        
        start_str = "build_button('"
        start = url.find(start_str)
        end = url.find('?autoPlay=true',start)
        url = url[start+len(start_str):end]                      
        #print 'DONE GETTING URL:'+str(start)+' '+str(end)+url
        #######################################################################

        req = urllib2.Request(url)            
        req.add_header('User-Agent', ' Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.9.0.3) Gecko/2008092417 Firefox/3.0.3')
        response = urllib2.urlopen(req)
        video_link=response.read()
        response.close()                  
        video_link = video_link.replace('\n',"")                    
        
        #######################################################################
        #Pull SMIL file link from url response
        #######################################################################
        start_text = 'http://link.theplatform.com'
        start = video_link.index(start_text)        
        end = video_link.find('" type="application/smil+xml" />')
        video_link = video_link[start:end]                  
        #print "HERE IS WHAT'S COMING BACK ==="+str(start)+' '+str(end)+video_link
        #######################################################################
            
        req = urllib2.Request(video_link)            
        req.add_header('User-Agent', ' Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.9.0.3) Gecko/2008092417 Firefox/3.0.3')
        response = urllib2.urlopen(req)
        video_link=response.read()
        response.close()      
        
        ########################################################################
        #Change image_link to high quality version
        ########################################################################
        #http://www.promotocross.com/sites/default/files/styles/tour_thumb/public/images/video/thumbnail/holeshot_250_moto_2_hangtown_RICE_5089_1280_960x540.jpg
        #http://www.promotocross.com/sites/default/files/images/video/thumbnail/holeshot_250_moto_2_hangtown_RICE_5089_1280.jpg

        #print image_link 
        #image_link = image_link.replace('styles/tour_thumb/public','')
        #image_link = image_link.replace('_960x540.jpg','.jpg')
        #print image_link

        #######################################################################
        #Read SMIL response file and pull the highest quality video from it
        #######################################################################
        #print "NOW THE SMIL="+video_link
          
        match=re.compile('<video src="(.+?)" system-bitrate="(.+?)" height="(.+?)" width="(.+?)"/>').findall(video_link,10)
        stream_url = ''
        stream_url = {}
        stream_title = [] 
        for link,bitrate,height,width in match:  
            #Convert bitrate to kb
            bitrate = str(int(bitrate) / 1024)
            title = bitrate+'kbps ('+width+'x'+height+')'
            stream_title.append(title)                
            stream_url.update({title:link+'|User-Agent='+USER_AGENT})
            #Add only the first (highest quality) video as a selection
            #self.addLink(video_name,link,video_name,image_link) 
            #stream_url = link
            #break

        dialog = xbmcgui.Dialog()
        ret = dialog.select('Choose Stream Quality', stream_title)        
        if ret >=0:
            stream_url = stream_url.get(stream_title[ret]) 
        else:
            sys.exit()


        return stream_url
        #######################################################################


    def addDir(self,name,url,mode,iconimage,fanart=None):   
        params = self.get_params()
        prev_name = ''
        full_name = ''
        try:
            prev_name=urllib.unquote_plus(params["full_name"])
        except:
            pass 
        if mode > 104:
            if prev_name != '':
                full_name = prev_name + ' - ' + name
            else:
                full_name = name

        u=sys.argv[0]+"?url="+urllib.quote_plus(url)+"&mode="+str(mode)+"&name="+urllib.quote_plus(name)+"&full_name="+urllib.quote_plus(full_name)+"&img_url="+urllib.quote_plus(iconimage)

        year = ''
        if mode == 104:
            year = name
        else:        
            try:
                year=urllib.unquote_plus(params["year"])
            except:
                pass 

        u = u+"&year="+urllib.quote_plus(year)
        ok=True
        liz=xbmcgui.ListItem(name, iconImage=ICON, thumbnailImage=iconimage)
        liz.setInfo( type="Video", infoLabels={ "Title": name } )
        if fanart == None:
            fanart = FANART
        liz.setProperty('fanart_image', fanart)
        ok=xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=u,listitem=liz,isFolder=True)    
        return ok


    def addStream(self,name,url,mode,iconimage,fanart=None):       
        ok=True
        u=sys.argv[0]+"?url="+urllib.quote_plus(url)+"&mode="+str(mode)+"&name="+urllib.quote_plus(name)
        u = u+"&img_url="+urllib.quote_plus(iconimage)            
        liz=xbmcgui.ListItem(name, iconImage=ICON, thumbnailImage=iconimage)            
        liz.setInfo(type="Video", infoLabels='')
        if fanart != None:
            liz.setProperty('fanart_image', fanart)
        else:
            liz.setProperty('fanart_image', FANART)

        print u
        liz.setProperty("IsPlayable", "true")
        ok=xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=u,listitem=liz,isFolder=False)
        xbmcplugin.setContent(int(sys.argv[1]), 'episodes')
        
        return ok

    def playStream(self, stream_url):
        #stream_url = self.CHECK_FOR_NBC_VIDEO(url,'','')
        #url = stream_url.get(stream_title[ret]) 
        listitem = xbmcgui.ListItem(path=stream_url)
        #listitem = xbmcgui.ListItem(path=stream_url[ret])       
       
        xbmcplugin.setResolvedUrl(int(sys.argv[1]), True, listitem)


    def getPID(self):
        ##########################################################################################################
        #Request the NBC sports moto stream, which redirects to a link that contains a PID variable that is needed    
        ##########################################################################################################

        req = urllib2.Request('http://motostream.nbcsports.com/')            
        #req.add_header('Connection','keep-alive')
        req.add_header('Accept','text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8')
        req.add_header('User-Agent', ' Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.9.0.3) Gecko/2008092417 Firefox/3.0.3') 
        req.add_header('Accept-Encoding', 'gzip,deflate,sdch')
        req.add_header('Accept-Language', 'en-US,en;q=0.8')
        req.add_header('Referer', 'http://www.promotocross.com/motocross/live')

        response = urllib2.urlopen(req)        
        pid_url = response.geturl()
        response.close()  
        xbmc.log('REDIRECT URL:' + pid_url)
        ##########################################################################################################

        ##########################################################################################################
        #Get the PID value from the url and create a link to the json file which contains the f4m file link
        #'http://stream.nbcsports.com/motocross/?pid=15620&referrer='
        ##########################################################################################################    
        start_str = 'http://stream.nbcsports.com/motocross/?pid='
        start = pid_url.find(start_str)
        end = pid_url.find('&referrer=',start)            
        pid = pid_url[start+len(start_str):end]                

        xbmc.log("PID="+pid)
        return pid


    def getHighlights(self):               
        #highlights = 'http://stream.nbcsports.com/data/mobile/moto-2013.json'
        highlights = 'http://stream.nbcsports.com/data/mobile/mcms/prod/nbc-moto.json '
                     #http://hdliveextra-pmd.edgesuite.net/HD/image_sports/mobile/2014-08-23T22-56-41.233Z--1280x720_m61.jpg
                     #http://hdliveextra-pmd.edgesuite.net/HD/image_sports/mobile/2014-08-16T18-55-51.666Z--1280x720_m61.jpg
        xbmc.log("HIGHLIGHT SOURCES:"+highlights)

        ###########################################
        #Read the json file and extraxt the f4m url
        ###########################################    
        req = urllib2.Request(highlights) 
        req.add_header('User-Agent', ' Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.9.0.3) Gecko/2008092417 Firefox/3.0.3') 
        #req.add_header('Referer', 'http://www.promotocross.com/motocross/live')
        response = urllib2.urlopen(req)        
        #data_sources = response.read()
        json_source = json.load(response)
        response.close()  
              
        #print data_sources
        #video_source =  json_source['videoSources']
        video_source =  json_source['spotlight']
        #video_source =  json_source['showCase']
        for item in video_source:
            #url =  item['sourceUrl'] + '|' + header_encoded            
            url = item['iosStreamUrl']
            name = item['title']
            if 'full race' not in name.lower():
                #info = item['info']
                imgurl = item['image']
                imgurl = 'http://hdliveextra-pmd.edgesuite.net/HD/image_sports/mobile/'+imgurl+'_m61.jpg'
                self.addLink(name,url,name,imgurl) 
    

    def setLiveLink(self,url): 
        
        req = urllib2.Request(url)            
        req.add_header('User-Agent', ' Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.9.0.3) Gecko/2008092417 Firefox/3.0.3')
        response = urllib2.urlopen(req)
        live_source = response.read()
        response.close()  

        pid = self.getPID()
        
        start_text = '<img alt="" class="media-image" height="540" width="960" typeof="foaf:Image" src="'
        start = live_source.find(start_text)        
        end = live_source.find('"',start+len(start_text))
        live_details_img = live_source[start+len(start_text):end] 

        #print 'Image Link'+ str(start) + ' '+ str(end) + live_details_img
        
        self.addDir('Live Stream',pid,102,live_details_img,live_details_img)    


    def playLive(self,pid):                

        #*********************************************************
        # LINK TO GET LIVE SOURCES 
        #ex. #http://stream.nbcsports.com/data/event_config_15620.json
        #*********************************************************
        live_sources = 'http://stream.nbcsports.com/data/live_sources_'+pid+'.json'   
        xbmc.log("LIVE SOURCES:"+live_sources)
        ##########################################################################################################


        ###########################################
        #Read the json file and extraxt the f4m url
        ###########################################
        req = urllib2.Request(live_sources)     
        req.add_header('User-Agent', ' Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.9.0.3) Gecko/2008092417 Firefox/3.0.3') 
        try:               
            response = urllib2.urlopen(req)         
            json_source = json.load(response)
            response.close()            
            
            video_source =  json_source['videoSources']


            for item in video_source:
                url =  item['sourceUrl']
                ios_url =  item['iossourceUrl']
                name = item['name'] + ' - ' + item['title']
                status = item['type']
               
            header = {  'User-Agent' : 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/35.0.1916.153 Safari/537.36',
                        'Accept' : '*/*',                  
                        'Referer' : 'http://stream.nbcsports.com/motocross/?pid='+pid+'&referrer=http://www.promotocross.com/motocross/live',
                        'Accept-Language' : 'en-US,en;q=0.8'} 
               
            header_encoded = urllib.urlencode(header)       
            url =  urllib.quote_plus(url+'|')       
            full_url = url + header_encoded     
            #print full_url
            ios_url = ios_url.replace('manifest(format=m3u8-aapl-v3)','QualityLevels(3450000)/Manifest(video,format=m3u8-aapl-v3,audiotrack=audio_en_0)')        
            ios_url = ios_url + '|User-Agent='+USER_AGENT            
            
            self.addLink(name,ios_url, name,FANART) 
        except:
            pass


    def get_params(self):
        param=[]
        paramstring=sys.argv[2]
        if len(paramstring)>=2:
                params=sys.argv[2]
                cleanedparams=params.replace('?','')
                if (params[len(params)-1]=='/'):
                        params=params[0:len(params)-2]
                pairsofparams=cleanedparams.split('&')
                param={}
                for i in range(len(pairsofparams)):
                        splitparams={}
                        splitparams=pairsofparams[i].split('=')
                        if (len(splitparams))==2:
                                param[splitparams[0]]=splitparams[1]
                                
        return param

    def addLink(self,name,url,title,iconimage):
        params = self.get_params()
        full_name = ''
        try:
            full_name = urllib.unquote_plus(params["full_name"])
        except:
            pass 
        
        if full_name != '':
            title = full_name + ' ' + title

        ok=True
        liz=xbmcgui.ListItem(name, iconImage="DefaultVideo.png", thumbnailImage=iconimage,)
        liz.setProperty('fanart_image',iconimage)
        liz.setInfo( type="Video", infoLabels={ "Title": title } )
        ok=xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=url,listitem=liz)
        return ok
