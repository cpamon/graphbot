import random
import networkx as nx
import os
from haversine import haversine
import requests
import time


import telegram
from telegram.ext import Updater
from telegram.ext import CommandHandler
from telegram.ext import MessageHandler
from telegram.ext import Filters


import pandas as pd
from staticmap import StaticMap, CircleMarker, Line

def start_nodes(pob, df):
    start1 = time.time()
    print('nodes1')
    G = nx.Graph()
    print('nodes2')
    for row in df.itertuples():
        node = ((row.Longitude, row.Latitude), row.Population, row.AccentCity)
        G.add_node(node)
    return G
    end1 = time.time()
    print(end1 - start1)

def graph(d, pob, df):
    start2 = time.time()
    G = nx.Graph()
    G = start_nodes(pob, df)
    for u in G.nodes():
        for v in G.nodes():
            dist = haversine(u[0],v[0])
            if(u!=v and (dist<=d)):
                G.add_edge(u, v, weight=dist)
    return G
    end2 = time.time()
    print(end2 - start2)

def plotgraph(ubi, radi, G):
    m = StaticMap(600, 600)
    print(radi)
    print(ubi)
    for u in G.nodes():
        d = haversine(u[0],ubi)
        if(d<=radi):
            marker = CircleMarker(u[0], 'red', 5)
            m.add_marker(marker)
            for v in G.neighbors(u):
                if(haversine(v[0],ubi)<=radi):
                    m.add_line(Line((u[0], v[0]), 'blue', 1))
    return m

def plotpop(ubi, radi, G):
    m = StaticMap(600, 600)
    max_pop = 0
    for u in G.nodes():
        d = haversine(u[0],ubi)
        if(d<=radi):
            pop = u[1]
            if (pop >= max_pop):
                max_pop = pop
    for u in G.nodes():
        d = haversine(u[0],ubi)
        if(d<=radi):
            x = (float(u[1]))/max_pop
            print(x)
            x = round(x*20)
            marker = CircleMarker(u[0], 'red', x)
            m.add_marker(marker)
    return m

def tracta_entrada(args):
    a = " "
    c = a.join(args)
    c = c[1:-1]
    div = c.partition('"')
    part1 = div[0]
    part2 = div[2][2:]
    part1 = part1.partition(',')
    part2 = part2.partition(',')
    ciutat_ori = part1[0]
    pais_ori = part1[2][1:]
    ciutat_des = part2[0]
    pais_des = part2[2][1:]
    print(ciutat_ori, pais_ori)
    print(ciutat_des, pais_des)
    return ciutat_ori, ciutat_des, pais_ori, pais_des
