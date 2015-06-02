import json
from django.core import serializers
from dajaxice.decorators import dajaxice_register
from models import Floor
from models import Sensor
from collections import defaultdict
from views import graph,upload

import persist

@dajaxice_register
def getConfList(request,select = ''):
    cat,json_list = persist.get_config_list(),[]
    for f in cat:
        d = defaultdict()
        d['id']='0'
        d['name']=f
        json_list.append(d)
    arg = 0
    json_list.sort(key=lambda t: t['name'],reverse=False)
    for i, x in enumerate(json_list):
        x['id']=str(i)
        if select == x['name']:
            arg = i
    return json.dumps({'arg': arg,'message': json_list})

@dajaxice_register
def saveConf(request,name,lists,graphtype,dtfilter,expression,expressionl,mtype,maw,pct,req):
    sensorlist = []

    for x in lists:
        sensor = Sensor.objects.filter(sensorid=x).values()[0]
        sensorlist.append((sensor['sensorname'],sensor['sensorid']))

    cont = {'id':name,'list':sensorlist,'graphtype':graphtype,\
            'dtfilter':dtfilter,'expression':expression,'expressionl':expressionl,'mtype':mtype,'maw':maw,\
            'pct':pct,'req':req
        }

    cat,json_list = persist.save_config(name,cont),[]
    retmessage = getConfList(request,name)
    print retmessage
    #retmessage['message']['id'] = name
    return retmessage

@dajaxice_register
def getConf(request,name):
    cont = persist.load_config(name)
    return json.dumps({ 'message': cont})

@dajaxice_register
def getFloorList(request):
    l = Floor.objects.all()
    json_list=[]
    for i,f in enumerate(l,1) :
        d = defaultdict()
        d['id']=str(i)
        d['name']=str(f)
        json_list.append(d)
    return json.dumps({ 'message': json_list})

@dajaxice_register
def uploadPython(request,text):
    if request.is_ajax() and request.method == 'POST':
        upload(text)


@dajaxice_register
def getSensorList(request,text):
    if request.is_ajax() and request.method == 'POST':
        return json.dumps({'message': sensor_list(text)})

@dajaxice_register
def getGraph(request,lists,graphtype,dtfilter,req,expression,mtype,maw,pct,mname,learn):
    sensorlist = []
    for x in lists:
        sensor = Sensor.objects.filter(sensorid=x).values()[0]
        sensorlist.append((sensor['sensorname'],sensor['sensorid']))
    series,arg = graph(graphtype,sensorlist,dtfilter,req,expression,mtype,maw,pct,mname,learn)
    return json.dumps({'arg': arg,'message': series})

@dajaxice_register
def getSensorTree(request):
    root = defaultdict()
    root['id']=0
    root['item'] = []
    types = ['CAV','AHU']
    i=0
    for s in Sensor.objects.all().values():
        add2Tree(root,s['sensorid'],s['sensorname'],s['sensorfloor'],s['sensortype'])
        i+=1
    js = json.dumps({'message': root})
    return js

def add2Tree(tree,id,name,floor,type):
    type = 'Type-'+type
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
    floor = 'Floor-' + floor
    floorid = type + floor
    for i, bfloor in enumerate(ntype['item']):
        if bfloor['id'] == floorid:
            nfloor = bfloor
            break
    else:
        nfloor = defaultdict()
        nfloor['text'] = floor
        nfloor['id'] = floorid
        nfloor['item'] = []
        ntype['item'].append(nfloor)

    leaf = defaultdict()
    leaf['id']= str(id) + '-' + name
    leaf['text']= '.'.join(name.split('.')[3:])
    nfloor['item'].append(leaf)



def sensor_list(floor):
    sensors = Sensor.objects.filter(sensorfloor=floor).values()
    json_list=[]
    for s in  sensors:
        d = defaultdict()
        d['id']= s['sensorid']
        d['name']=s['sensorname']
        json_list.append(d)
    json_list.sort(key=lambda t: t['name'])
    return json_list