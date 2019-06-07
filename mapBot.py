#!/usr/bin/python3
# -*- coding: utf-8 -*-
import random
import networkx as nx
import os
from haversine import haversine
import requests
import time
import mapBot_func as pj
import gzip
import shutil
import urllib
from fuzzywuzzy import fuzz
from fuzzywuzzy import process

import telegram
from telegram.ext import Updater
from telegram.ext import CommandHandler
from telegram.ext import MessageHandler
from telegram.ext import Filters


import pandas as pd
from staticmap import StaticMap, CircleMarker, Line

wci = "worldcitiespop.csv"
poblacio = 'Population'
pais = 'Country'
ciutat = 'AccentCity'
lat = 'Latitude'
lon = 'Longitude'

G = nx.Graph()

def start(bot, update):
    bot.send_message(chat_id=update.message.chat_id, text="Hola! Envia'm la teva ubicació\nSi necessites ajuda, prem /help")

def author(bot, update):
    bot.send_message(chat_id=update.message.chat_id, text="Carles Pàmies Montero\ncarles.pamies@est.fib.upc.edu")


def help(bot, update):
    info = '''
*Comandes*

*Aquestes són les comandes que es poden usar:*

- /graph _⟨distance⟩ ⟨population⟩_  -  Crea un graf on:
nodes = ciutats del mon amb població major o igual a   ⟨population⟩
edges = distancia entre ciutats menor o igual a ⟨distance⟩
- /nodes - Escriu el nombre de nodes en el graf
- /edges - Escriu el nombre d'arestes en el graf
- /components - Escriu el nombre de components connexs en el graf
- /plotpop ⟨dist⟩ [⟨lat⟩ ⟨lon⟩] - Mostra un mapa amb totes les ciutats del graf a distància menor o igual que ⟨dist⟩ de [⟨lat⟩,⟨lon⟩]. Si no s'especifica cap ubicació, es pren la de l'usuari.  Cada ciutat es mostra amb un cercle, de radi proporcional a la seva població
- /plotgraph ⟨dist⟩ [⟨lat⟩ ⟨lon⟩] - Mostra un mapa amb totes les ciutats del graf a distància menor o igual que ⟨dist⟩ de ⟨lat⟩,⟨lon⟩ i les arestes que es connecten. Si no s'especifica cap ubicació, es pren la de l'usuari
- /route ⟨src⟩ ⟨dst⟩ - Mostra un mapa amb les arestes del camí més curt per anar entre dues ciutats ⟨src⟩ i ⟨dst⟩. La sintàxi de les ciutats és "_Nom_, _codiPaís_"

'''
    bot.send_message(chat_id=update.message.chat_id, text=info, parse_mode=telegram.ParseMode.MARKDOWN)

def ubicacio(bot, update, user_data):
    try:
        lat, lon = update.message.location.latitude, update.message.location.longitude
        ubic = (lon, lat)
        user_data['Ubicacio'] = ubic
        print('ubi')
        bot.send_message(chat_id=update.message.chat_id, text='Ubicació rebuda!')
    except Exception as e:
        print(e)
        bot.send_message(chat_id=update.message.chat_id, text='💣')


def graph(bot, update, args, user_data):
    try:
        start1 = time.time()
        if (len(args) != 2): raise Exception("args")

        if not (os.path.isfile(wci)):
            print('descarregant')
            bot.send_message(chat_id=update.message.chat_id, text='Descarregant informació necessaria...')
            url = "https://github.com/jordi-petit/lp-graphbot-2019/blob/master/dades/worldcitiespop.csv.gz?raw=true"
            urllib.request.urlretrieve (url, "worldcitiespop.csv.gz")
            with gzip.open('worldcitiespop.csv.gz', 'rb') as f_in:
                with open('worldcitiespop.csv', 'wb') as f_out:
                    shutil.copyfileobj(f_in, f_out)
            print('descarregant6')
            os.remove('worldcitiespop.csv.gz')
            bot.send_message(chat_id=update.message.chat_id, text='Descarrega completada!')

        distance = int(args[0])
        population = int(args[1])
        if (population < 50000 or distance > 10000): raise Exception('Max. distance = 10000\nMin. population = 100000')
        df = pd.read_csv(wci, usecols=[poblacio, lat, lon, ciutat])
        df_poblacio = df.loc[df[poblacio] >= population]
        print('Generant graf')
        bot.send_message(chat_id=update.message.chat_id, text="Generant graf.....")
        G = pj.graph(distance, population, df_poblacio)
        user_data['Graf'] = G
        user_data['Poblacio'] = population
        end1 = time.time()
        print(end1 - start1)
        bot.send_message(chat_id=update.message.chat_id, text='Graf generat!')
    
    except IndexError as e:
        print(e)
        bot.send_message(chat_id=update.message.chat_id, text="El format correcte es:\n/graph ⟨distance⟩ ⟨population⟩")
    except Exception as e:
        if(str(e) == 'Max. distance = 10000\nMin. population = 100000'):
            bot.send_message(chat_id=update.message.chat_id, text=str(e))
        if(str(e) == 'args'):
            bot.send_message(chat_id=update.message.chat_id, text="El format correcte es:\n/graph ⟨distance⟩ ⟨population⟩")

