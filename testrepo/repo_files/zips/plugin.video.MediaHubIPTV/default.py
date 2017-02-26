#############Imports#############
import base64,os,re,requests,string,sys,urllib,json,urlparse,datetime,zipfile,shutil
import xbmc,xbmcaddon,xbmcgui,xbmcplugin
from resources.modules import client,control,tools
#################################

#############Defined Strings#############
addon_id     = 'plugin.video.MediaHubIPTV'
selfAddon    = xbmcaddon.Addon(id=addon_id)
icon         = xbmc.translatePath(os.path.join('special://home/addons/' + addon_id, 'icon.png'))
fanart       = xbmc.translatePath(os.path.join('special://home/addons/' + addon_id , 'fanart.jpg'))

username     = control.setting('Username')
password     = control.setting('Password')

host         = 'http://mediahubiptv.ddns.net'
port         = '4545'

live_url     = '%s:%s/enigma2.php?username=%s&password=%s&type=get_live_categories'%(host,port,username,password)
vod_url      = '%s:%s/enigma2.php?username=%s&password=%s&type=get_vod_categories'%(host,port,username,password)
panel_api    = '%s:%s/panel_api.php?username=%s&password=%s'%(host,port,username,password)
play_url     = '%s:%s/live/%s/%s/'%(host,port,username,password)

advanced_settings           =  xbmc.translatePath('special://home/addons/'+addon_id+'/resources/advanced_settings')
advanced_settings_target    =  xbmc.translatePath(os.path.join('special://home/userdata','advancedsettings.xml'))
#########################################


def start():
	if username=="":
		user = userpopup()
		passw= passpopup()
		control.setSetting('Username',user)
		control.setSetting('Password',passw)
		xbmc.executebuiltin('Container.Refresh')
		auth = '%s:%s/enigma2.php?username=%s&password=%s&type=get_vod_categories'%(host,port,user,passw)
		auth = OPEN_URL(auth)
		if auth == "":
			line1 = "Incorrect Login Details"
			line2 = "Please Re-enter" 
			line3 = "" 
			xbmcgui.Dialog().ok('Attention', line1, line2, line3)
			start()
		else:
			line1 = "Login Sucsessfull"
			line2 = "Welcome to MediaHub IPTV" 
			line3 = ('[COLOR blue]%s[/COLOR]'%user)
			xbmcgui.Dialog().ok('MediaHub IPTV', line1, line2, line3)
			pvrsetup()
			asettings()
			xbmc.executebuiltin('Container.Refresh')
			home()
	else:
		auth = '%s:%s/enigma2.php?username=%s&password=%s&type=get_vod_categories'%(host,port,username,password)
		auth = OPEN_URL(auth)
		if not auth=="":
			addDir('Account Information','url',6,icon,fanart,'')
			addDir('Live IPTV','live',1,icon,fanart,'')
			if xbmc.getCondVisibility('System.HasAddon(pvr.iptvsimple)'):
				addDir('TV Guide','pvr',7,icon,fanart,'')
			addDir('VOD','vod',3,icon,fanart,'')
			addDir('Search','url',5,icon,fanart,'')
			addDir('Settings','url',8,icon,fanart,'')
			
def home():
	addDir('Account Information','url',6,icon,fanart,'')
	addDir('Live IPTV','live',1,icon,fanart,'')
	if xbmc.getCondVisibility('System.HasAddon(pvr.iptvsimple)'):
		addDir('TV Guide','pvr',7,icon,fanart,'')
	addDir('VOD','vod',3,icon,fanart,'')
	addDir('Search','',5,icon,fanart,'')
		
def livecategory(url):
	open = OPEN_URL(live_url)
	all_cats = regex_get_all(open,'<channel>','</channel>')
	for a in all_cats:
		name = regex_from_to(a,'<title>','</title>')
		name = base64.b64decode(name)
		url1  = regex_from_to(a,'<playlist_url>','</playlist_url>').replace('<![CDATA[','').replace(']]>','')
		addDir(name.replace('UK:','[COLOR blue]UK:[/COLOR]').replace('USA/CA:','[COLOR blue]USA/CA:[/COLOR]').replace('All','[COLOR blue]A[/COLOR]ll').replace('International','[COLOR blue]Int[/COLOR]ertaional').replace('Live:','[COLOR blue]Live:[/COLOR]').replace('TEST','[COLOR blue]TEST[/COLOR]').replace('Install','[COLOR blue]Install[/COLOR]').replace('24/7','[COLOR blue]24/7[/COLOR]').replace('INT:','[COLOR blue]INT:[/COLOR]').replace('DE:','[COLOR blue]DE:[/COLOR]').replace('FR:','[COLOR blue]FR:[/COLOR]').replace('PL:','[COLOR blue]PL:[/COLOR]').replace('AR:','[COLOR blue]AR:[/COLOR]').replace('LIVE:','[COLOR blue]LIVE:[/COLOR]').replace('ES:','[COLOR blue]ES:[/COLOR]').replace('IN:','[COLOR blue]IN:[/COLOR]').replace('PK:','[COLOR blue]PK:[/COLOR]'),url1,2,icon,fanart,'')
		
