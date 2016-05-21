﻿# -*- coding: utf-8 -*-#------------------------------------------------------------# pelisalacarta - XBMC Plugin# Canal para http://www.conectate.gov.ar# creado por rsantaella# http://blog.tvalacarta.info/plugin-xbmc/pelisalacarta/#------------------------------------------------------------import urlparse,urllib2,urllib,reimport os, sysfrom core import loggerfrom core import configfrom core import scrapertoolsfrom core.item import Itemfrom servers import servertools__channel__ = "conectate"__category__ = "F"__type__ = "generic"__title__ = "conectate"__language__ = "ES"__creationdate__ = "20121130"DEBUG = config.get_setting("debug")def isGeneric():    return Truedef mainlist(item):    logger.info("tvalacarta.channels.conectate mainlist")       itemlist = []    itemlist.append( Item(channel=__channel__, title="Encuentro", action="secciones", url="http://www.conectate.gob.ar/sitios/conectate/busqueda/encuentro"))     itemlist.append( Item(channel=__channel__, title="Pakapaka", action="secciones", url="http://www.conectate.gob.ar/sitios/conectate/busqueda/pakapaka"))     itemlist.append( Item(channel=__channel__, title="DEPORTV", action="secciones", url="http://www.conectate.gob.ar/sitios/conectate/busqueda/deportv"))    itemlist.append( Item(channel=__channel__, title="Educ.ar", action="secciones", url="http://www.conectate.gob.ar/sitios/conectate/busqueda/educar"))    itemlist.append( Item(channel=__channel__, title="Conectar igualdad", action="secciones", url="http://www.conectate.gob.ar/sitios/conectate/busqueda/conectar"))    return itemlistdef secciones(item):    logger.info("tvalacarta.channels.secciones mainlist")       itemlist = []    headers = []    headers.append(["Accept","text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8"])    headers.append(["Accept-Encoding","gzip,deflate"])    headers.append(["Accept-Language","es-ES,es;q=0.8,en;q=0.6"])    headers.append(["Connection","keep-alive"])    headers.append(["User-Agent","Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/33.0.1750.152 Safari/537.36"])    reintentos = 5    while reintentos>0:        data = scrapertools.cache_page(item.url,headers=headers,timeout=5)        if data!="":            break        logger.info("tvalacarta.channels.conectate.secciones Respuesta vacia, reintentando")            reintentos = reintentos - 1    logger.info("data="+data)    bloque = scrapertools.find_single_match(data,'<h2 class="audible">Secciones</h2>(.*?)</ul>')    logger.info("bloque="+bloque)    patron = '<li class="menu-item[^<]+<a class="Menu-link" href="([^"]+)">([^<]+)</a>'    matches = re.compile(patron,re.DOTALL).findall(bloque)    for scrapedurl,scrapedtitle in matches:        url = urlparse.urljoin(item.url,scrapedurl)        thumbnail = ""        title = scrapedtitle.strip()        plot = ""        itemlist.append( Item(channel=__channel__, action="programas", title=title , url=url , thumbnail=thumbnail , fanart=thumbnail,  plot=plot , viewmode="movie_with_plot", folder=True) )    return itemlistdef programas(item, load_all_pages=False):    logger.info("tvalacarta.channels.conectate programas")    #print "      "+item.url    # Descarga la pagina    headers = []    headers.append(["Accept","text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8"])    headers.append(["Accept-Encoding","gzip,deflate"])    headers.append(["Accept-Language","es-ES,es;q=0.8,en;q=0.6"])    headers.append(["Connection","keep-alive"])    headers.append(["Referer",item.url])    headers.append(["User-Agent","Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/33.0.1750.152 Safari/537.36"])    reintentos = 5    while reintentos>0:        #print "      leyendo"        data = scrapertools.cache_page(item.url,headers=headers,timeout=5)        patron  = '<li class="col-xs-3"[^<]+'        patron += '<div class="card"[^<]+'        patron += '<a href="([^"]+)"[^<]+'        patron += '<img class="" height="\d+" width="\d+" src="([^"]+)"/[^<]+'        patron += '<h5>([^<]+)</h5[^<]+'        patron += '</a[^<]+'        patron += '<p>([^<]+)</p'        matches = re.compile(patron,re.DOTALL).findall(data)        itemlist = []        for scrapedurl,scrapedthumbnail,scrapedtitle,scrapedplot in matches:            url = urlparse.urljoin(item.url,scrapedurl)            thumbnail = urlparse.urljoin(item.url,scrapedthumbnail)            title = scrapedtitle            plot = scrapedplot            if (item.title == "Película") or (item.title == "Especial"):                itemlist.append( Item(channel=__channel__, action="play", server="conectate", title=title , url=url , thumbnail=thumbnail , fanart=thumbnail,  plot=plot , viewmode="movie_with_plot", folder=False) )            else:                itemlist.append( Item(channel=__channel__, action="episodios", title=title , url=url , thumbnail=thumbnail , fanart=thumbnail,  plot=plot , show=title, viewmode="movie_with_plot", folder=True) )        if len(itemlist)>0:            break        else:            logger.info("tvalacarta.channels.conectate.capitulos Respuesta vacia, reintentando")            #print "      reintentando"            reintentos = reintentos - 1            import time            time.sleep(2)    #http://www.conectate.gob.ar/sitios/conectate/busqueda/encuentro?rec_tipo_funcional_id=11&amp;limit=12&amp;offset=12    next_page_url = scrapertools.find_single_match(data,'<a class="menu-link" id="nextPage" class="siguiente" href="([^"]+)"[^>]+>Siguiente</a>')    if next_page_url!="":        next_page_url = urlparse.urljoin(item.url,next_page_url.replace("&amp;","&"))        logger.info("next_page_url="+next_page_url)        try:            current_offset = scrapertools.find_single_match(item.url,"offset\=(\d+)")            if current_offset=="":                current_offset=0            next_offset = scrapertools.find_single_match(next_page_url,"offset\=(\d+)")            if int(next_offset) > int(current_offset):                next_page_item = Item(channel=__channel__, action="programas", title=">> Página siguiente" , url=next_page_url )                if load_all_pages:                    itemlist.extend(programas(next_page_item,load_all_pages))                else:                    itemlist.append(next_page_item)        except:            import traceback            logger.info(traceback.format_exc())            #print traceback.format_exc()    return itemlist	def episodios(item):    logger.info("tvalacarta.channels.conectate episodios")        itemlist = []    # Descarga la pagina    headers = []    headers.append(["Accept","text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8"])    headers.append(["Accept-Encoding","gzip,deflate"])    headers.append(["Accept-Language","es-ES,es;q=0.8,en;q=0.6"])    headers.append(["Connection","keep-alive"])    headers.append(["Referer",item.url])    headers.append(["User-Agent","Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/33.0.1750.152 Safari/537.36"])    reintentos = 2    while reintentos>0:        data = scrapertools.cachePage(item.url,headers=headers,timeout=5)        patron_bloque = '<li class="temporada"[^<]+<a href="." class="temporada-titulo">([^<]+)</a[^<]+<ul(.*?)</ul>'        matches_bloques = re.compile(patron_bloque,re.DOTALL).findall(data)        for temporada,bloque in matches_bloques:            logger.info("temporada="+temporada+", bloque="+bloque)            patron = '<li>[^<]+<a href="([^"]+)"[^>]+>(.*?)</a>'            matches = re.compile(patron,re.DOTALL).findall(bloque)            for scrapedurl,scrapedtitle in matches:                logger.info("url="+scrapedurl+", title="+scrapedtitle)                    url = scrapedurl                title = re.compile('<span class="AD">[^<]+</span>',re.DOTALL).sub("",scrapedtitle)                title = re.compile('<span class="CC">[^<]+</span>',re.DOTALL).sub("",title)                title = scrapertools.htmlclean(title).strip()                title = temporada.strip() + " - " + title.strip()                itemlist.append( Item(channel=__channel__, action="play", server="conectate", title=title , url=url , show=item.show, folder=False) )        if len(itemlist)>0:            break        else:            logger.info("tvalacarta.channels.conectate.capitulos Respuesta vacia, reintentando")            #print "      reintentando"            reintentos = reintentos - 1            import time            time.sleep(2)    if len(itemlist)==0:        itemlist.append( Item(channel=__channel__, action="play", server="conectate", title="Ver este vídeo" , url=item.url ,  folder=False) )    return itemlistdef detalle_episodio(item):    data = scrapertools.cache_page(item.url)    scrapedplot = scrapertools.find_single_match(data,'<meta property="og:description" content="([^"]+)"')    item.plot = scrapertools.htmlclean( scrapedplot ).strip()    #24\/08\/2015    scrapeddate = scrapertools.find_single_match(data,'"fecha_creacion"\:"([^"]+)"')    if scrapeddate=="":        scrapeddate = scrapertools.find_single_match(data,'"fecha"\:"([^"]+)"')    item.aired_date = scrapertools.parse_date(scrapeddate.replace("\\/","/"))    scrapedduration = scrapertools.find_single_match(data,'"duracion_segundos":"(\d+)"')    item.duration = scrapertools.parse_duration_secs(scrapedduration)    item.geolocked = "0"        try:        from servers import conectate as servermodule        video_urls = servermodule.get_video_url(item.url,page_data=data)        item.media_url = video_urls[-1][1]    except:        import traceback        print traceback.format_exc()        item.media_url = ""    return itemdef play(item):    item.server="conectate"    itemlist = [item]    return itemlist# Verificación automática de canales: Esta función debe devolver "True" si todo está ok en el canal.def test():        # El canal tiene estructura programas -> episodios -> play    items = mainlist(Item())    items_secciones = secciones(items[0])    for item_seccion in items_secciones:        if item_seccion.title=="Serie":            items_programas = programas(item_seccion)            if len(items_programas)==0:                print "No hay programas en "+items_secciones[0].tostring()                return False            items_episodios = episodios(items_programas[0])            if len(items_episodios)==0:                print "No hay episodios en "+items_programas[0].tostring()                return False            break    return True