def plotgraph(bot, update, args, user_data):
    try:
        start1 = time.time()
        G = user_data['Graf']
        distance = float(args[0])
        if (len(args) == 3):
            ubi = (float(args[2]), float(args[1]))
        else:
            ubi = user_data['Ubicacio']
        print('Generant mapa')
        bot.send_message(chat_id=update.message.chat_id, text="Generant mapa.....")
        m = pj.plotgraph(ubi, distance, G)
        fitxer = "%d.png" % random.randint(1000000, 9999999)
        imatge = m.render()
        imatge.save(fitxer)
        bot.send_photo(chat_id=update.message.chat_id, photo=open(fitxer, 'rb'))
        os.remove(fitxer)
        end1 = time.time()
        print(end1 - start1)

    except IndexError as e:
        print(e)
        bot.send_message(chat_id=update.message.chat_id, text="El format correcte es:\n/plotgraph ⟨dist⟩ [⟨lat⟩ ⟨lon⟩]")
    except Exception as e:
        if (str(e) == "'Graf'"):
            bot.send_message(chat_id=update.message.chat_id, text="No hi ha cap graf creat")
            print(e)
        else:
            bot.send_message(chat_id=update.message.chat_id, text="Envia'm o especifica una ubicació")
            print(e)

def plotpop(bot, update, args, user_data):
    try:
        start1 = time.time()
        distance = float(args[0])
        if (len(args) == 3):
            ubi = (float(args[2]), float(args[1]))
        else:
            ubi = user_data['Ubicacio']
            
        G = user_data['Graf']

        m = pj.plotpop(ubi, distance, G)
        fitxer = "%d.png" % random.randint(1000000, 9999999)
        imatge = m.render()
        imatge.save(fitxer)
        bot.send_photo(chat_id=update.message.chat_id, photo=open(fitxer, 'rb'))
        os.remove(fitxer)
        end1 = time.time()
        print(end1 - start1)

    except IndexError as e:
        print(e)
        bot.send_message(chat_id=update.message.chat_id, text="El format correcte es:\n/plotpop ⟨dist⟩ [⟨lat⟩ ⟨lon⟩]")
    except Exception as e:
        if (str(e) == "'Graf'"):
            bot.send_message(chat_id=update.message.chat_id, text="No hi ha cap graf creat")
            print(e)
        else:
            bot.send_message(chat_id=update.message.chat_id, text="Envia'm o especifica una ubicació")
            print(e)

