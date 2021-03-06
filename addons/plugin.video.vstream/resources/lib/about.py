#-*- coding: utf-8 -*-
#Venom.
from config import cConfig
   
import urllib, urllib2
import xbmc, xbmcgui, xbmcaddon
import xbmcvfs
import sys, datetime, time, os

sLibrary = xbmc.translatePath(cConfig().getAddonPath())
sys.path.append (sLibrary) 

from resources.lib.handler.requestHandler import cRequestHandler

SITE_IDENTIFIER = 'about'
SITE_NAME = 'About'


class cAbout:

    def __init__(self):
        self.main(sys.argv[1])
        #self.__sFunctionName = ''            
            
    def size(self, filepath):
        file=open(filepath)
        Content = file.read()
        file.close()

        return len(Content)
        
    
    def getUpdate(self):
        service_time = cConfig().getSetting('service_time')
        if (service_time):
            #delay mise a jour            
            time_sleep = datetime.timedelta(hours=72)
            time_now = datetime.datetime.now()
            time_service = self.__strptime(service_time, "%Y-%m-%d %H:%M:%S.%f")
            #pour test
            #time_service = time_service - datetime.timedelta(hours=50)
            if (time_now - time_service > time_sleep):
                #test les fichier pour mise a jour
                self.checkupdate()
                #Function update auto
        else:
            cConfig().setSetting('service_time', str(datetime.datetime.now()))  

        return
      

    def main(self, env):
        
        if (env == 'changelog'):
            try:
                sUrl = 'https://raw.githubusercontent.com/LordVenom/venom-xbmc-addons/master/plugin.video.vstream/changelog.txt'
                oRequest =  urllib2.Request(sUrl)
                oResponse = urllib2.urlopen(oRequest)
                sContent = oResponse.read()
                self.TextBoxes('vStream Changelog', sContent)
            except:            
                cConfig().error("%s,%s" % (cConfig().getlanguage(30205), sUrl))
            return
                
        return
     
    #bug python
    def __strptime(self, date, format):
        try:
            date = datetime.datetime.strptime(date, format)
        except TypeError:
            date = datetime.datetime(*(time.strptime(date, format)[0:6]))
        return date
     
    def __checkversion(self):
        service_version = cConfig().getSetting('service_version')
        if (service_version):          
            version = cConfig().getAddonVersion()
            if (version > service_version):
                try:
                    sUrl = 'https://raw.githubusercontent.com/LordVenom/venom-xbmc-addons/master/plugin.video.vstream/changelog.txt'
                    oRequest =  urllib2.Request(sUrl)
                    oResponse = urllib2.urlopen(oRequest)
                    sContent = oResponse.read()
                    self.TextBoxes('Changelog', sContent)
                    cConfig().setSetting('service_version', str(cConfig().getAddonVersion()))
                    return
                except:            
                    cConfig().error("%s,%s" % (cConfig().getlanguage(30205), sUrl))
                    return
        else:
            cConfig().setSetting('service_version', str(cConfig().getAddonVersion()))
            return
        

    def getRootPath(self, folder):
        sMath = cConfig().getAddonPath().replace('plugin.video.vstream', '') 
        
        sFolder = os.path.join(sMath, folder)
        # xbox hack        
        sFolder = sFolder.replace('\\', '/')
        return sFolder
    
    
    def resultGit(self):
        try:    import json
        except: import simplejson as json
        
        try: 
            sUrl = 'https://raw.githubusercontent.com/LordVenom/venom-xbmc-addons/master/sites.json'
            oRequestHandler = cRequestHandler(sUrl)
            sHtmlContent = oRequestHandler.request();
            result = json.loads(sHtmlContent)
            
            sUrl = 'https://raw.githubusercontent.com/LordVenom/venom-xbmc-addons/master/hosts.json'
            oRequestHandler = cRequestHandler(sUrl)
            sHtmlContent = oRequestHandler.request();
            result += json.loads(sHtmlContent)
        except:
            return False
        return result
    
    
    def checkupdate(self):
            
            service_time = cConfig().getSetting('service_time')            
            
            #dialog = cConfig().showInfo("vStream", "Cherche les mises a jour")
            
            result = self.resultGit()
           
            sDown = 0
            
            if result:
            
                for i in result:
                    
                    try: 
                        rootpath = self.getRootPath(i['path'])
                        
                        if (self.size(rootpath) != i['size']):
                            #print i['name']
                            #print self.size(rootpath)
                            #print i['size']
                            sDown = sDown+1
                            break #Si on en trouve un, pas besoin de tester les autres.
                            
                    except:
                        pass
                 
                if (sDown != 0):
                    cConfig().setSetting('home_update', str('true')) 
                    cConfig().setSetting('service_time', str(datetime.datetime.now()))
                    dialog = cConfig().showInfo("vStream", "Mise à jour disponible")   
                else:
                    #cConfig().showInfo('vStream', 'Fichier a jour')
                    cConfig().setSetting('service_time', str(datetime.datetime.now()))
                    cConfig().setSetting('home_update', str('false'))
                
            return
    
    def checkdownload(self):

            result = self.resultGit()
            total = len(result)
            dialog = cConfig().createDialog('Update')
            site = []
            sdown = 0

            if result: 
                
                for i in result:
                    cConfig().updateDialog(dialog, total)
                   
                    try:
                        rootpath = self.getRootPath(i['path'])
                        
                        if (self.size(rootpath) != i['size']):
                            try:
                                self.__download(i['download_url'], rootpath)
                                site.append("[COLOR green]"+i['name'].encode("utf-8")+"[/COLOR]")
                                sdown = sdown+1
                            except:
                                site.append("[COLOR red]"+i['name'].encode("utf-8")+"[/COLOR]")
                                sdown = sdown+1
                                pass
                    except:
                        pass
                 
                cConfig().finishDialog(dialog)
                sContent = "Fichier mise à jour %s / %s \n %s" %  (sdown, total, site)
                #self.TextBoxes('vStream mise à Jour', sContent)
                cConfig().setSetting('service_time', str(datetime.datetime.now()))
                cConfig().setSetting('home_update', str('false'))
                fin = cConfig().createDialogOK(sContent)
                cConfig().update()
            return
            
    def __download(self, WebUrl, RootUrl):
        try:
            inf = urllib.urlopen(WebUrl)
            f = xbmcvfs.File(RootUrl, 'w')
            #save it
            line = inf.read()         
            f.write(line)
            
            inf.close()
            f.close()
        except:
            pass
        return
        
            
        
    def TextBoxes(self, heading, anounce):
        class TextBox():
            # constants
            WINDOW = 10147
            CONTROL_LABEL = 1
            CONTROL_TEXTBOX = 5

            def __init__( self, *args, **kwargs):
                # activate the text viewer window
                xbmc.executebuiltin( "ActivateWindow(%d)" % ( self.WINDOW, ) )
                # get window
                self.win = xbmcgui.Window( self.WINDOW )
                # give window time to initialize
                xbmc.sleep( 500 )
                self.setControls()

            def setControls( self ):
                # set heading
                self.win.getControl( self.CONTROL_LABEL ).setLabel(heading)
                try:
                    f = open(anounce)
                    text = f.read()
                except: text=anounce
                self.win.getControl( self.CONTROL_TEXTBOX ).setText(text)
                return
        TextBox()

cAbout()
