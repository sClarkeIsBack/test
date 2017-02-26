import os,sys,xbmc,shutil
import xbmc, xbmcaddon, xbmcgui, xbmcplugin, os, sys, xbmcvfs, glob, zipfile
import shutil
import urllib2,urllib
import re

ADDONTITLE     = 'MediaHub IPTV'

def speedtest():
	xbmc.executebuiltin('Runscript("special://home/addons/plugin.video.MediaHubIPTV/resources/modules/speedtest.py")')

def clear_cache():
	xbmc.log('CLEAR CACHE ACTIVATED')
	xbmc_cache_path = os.path.join(xbmc.translatePath('special://home'), 'cache')
	confirm=xbmcgui.Dialog().yesno("Please Confirm","Please Confirm You Wish To Delete Your Kodi Application Data","","","Cancel","Clear")
	if confirm:
		if os.path.exists(xbmc_cache_path)==True:
			for root, dirs, files in os.walk(xbmc_cache_path):
				file_count = 0
				file_count += len(files)
				if file_count > 0:


						for f in files:
							try:
								os.unlink(os.path.join(root, f))
							except:
								pass
						for d in dirs:
							try:
								shutil.rmtree(os.path.join(root, d))
							except:
								pass


		dialog = xbmcgui.Dialog()
		dialog.ok(ADDONTITLE, "Cache Cleared Successfully!")
		xbmc.executebuiltin("Container.Refresh()")