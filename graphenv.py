#!/usr/local/bin/python -O
import numpy as np
from collections import defaultdict
import sqlite3
from graph import Graph
from graph import Graphenv

from pandas.io import sql
from string import *
import pandas

from local_settings import CONNEXION_PATH
from local_settings import CONNEXION_PATH
import persist

from nn import Learn
cnx = CONNEXION_PATH + "mysite/databases/localdb"
data_cnx= CONNEXION_PATH + "mysite/databases/db"
import matplotlib.pyplot as plt

hash=defaultdict(lambda: defaultdict())
__author__ = 'eric'

DATASET_COLS=['datasetid', 'buildingid' ,'collection_interval', 'start_date', 'end_date',
 'timings', 'reportid', 'sensorid', 'record_count']
SENSORLIST_COLS=['sensorid', 'buildingid' ,'sensorname', 'sensortype', 'sensorfloor',
 'sensor_deviceid', 'sensor_units']


def test2():
    env = Graphenv()
    env.init()
    root = defaultdict()
    root['id']=0
    root['item'] = []
    for i,s in enumerate(env.sensorlist.values):

        add2Tree(root,str(s[0]),str(s[2]),str(s[4]),str(s[3]))
    print root

def add2Tree(tree,id,name,floor,type):

    for i, btype in enumerate(tree['item']):
        if btype['id'] == type:
            ntype = btype
            break
    else:
        ntype = defaultdict()
        ntype['text'] = type
        ntype['id'] = type
        ntype['item'] = []
        tree['item'].append(ntype)

    for i, bfloor in enumerate(ntype['item']):
        if bfloor['id'] == floor:
            nfloor = bfloor
            break
    else:
        nfloor = defaultdict()
        nfloor['text'] = floor
        nfloor['id'] = floor
        nfloor['item'] = []
        ntype['item'].append(nfloor)

    leaf = defaultdict()
    leaf['id']=id
    leaf['text']=name
    nfloor['item'].append(leaf)

def dataok(set):
    for x in set:
        if x == 0 or np.isnan(x):
            return False
    return True


def checkVav(diff):
    env = Graphenv()
    gr = Graph()
    env.init()
    l = env.getSensorsByType(u'VAV')
    pairs = list
    for it in l:
        k = it.split(':')
        if pairs.has_key(k[0]):
            p1 = pairs[k[0]]
            if k[1] == 'RM STPT DIAL':
                p2 = it
            elif k[1] == 'ROOM TEMP':
                p2 = p1
                p1 = it
            else:
                continue
            pairs[k[0]] = (p1,p2)
        else:
            if k[1] in ['RM STPT DIAL','ROOM TEMP']:            
                pairs[k[0]] = (it)   
    series = []
    for it in pairs.values():
        slist = [(it[0],env.getSensorId(it[0])),(it[1],env.getSensorId(it[1]))]
        cs = gr.getSeries(slist,'')
        ex = gr.getExpression(slist,'abs({0}-{1})',cs,False)    
        name = it[0].split(':')[0]
        dataserie = defaultdict()
        c = ex[0][1][ex[0][1]['svalue'] > diff]
        if len(c) == 0:
            continue;
        json_s = c[['stime','svalue']].to_json(orient='values')
                   
        dataserie['name']=name
        dataserie['data']=json_s
        series.append(dataserie)
    return json.dumps(series)                
    
def testgb():
    g = Graph()
    name1='JJCEX.ACS.PH.03.OAT'
    env = Graphenv()
    env.init()   
    L =[(name1,env.getSensorId(name1))]
    expr = '{0} + 1'      
    a = g.getRegular(L,'',expr)
    cs = "select(subtype = ['RM STPT DIAL','ROOM TEMP'], floor = 6, nexp = '47*',pattern ='({i} - {i+1})',cond='cmax(x,4)',maxn = 20)"
    b = g.getRequest(cs,dtfilter='x.weekday in [1,2,3,4]')
    a.extend(b)
    print a
    
def test():
    env = Graphenv()
    env.init()
    name1='JJCEX.ACS.PH.03.OAT'
    name2= 'JJCEX.ACS.PH.04.OAT'
    name3 = 'JJCEX.ACS.PH.03.COOLING.VLV'
    name4 = 'JJCEX.ACS.PH.03.STEAM.VLV.2'

    L =[(name1,env.getSensorId(name1)),\
        (name2,env.getSensorId(name2))]
    gr = Graph()



    #print a[0].head()
    expr = "{0};{1};{t}.hour"
    a = gr.getXY(L,'',expr)
    #a = gr.getPredict(L,'x.month == 7',expr,'SVM',4,30,'ada1',True)

    #b = gr.getPredict(L,'x.month == 9','','Ada Boost',4,0,'svm1',False)

    print a

    #a = gr.getCorrelations(L,expr)

    #ex = gr.getMSTF(L,expr)
    #ex = gr.getExpression(L,expr,a,True)
    #print a
    return a
def testc():
    cont = {'list':['a','b','c','d'],'graphtype':'aa','expression':'vvv','mtype':'ada','maw':10}
    persist.save_config('t1',cont)
    a = persist.load_config('t1')
    x = persist.get_config_list()
    print x

#import pluginloader as pl
#def testp():
#    foofile = open("plugins.py")
#    foo = pl.importCode(foofile,"plugins",1)
#    foo.plugtest()

if  __name__ == "__main__":
    test()