def route(bot, update, user_data, args):
    try:
        bot.send_message(chat_id=update.message.chat_id, text="Buscant ruta.....")
        
        ciutat_ori, ciutat_des, pais_ori, pais_des = pj.tracta_entrada(args)

        G = user_data['Graf']
        population = user_data['Poblacio']

        df = pd.read_csv(wci, usecols=[pais, ciutat, poblacio, lat, lon])
        df2 = df.loc[df[poblacio] >= population]
        df_or = df2.loc[df2[pais] == str(pais_ori)]
        df_de = df2.loc[df2[pais] == str(pais_des)]
        

        ciutat_ori = (process.extractOne(ciutat_ori, df_or[ciutat]))
        ciutat_des = (process.extractOne(ciutat_des, df_de[ciutat]))

        print(ciutat_ori[0], ciutat_des[0])
        df_ori = df_or.loc[df_or[ciutat] == str(ciutat_ori[0])]
        df_des = df_de.loc[df_de[ciutat] == str(ciutat_des[0])]
        
        ori = ((float(df_ori.iloc[0][lon]), float(df_ori.iloc[0][lat])), df_ori.iloc[0][poblacio], df_ori.iloc[0][ciutat])
        des = ((float(df_des.iloc[0][lon]), float(df_des.iloc[0][lat])), df_des.iloc[0][poblacio], df_des.iloc[0][ciutat])
        
        shortestPath = nx.shortest_path(G, source=ori, target=des, weight='dist')
        
        zippedPath = zip(shortestPath,shortestPath[1:])
        
        m = StaticMap(600, 600)
        for city, nextCity in zippedPath:
            print(city[2], nextCity[2])
            print(haversine(city[0], nextCity[0]))
            marker1 = CircleMarker(city[0], 'red', 5)
            marker2 = CircleMarker(nextCity[0], 'red', 5)
            m.add_marker(marker1)
            m.add_marker(marker2)
            m.add_line(Line((city[0], nextCity[0]), 'blue', 1))

        fitxer = "%d.png" % random.randint(1000000, 9999999)
        imatge = m.render()
        imatge.save(fitxer)
        bot.send_photo(chat_id=update.message.chat_id, photo=open(fitxer, 'rb'))
        os.remove(fitxer)

    except IndexError as e:
        print(e)
        bot.send_message(chat_id=update.message.chat_id, text='El format correcte es:\n/route ⟨src⟩ ⟨dst⟩\n\n p.ex. "Barcelona, es" "Madrid, es"')
    except Exception as e:
        print(e)
        err = str(e)
        err1 = err[-8:]
        err2 = err[:10]
        if (err1 == "not in G"):
            bot.send_message(chat_id=update.message.chat_id, text='Una o les dues ciutats no es troben al graf')
        elif (err2 == "No path to"):
            missatge = ("No s'ha trobat cap camí de %s, %s a %s, %s" % (ciutat_ori[0], pais_ori, ciutat_des[0], pais_des))
            print(missatge)
            bot.send_message(chat_id=update.message.chat_id, text=str(missatge))
        elif (str(e) == "'Graf'"):
            bot.send_message(chat_id=update.message.chat_id, text="No hi ha cap graf creat")
        elif (str(e) == "'NoneType' object is not subscriptable"):
            bot.send_message(chat_id=update.message.chat_id, text='El format correcte es:\n/route ⟨src⟩ ⟨dst⟩\n\n p.ex. "Barcelona, es" "Madrid, es"')


def nodes(bot, update, user_data):
    try:
        G = user_data['Graf']
        print("nodes:", G.number_of_nodes())
        bot.send_message(chat_id=update.message.chat_id, text=str(G.number_of_nodes()))
    except Exception as e:
        if (str(e) == "'Graf'"):
            bot.send_message(chat_id=update.message.chat_id, text="No hi ha cap graf creat")
        else:
            print(e)
            bot.send_message(chat_id=update.message.chat_id, text='💣')

def edges(bot, update, user_data):
    try:
        G = user_data['Graf']
        print("arestes:", G.number_of_edges())
        bot.send_message(chat_id=update.message.chat_id, text=str(G.number_of_edges()))
    except Exception as e:
        if (str(e) == "'Graf'"):
            bot.send_message(chat_id=update.message.chat_id, text="No hi ha cap graf creat")
        else:
            print(e)
            bot.send_message(chat_id=update.message.chat_id, text='💣')

def components(bot, update, user_data):
    try:
        print('comp')
        G = user_data['Graf']
        print("components:", nx.number_connected_components(G))
        bot.send_message(chat_id=update.message.chat_id, text=str(nx.number_connected_components(G)))
    except Exception as e:
        if (str(e) == "'Graf'"):
            bot.send_message(chat_id=update.message.chat_id, text="No hi ha cap graf creat")
        else:
            print(e)
            bot.send_message(chat_id=update.message.chat_id, text='💣')



TOKEN = open('token.txt').read().strip()
updater = Updater(token=TOKEN)
dispatcher = updater.dispatcher

dispatcher.add_handler(CommandHandler('start', start))
dispatcher.add_handler(CommandHandler('author', author))
dispatcher.add_handler(CommandHandler('help', help))
dispatcher.add_handler(MessageHandler(Filters.location, ubicacio, pass_user_data=True))
dispatcher.add_handler(CommandHandler('graph', graph, pass_args=True, pass_user_data=True))
dispatcher.add_handler(CommandHandler('nodes', nodes, pass_user_data=True))
dispatcher.add_handler(CommandHandler('edges', edges, pass_user_data=True))
dispatcher.add_handler(CommandHandler('components', components, pass_user_data=True))
dispatcher.add_handler(CommandHandler('plotgraph', plotgraph, pass_args=True, pass_user_data=True))
dispatcher.add_handler(CommandHandler('plotpop', plotpop, pass_args=True, pass_user_data=True))
dispatcher.add_handler(CommandHandler('route', route, pass_args=True, pass_user_data=True))

updater.start_polling()