def Livelist(url):
	open = OPEN_URL(url)
	all_cats = regex_get_all(open,'<channel>','</channel>')
	for a in all_cats:
		name = regex_from_to(a,'<title>','</title>')
		name = base64.b64decode(name)
		xbmc.log(str(name))
		name = re.sub('\[.*?min ','-',name)
		thumb= regex_from_to(a,'<desc_image>','</desc_image>').replace('<![CDATA[','').replace(']]>','')
		url1  = regex_from_to(a,'<stream_url>','</stream_url>').replace('<![CDATA[','').replace(']]>','')
		desc = regex_from_to(a,'<description>','</description>')
		addDir(name.replace('UK:','[COLOR blue]UK:[/COLOR]').replace('USA/CA:','[COLOR blue]USA/CA:[/COLOR]').replace('All','[COLOR blue]A[/COLOR]ll').replace('International','[COLOR blue]Int[/COLOR]ertaional').replace('Live:','[COLOR blue]Live:[/COLOR]').replace('TEST','[COLOR blue]TEST[/COLOR]').replace('Install','[COLOR blue]Install[/COLOR]').replace('24/7','[COLOR blue]24/7[/COLOR]').replace('INT:','[COLOR blue]INT:[/COLOR]').replace('DE:','[COLOR blue]DE:[/COLOR]').replace('FR:','[COLOR blue]FR:[/COLOR]').replace('PL:','[COLOR blue]PL:[/COLOR]').replace('AR:','[COLOR blue]AR:[/COLOR]').replace('LIVE:','[COLOR blue]LIVE:[/COLOR]').replace('ES:','[COLOR blue]ES:[/COLOR]').replace('IN:','[COLOR blue]IN:[/COLOR]').replace('PK:','[COLOR blue]PK:[/COLOR]'),url1,4,thumb,fanart,base64.b64decode(desc))
		
	
def vod(url):
	if url =="vod":
		open = OPEN_URL(vod_url)
	else:
		open = OPEN_URL(url)
	all_cats = regex_get_all(open,'<channel>','</channel>')
	for a in all_cats:
		if '<playlist_url>' in open:
			name = regex_from_to(a,'<title>','</title>')
			url1  = regex_from_to(a,'<playlist_url>','</playlist_url>').replace('<![CDATA[','').replace(']]>','')
			addDir(str(base64.b64decode(name)).replace('?',''),url1,3,icon,fanart,'')
		else:
			if xbmcaddon.Addon().getSetting('meta') == 'true':
				try:
					name = regex_from_to(a,'<title>','</title>')
					name = base64.b64decode(name)
					num  = re.compile('^[0-9].').findall(name)
					num = str(num).replace("['","").replace("']","")
					num  = '[COLOR blue]'+num+'[/COLOR]'
					name = re.sub('^[0-9].',num,name)
					thumb= regex_from_to(a,'<desc_image>','</desc_image>').replace('<![CDATA[','').replace(']]>','')
					url  = regex_from_to(a,'<stream_url>','</stream_url>').replace('<![CDATA[','').replace(']]>','')
					desc = regex_from_to(a,'<description>','</description>')
					desc = base64.b64decode(desc)
					plot = regex_from_to(desc,'PLOT:','\n')
					cast = regex_from_to(desc,'CAST:','\n')
					ratin= regex_from_to(desc,'RATING:','\n')
					year = regex_from_to(desc,'RELEASEDATE:','\n').replace(' ','-')
					year = re.compile('-.*?-.*?-(.*?)-',re.DOTALL).findall(year)
					runt = regex_from_to(desc,'DURATION_SECS:','\n')
					genre= regex_from_to(desc,'GENRE:','\n')
					addDirMeta(str(name).replace('[/COLOR].','.[/COLOR]'),url,4,thumb,fanart,plot,str(year).replace("['","").replace("']",""),str(cast).split(),ratin,runt,genre)
				except:pass
				xbmcplugin.setContent(int(sys.argv[1]), 'movies')
			else:
				name = regex_from_to(a,'<title>','</title>')
				name = base64.b64decode(name)
				num  = re.compile('^[0-9].').findall(name)
				num = str(num).replace("['","").replace("']","")
				num  = '[COLOR blue]'+num+'[/COLOR]'
				name = re.sub('^[0-9].',num,name)
				thumb= regex_from_to(a,'<desc_image>','</desc_image>').replace('<![CDATA[','').replace(']]>','')
				url  = regex_from_to(a,'<stream_url>','</stream_url>').replace('<![CDATA[','').replace(']]>','')
				desc = regex_from_to(a,'<description>','</description>')
				addDir(name,url,4,thumb,fanart,base64.b64decode(desc))
		
