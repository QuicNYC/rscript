from django.shortcuts import get_object_or_404, render
from models import Sensor
from django import forms
from graph import Graph,upload
import json
def index(request):
    print "index"
    return  render(request, 'main.html')

def uploadpy(text):
    graph.upload(text)

def graphit(sensorname,sensorid):
    g = Graph()
    j,t = g.getMSTF(sensorname,sensorid)
    return t

def graphitDiff(n1,id1,n2,id2):
    g = Graph()
    j,t = g.getDiff(n1,id1,n2,id2)
    return t


def graph(type,h,dtfilter,req,expression,mtype,maw,pct,mname,learn):
    keys= [(n,int(x)) for n,x in h]
    g = Graph()
    j0=g.getRequest(req,dtfilter)
    if type =='Moving Std':
        print "type",type
        j = g.getMSTF(keys,dtfilter,expression)
        ctype='StockChart'
    elif type =='Time Series':
        print type,keys
        j = g.getRegular(keys,dtfilter,expression,False)
        ctype='StockChart'
    elif type =='XY':
        print type,keys
        j = g.getXY(keys,dtfilter,expression)
        ctype='scatter'
    elif type =='Correl':
        print type,keys
        j = g.getCorrelations(keys,dtfilter,expression)
        ctype='StockChart'
    elif type =='Frequencies':
        print type,keys
        j = g.getFreq(keys,dtfilter,expression)
        ctype='Histogram'
    elif type =='Learn':
        print type,keys,mtype,maw
        j = g.getPredict(keys,dtfilter,expression,mtype,maw,float(pct),mname,learn)
        ctype='StockChart'
    elif type =='Table':
        print type,keys
        j = g.getRegular(keys,dtfilter,expression,False)
        ctype='Table'        
    else:
        return {}
    if not isinstance(j, str):
        j.extend(j0)
    return json.dumps(j),ctype