def accountinfo():
	open = OPEN_URL(panel_api)
	try:
		username  = regex_from_to(open,'"username":"','"')
		password  = regex_from_to(open,'"password":"','"')
		status    = regex_from_to(open,'"status":"','"')
		connects  = regex_from_to(open,'"max_connections":"','"')
		expiry    = regex_from_to(open,'"exp_date":"','"')
		expiry    = datetime.datetime.fromtimestamp(int(expiry)).strftime('%d/%m/%Y - %H:%M')
		addDir('[COLOR blue]Username :[/COLOR] '+username,'','',icon,fanart,'')
		addDir('[COLOR blue]Password :[/COLOR] '+password,'','',icon,fanart,'')
		addDir('[COLOR blue]Expiry Date:[/COLOR] '+expiry,'','',icon,fanart,'')
		addDir('[COLOR blue]Account Status :[/COLOR] %s'%status,'','',icon,fanart,'')
		addDir('[COLOR blue]Allowed Connections:[/COLOR] '+connects,'','',icon,fanart,'')
	except:pass
	
def searchdialog():
	search = control.inputDialog(heading='Search MediaHub IPTV:')
	if search=="":
		return
	else:
		return search
	
def search():
	if mode==3:
		return False
	text = searchdialog()
	if not text:
		xbmc.executebuiltin("XBMC.Notification([COLOR red][B]Search is Empty[/B][/COLOR],Aborting search,4000,"+icon+")")
		return
	xbmc.log(str(text))
	open = OPEN_URL(panel_api)
	all_chans = regex_get_all(open,'{"num":','epg')
	for a in all_chans:
		name = regex_from_to(a,'name":"','"').replace('\/','/')
		url  = regex_from_to(a,'"stream_id":"','"')
		thumb= regex_from_to(a,'stream_icon":"','"').replace('\/','/')
		if text in name.lower():
			addDir(name.replace('UK:','[COLOR blue]UK:[/COLOR]').replace('USA/CA:','[COLOR blue]USA/CA:[/COLOR]').replace('All','[COLOR blue]A[/COLOR]ll').replace('International','[COLOR blue]Int[/COLOR]ertaional').replace('Live:','[COLOR blue]Live:[/COLOR]').replace('TEST','[COLOR blue]TEST[/COLOR]').replace('Install','[COLOR blue]Install[/COLOR]').replace('24/7','[COLOR blue]24/7[/COLOR]').replace('INT:','[COLOR blue]INT:[/COLOR]').replace('DE:','[COLOR blue]DE:[/COLOR]').replace('FR:','[COLOR blue]FR:[/COLOR]').replace('PL:','[COLOR blue]PL:[/COLOR]').replace('AR:','[COLOR blue]AR:[/COLOR]').replace('LIVE:','[COLOR blue]LIVE:[/COLOR]').replace('ES:','[COLOR blue]ES:[/COLOR]').replace('IN:','[COLOR blue]IN:[/COLOR]').replace('PK:','[COLOR blue]PK:[/COLOR]'),play_url+url+'.ts',4,thumb,fanart,'')
		elif text not in name.lower() and text in name:
			addDir(name.replace('UK:','[COLOR blue]UK:[/COLOR]').replace('USA/CA:','[COLOR blue]USA/CA:[/COLOR]').replace('All','[COLOR blue]A[/COLOR]ll').replace('International','[COLOR blue]Int[/COLOR]ertaional').replace('Live:','[COLOR blue]Live:[/COLOR]').replace('TEST','[COLOR blue]TEST[/COLOR]').replace('Install','[COLOR blue]Install[/COLOR]').replace('24/7','[COLOR blue]24/7[/COLOR]').replace('INT:','[COLOR blue]INT:[/COLOR]').replace('DE:','[COLOR blue]DE:[/COLOR]').replace('FR:','[COLOR blue]FR:[/COLOR]').replace('PL:','[COLOR blue]PL:[/COLOR]').replace('AR:','[COLOR blue]AR:[/COLOR]').replace('LIVE:','[COLOR blue]LIVE:[/COLOR]').replace('ES:','[COLOR blue]ES:[/COLOR]').replace('IN:','[COLOR blue]IN:[/COLOR]').replace('PK:','[COLOR blue]PK:[/COLOR]'),play_url+url+'.ts',4,thumb,fanart,'')
	
def userpopup():
	kb =xbmc.Keyboard ('', 'heading', True)
	kb.setHeading('Enter Username')
	kb.setHiddenInput(False)
	kb.doModal()
	if (kb.isConfirmed()):
		text = kb.getText()
		return text
	else:
		return False
		
def passpopup():
	kb =xbmc.Keyboard ('', 'heading', True)
	kb.setHeading('Enter Password')
	kb.setHiddenInput(False)
	kb.doModal()
	if (kb.isConfirmed()):
		text = kb.getText()
		return text
	else:
		return False
		
		
def stream_video(url):
	liz = xbmcgui.ListItem('', iconImage='DefaultVideo.png', thumbnailImage=icon)
	liz.setInfo(type='Video', infoLabels={'Title': '', 'Plot': ''})
	liz.setProperty('IsPlayable','true')
	liz.setPath(str(url))
	xbmcplugin.setResolvedUrl(int(sys.argv[1]), True, liz)#
	
def settingsmenu():
	if xbmcaddon.Addon().getSetting('meta')=='true':
		META = '[COLOR lime]ON[/COLOR]'
	else:
		META = '[COLOR red]OFF[/COLOR]'
	addDir('META for VOD is %s'%META,'META',10,icon,fanart,META)
	addDir('Run a Speed Test','ST',10,icon,fanart,'')
	addDir('Clear Cache','CC',10,icon,fanart,'')
	addDir('Log Out','LO',10,icon,fanart,'')
	

def addonsettings(url,description):
	if   url =="CC":
		tools.clear_cache()
	elif url =="AS":
		xbmc.executebuiltin('Addon.OpenSettings(%s)'%addon_id)
	elif url =="ST":
		xbmc.executebuiltin('Runscript("special://home/addons/plugin.video.MediaHubIPTV/resources/modules/speedtest.py")')
	elif url =="META":
		if 'ON' in description:
			xbmcaddon.Addon().setSetting('meta','false')
			xbmc.executebuiltin('Container.Refresh')
		else:
			xbmcaddon.Addon().setSetting('meta','true')
			xbmc.executebuiltin('Container.Refresh')
	elif url =="LO":
		xbmcaddon.Addon().setSetting('Username','')
		xbmcaddon.Addon().setSetting('Password','')
		xbmc.executebuiltin('XBMC.ActivateWindow(Videos,addons://sources/video/)')
		xbmc.executebuiltin('Container.Refresh')
	
def asettings():
	dialog = xbmcgui.Dialog()
	choice = dialog.yesno('MediaHub IPTV', 'Please Select The RAM Size of Your Device', yeslabel='Less than 1GB RAM', nolabel='More than 1GB RAM')
	if choice:
		lessthan()
	else:
		morethan()

			
def tvguide():
	xbmc.executebuiltin('ActivateWindow(TVGuide)')
	
def pvrsetup():
	dialog = xbmcgui.Dialog()
	choice = dialog.yesno('MediaHub IPTV', 'Would you like us to Setup the TV Guide for You?', yeslabel='Yes', nolabel='No')
	if choice:
		correctPVR()
	else:
		return
	
			
def correctPVR():

	addon = xbmcaddon.Addon('plugin.video.MediaHubIPTV')
	username_text = addon.getSetting(id='Username')
	password_text = addon.getSetting(id='Password')
	jsonSetPVR = '{"jsonrpc":"2.0", "method":"Settings.SetSettingValue", "params":{"setting":"pvrmanager.enabled", "value":true},"id":1}'
	IPTVon 	   = '{"jsonrpc":"2.0","method":"Addons.SetAddonEnabled","params":{"addonid":"pvr.iptvsimple","enabled":true},"id":1}'
	nulldemo   = '{"jsonrpc":"2.0","method":"Addons.SetAddonEnabled","params":{"addonid":"pvr.demo","enabled":false},"id":1}'
	loginurl   = "http://mediahubiptv.ddns.net:4545/get.php?username=" + username_text + "&password=" + password_text + "&type=m3u_plus&output=ts"
	EPGurl     = "http://mediahubiptv.ddns.net:4545/xmltv.php?username=" + username_text + "&password=" + password_text + "&type=m3u_plus&output=ts"

	xbmc.executeJSONRPC(jsonSetPVR)
	xbmc.executeJSONRPC(IPTVon)
	xbmc.executeJSONRPC(nulldemo)
	
	moist = xbmcaddon.Addon('pvr.iptvsimple')
	moist.setSetting(id='m3uUrl', value=loginurl)
	moist.setSetting(id='epgUrl', value=EPGurl)
	moist.setSetting(id='m3uCache', value="false")
	moist.setSetting(id='epgCache', value="false")
	xbmc.executebuiltin("Container.Refresh")
	

class Trailer:
    def __init__(self):
        self.base_link = 'http://www.youtube.com'
        self.key_link = 'QUl6YVN5QnZES3JnSU1NVmRPajZSb1pnUWhaSzRHM3MybDZXeVhn'
        self.key_link = '&key=%s' % base64.urlsafe_b64decode(self.key_link)
        self.search_link = 'https://www.googleapis.com/youtube/v3/search?part=snippet&type=video&maxResults=5&q=%s'
        self.youtube_search = 'https://www.googleapis.com/youtube/v3/search?q='
        self.youtube_watch = 'http://www.youtube.com/watch?v=%s'

    def play(self, name, url=None):
        try:
            url = self.worker(name, url)
            if url == None: return

            title = control.infoLabel('listitem.title')
            if title == '': title = control.infoLabel('listitem.label')
            icon = control.infoLabel('listitem.icon')

            item = control.item(path=url, iconImage=icon, thumbnailImage=icon)
            try: item.setArt({'icon': icon})
            except: pass
            item.setInfo(type='Video', infoLabels = {'title': title})
            control.player.play(url, item)
        except:
            pass

    def worker(self, name, url):
        try:
            if url.startswith(self.base_link):
                url = self.resolve(url)
                if url == None: raise Exception()
                return url
            elif not url.startswith('http://'):
                url = self.youtube_watch % url
                url = self.resolve(url)
                if url == None: raise Exception()
                return url
            else:
                raise Exception()
        except:
            query = name + ' trailer'
            query = self.youtube_search + query
            url = self.search(query)
            if url == None: return
            return url


    def search(self, url):
        try:
            query = urlparse.parse_qs(urlparse.urlparse(url).query)['q'][0]

            url = self.search_link % urllib.quote_plus(query) + self.key_link

            result = client.request(url)

            items = json.loads(result)['items']
            items = [(i['id']['videoId']) for i in items]

            for url in items:
                url = self.resolve(url)
                if not url is None: return url
        except:
            return


    def resolve(self, url):
        try:
            id = url.split('?v=')[-1].split('/')[-1].split('?')[0].split('&')[0]
            result = client.request('http://www.youtube.com/watch?v=%s' % id)

            message = client.parseDOM(result, 'div', attrs = {'id': 'unavailable-submessage'})
            message = ''.join(message)

            alert = client.parseDOM(result, 'div', attrs = {'id': 'watch7-notification-area'})

            if len(alert) > 0: raise Exception()
            if re.search('[a-zA-Z]', message): raise Exception()

            url = 'plugin://plugin.video.youtube/play/?video_id=%s' % id
            return url
        except:
            return
			
def trailer(url):
	xbmc.executebuiltin('ActivateWindow(busydialog)')
	Trailer().play(url) 
	xbmc.executebuiltin('Dialog.Close(busydialog)')

def regex_from_to(text, from_string, to_string, excluding=True):
	if excluding:
		try: r = re.search("(?i)" + from_string + "([\S\s]+?)" + to_string, text).group(1)
		except: r = ''
	else:
		try: r = re.search("(?i)(" + from_string + "[\S\s]+?" + to_string + ")", text).group(1)
		except: r = ''
	return r


def regex_get_all(text, start_with, end_with):
	r = re.findall("(?i)(" + start_with + "[\S\s]+?" + end_with + ")", text)
	return r


def get_params():
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


def addDir(name,url,mode,iconimage,fanart,description):
	u=sys.argv[0]+"?url="+urllib.quote_plus(url)+"&mode="+str(mode)+"&name="+urllib.quote_plus(name)+"&iconimage="+urllib.quote_plus(iconimage)+"&description="+urllib.quote_plus(description)
	ok=True
	liz=xbmcgui.ListItem(name, iconImage=iconimage, thumbnailImage=iconimage)
	liz.setInfo( type="Video", infoLabels={"Title": name,"Plot":description,})
	liz.setProperty('fanart_image', fanart)
	if mode==4:
		liz.setProperty("IsPlayable","true")
		cm = []
		cm.append(('Movie Information', 'XBMC.Action(Info)'))
		cm.append(('Play Trailer','XBMC.RunPlugin(plugin://plugin.video.MediaHubIPTV/?mode=9&url='+str(name)+')'))
		liz.addContextMenuItems(cm)
		ok=xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=u,listitem=liz,isFolder=False)
	elif mode==7 or mode==10:
		liz.setInfo( type="Video", infoLabels={"Title": name,"Plot":description})
		ok=xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=u,listitem=liz,isFolder=False)
	else:
		liz.setInfo( type="Video", infoLabels={"Title": name,"Plot":description})
		ok=xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=u,listitem=liz,isFolder=True)
	return ok
	xbmcplugin.endOfDirectory
	
def addDirMeta(name,url,mode,iconimage,fanart,description,year,cast,rating,runtime,genre):
	u=sys.argv[0]+"?url="+urllib.quote_plus(url)+"&mode="+str(mode)+"&name="+urllib.quote_plus(name)+"&iconimage="+urllib.quote_plus(iconimage)+"&description="+urllib.quote_plus(description)
	ok=True
	liz=xbmcgui.ListItem(name, iconImage=iconimage, thumbnailImage=iconimage)
	liz.setInfo( type="Video", infoLabels={"Title": name,"Plot":description,"Rating":rating,"Year":year,"Duration":runtime,"Cast":cast,"Genre":genre})
	liz.setProperty('fanart_image', fanart)
	liz.setProperty("IsPlayable","true")
	cm = []
	cm.append(('Play Trailer','XBMC.RunPlugin(plugin://plugin.video.MediaHubIPTV/?mode=9&url='+str(name)+')'))
	cm.append(('Movie Information', 'XBMC.Action(Info)'))
	liz.addContextMenuItems(cm,replaceItems=True)
	ok=xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=u,listitem=liz,isFolder=False)
	return ok
	

def OPEN_URL(url):
	headers = {}
	headers['User-Agent'] = 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/52.0.2743.116 Safari/537.36'
	link = requests.session().get(url, headers=headers, verify=False).text
	link = link.encode('ascii', 'ignore')
	return link

def morethan():
		file = open(os.path.join(advanced_settings, 'morethan.xml'))
		a = file.read()
		f = open(advanced_settings_target, mode='w+')
		f.write(a)
		f.close()
		
def lessthan():
		file = open(os.path.join(advanced_settings, 'lessthan.xml'))
		a = file.read()
		f = open(advanced_settings_target, mode='w+')
		f.write(a)
		f.close()
		
params=get_params()
url=None
name=None
mode=None
iconimage=None
description=None
query=None
type=None

try:
	url=urllib.unquote_plus(params["url"])
except:
	pass
try:
	name=urllib.unquote_plus(params["name"])
except:
	pass
try:
	iconimage=urllib.unquote_plus(params["iconimage"])
except:
	pass
try:
	mode=int(params["mode"])
except:
	pass
try:
	description=urllib.unquote_plus(params["description"])
except:
	pass
try:
	query=urllib.unquote_plus(params["query"])
except:
	pass
try:
	type=urllib.unquote_plus(params["type"])
except:
	pass

if mode==None or url==None or len(url)<1:
	start()

elif mode==1:
	livecategory(url)
	
elif mode==2:
	Livelist(url)
	
elif mode==3:
	vod(url)
	
elif mode==4:
	stream_video(url)
	
elif mode==5:
	search()
	
elif mode==6:
	accountinfo()
	
elif mode==7:
	tvguide()
	
elif mode==8:
	settingsmenu()
	
elif mode==9:
	trailer(url)
	
elif mode==10:
	addonsettings(url,description)



xbmcplugin.endOfDirectory(int(sys.argv[1]))