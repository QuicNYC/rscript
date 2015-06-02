__author__ = 'eric'
from collections import defaultdict
import sqlite3
import json
#import gviz_api
from string import Formatter
from pandas.io import sql
from pandas import date_range
from sklearn.linear_model import LinearRegression
from operator import itemgetter
import pandas
#import numexpr
import local_settings
import math
import numpy
import random
from itertools import izip
from local_settings import CONNEXION_PATH
import nn
from nn import Learn
from nn import Run
import pluginloader
import fnmatch
modelcnx = CONNEXION_PATH + "/databases/localdb"
data_cnx= CONNEXION_PATH + "/databases/db"
TIMEAXIS='{t}'
from string import Template

P = pluginloader.reload()

def upload(text):
    global P
    P = pluginloader.upload(text)

def isweekday(stime):
    return  pandas.to_datetime(stime).apply(lambda x: x.weekday()) <5
def isweekend(stime):
    return  pandas.to_datetime(stime).apply(lambda x: x.weekday()) >= 5

def cmax(s,v):
    return 0 if s < v else s

def cmin(s,v):
    return 0 if s > v else s

class Graphenv(object):
    def init(self):
        cx = sqlite3.connect(modelcnx)
        self.sensorlist=sql.read_frame('select * from building_sensor',cx)
        cx.close()
    def existsData(self,sensorid):
        global  data_cnx
        cx = sqlite3.connect(data_cnx)
        e = sql.table_exists('sensor_'+  str(sensorid),cx,'sqlite')
        cx.close()
        return e

    def getSensorId(self,name):
        cols = self.sensorlist['sensorname']
        return int(self.sensorlist[cols == name].sensorid)

    def getSensorData(self,id,force=False):
        global  data_cnx
        cx = sqlite3.connect(data_cnx)
        val=None
        #todo: update tables
        if self.existsData(id):
            return sql.read_frame('select * from sensor_'+str(id),cx)
        else:
            return None
    def getSensorsByType(self,t):
        types = self.sensorlist['sensortype']
        s = self.sensorlist[types == t].sensorname 
        return list(s)

class Graph(object):
    def _genv(self):
        return Graphenv()
    def existData(self,sensorid):
        global data_cnx
        cnx = sqlite3.connect(data_cnx)
        e = sql.table_exists  ('sensor_'+  str(id),con=cnx)
        cnx.close()
        return e

    def getSensorData(self,id,dtfilter=None):
        global data_cnx
        cnx = sqlite3.connect(data_cnx)
        data = sql.read_frame('select * from sensor_'+  str(id) + ' order by stime asc',con=cnx)
        cnx.close() 
        sdata = data[['stime','svalue']]
       
        sdata['stime'] = pandas.to_datetime(data['stime'])
        if dtfilter is not None and dtfilter != '':
            criterion = sdata.stime.map(lambda x : eval(dtfilter))
            sdata = sdata[criterion]
        sdata.index=sdata['stime']
        return sdata
    
    def getSensorUnits(self,sensorlist):
        ret = []
        cnx = sqlite3.connect(modelcnx)
        for name in sensorlist:
            d = sql.read_frame('select * from building_sensor where sensorname="%s"'%name, con=cnx)
            ret.append(d['sensor_units'][0])
        
        cnx.close()            
        return ret   
            
            
    def getMSTF(self, sensorlist,dtfilter, expression):
        cs = self.getSeries(sensorlist,dtfilter)
        ex = self.getExpression(sensorlist,expression,cs)
        series=[]

        for name ,data in ex:
            data.index = pandas.to_datetime(data.pop('stime'))
            json_s = self.computeMSTF(data)

            dataserie = defaultdict()
            dataserie['name']=name
            dataserie['data']=json_s
            series.append(dataserie)

            dataserie = defaultdict()
            dataserie['name']=name + ' MA'
            dataserie['data']=data[['stime','MA']].to_json(orient='values')
            series.append(dataserie)

            dataserie = defaultdict()
            dataserie['name']=name + ' 2STD'
            dataserie['data']=data[['stime','std2']].to_json(orient='values')
            series.append(dataserie)

            dataserie = defaultdict()
            dataserie['name']=name + ' -2STD'
            dataserie['data']=data[['stime','std_2']].to_json(orient='values')
            series.append(dataserie)

        return series

    def computeMSTF(self,data):

        mean = pandas.rolling_mean(data.values,window=20)
        st = pandas.rolling_std(data.values,window=20)

        data['MA'] = mean
        data['std2'] = mean + 2*st
        data['std_2'] = mean - 2*st
        data['stime'] = data.index

        json_s = data[['stime','svalue']].to_json(orient='values')
        return json_s

    def computeCorrelations(self,data1,data2):

        correl = pandas.rolling_corr(data1,data2,window=20)
        data2['CORR'] = correl
        data2['stime'] = data2.index
        json_s = data2[['stime','svalue']].to_json(orient='values')
        return json_s

    def getMSTF(self, sensorlist,dtfilter, expression):
        cs = self.getSeries(sensorlist,dtfilter)
        ex = self.getExpression(sensorlist,expression,cs)
        series=[]
        yaxis,keys,unitlist = self.buildYAxis(sensorlist,[n[0] for n in ex])
        for i,(name ,data) in enumerate(ex):
            u = unitlist[i]
                              
            data.index = pandas.to_datetime(data.pop('stime'))
            json_s = self.computeMSTF(data)

            dataserie = defaultdict()
            dataserie['name']=name
            dataserie['data']=json_s
            dataserie['yAxis']=keys[u] 
            series.append(dataserie)

            dataserie = defaultdict()
            dataserie['name']=name + ' MA'
            dataserie['data']=data[['stime','MA']].to_json(orient='values')
            dataserie['yAxis']=keys[u] 
            series.append(dataserie)

            dataserie = defaultdict()
            dataserie['name']=name + ' 2STD'
            dataserie['data']=data[['stime','std2']].to_json(orient='values')
            dataserie['yAxis']=keys[u] 
            series.append(dataserie)

            dataserie = defaultdict()
            dataserie['name']=name + ' -2STD'
            dataserie['data']=data[['stime','std_2']].to_json(orient='values')
            dataserie['yAxis']=keys[u] 
            series.append(dataserie)

        return series,yaxis

    def getCorrelations(self, sensorlist,dtfilter, expression):
        cs = self.getSeries(sensorlist,dtfilter)
        ex = self.getExpression(sensorlist,expression,cs)
        series=[]
        datar = ex[0][1]
        nr = ex[0][0]
        datar.index = pandas.to_datetime(ex[0][1].pop('stime'))
        yaxis,keys,unitlist = self.buildYAxis(sensorlist,[n[0] for n in ex])
        for i,(name ,data) in enumerate(ex[1:]):
            data.index = pandas.to_datetime(data.pop('stime'))
            json_s = self.computeCorrelations(datar,data)

            #dataserie = defaultdict()
            #dataserie['name']=name
            #dataserie['data']=json_s
            #series.append(dataserie)

            dataserie = defaultdict()
            dataserie['name']= nr + ' CORR ' + name
            dataserie['data']=data[['stime','CORR']].to_json(orient='values')
            u = unitlist[i]
            dataserie['yAxis']=keys[u]            
            series.append(dataserie)

        return series,yaxis

    def tryit(self,x):
        return x > 20

    def getExpression(self,sensorlist,expression,series,xy=False,ignore_time=True):
        if series == []:
            return []
        pdata = series[0].rename(columns={'svalue': 'svalue0'})
        if xy:
            l = max(len(pdata),1000)
            l = min(l,1000)
            step = max(len(pdata)/l,1)
            rows = range(0,len(pdata),step)
            pdata = pdata.ix[rows]
        for i, frame in enumerate(series[1:], 1):
            pdata = pdata.merge(frame, on='stime',how='inner',sort=True).rename(
                columns={'svalue': 'svalue%d' % i}).drop_duplicates()

        indexcol='stime'
        if xy:
            pdata.index = pdata['svalue0']
            pdata.drop('stime',1)
            indexcol='svalue0'
            startindex=1
        else:
            pdata.index=pdata['stime']
            startindex=0


        results = []
        exprarray = expression.split(';') if expression != '' else []
        exprwithoutt  = ''
        expr , exprt = [],[]
        for x in exprarray:
            if TIMEAXIS not in x:
                expr.append(x)
            elif not ignore_time:
                exprt.append(x.replace(TIMEAXIS,'pdata.index'))
        if expr == []:
            expr = [('{%d}')%(i) for i in range(0,len(sensorlist)-startindex)]

        expression = ','.join(expr + exprt)
        labelexpression = ';'.join(expr + exprt)
        a = eval(expression.format(* [ ('pdata.svalue%d')%(i) for i in range(startindex,len(sensorlist))]))

        labels = labelexpression.format(*[sensorlist[i][0] for i in range(startindex,len(sensorlist))]).split(';')
        for i,d in enumerate([a] if not isinstance(a,tuple) else a,0):
            pc = pandas.DataFrame(d)
            pc.columns = ['svalue']
            pc[indexcol] = pc.index
            results.append((labels[i],pc))
        return results

    def getSeries(self,sensorlist,dtfilter):
        series =[]
        filters = dtfilter.split(';\n')
        dtfilter = None if len(filters) == 0 else filters[0]
        for i,(name,id) in enumerate(sensorlist):
            pdata = self.getSensorData(id,dtfilter)
            if i < len(filters[1:]) and filters[i+1] != '':
                pdata = pdata[pdata.svalue.map(lambda x: eval(filters[i+1]))]
            series.append(pdata)
        return series

    def getMergedData(self,sensorlist,dtfilter,expression,xy=False,ignore_time=True):
        series=[]
        cs = self.getSeries(sensorlist,dtfilter)
        if cs == []:
            return []
        ex = self.getExpression(sensorlist,expression,cs,xy,ignore_time)
        return ex


    def buildYAxis(self,sensorlist,ex):
        slist = []
        for (name,id) in sensorlist:
            for e in ex:
                if name in e :
                    slist.append(name)
    
        unitlist = self.getSensorUnits(slist)        
        
        yax = []
        keys = defaultdict()
        c = 0
        for u in unitlist:
            if u not in keys.keys():
                y = { \
                    'minorTickInterval': 'auto',\
                    'lineWidth': 3,'tickWidth': 1,\
                    'gridLineWidth': 0,\
                    'title':\
                        {\
                            'text':'%s'%u,\
                            'font': '9px Trebuchet MS, Verdana, sans-serif',\
                        },\
                'opposite': c%2==0,
				'labels':
					{
						'format':'{value}'\
					}\
				};
                yax.append(y)
                keys[u]=c
                c += 1
        return yax,keys,unitlist
    
    def getRegular(self,sensorlist,dtfilter,expression,xy=False):

        series=[]
        cs = self.getSeries(sensorlist,dtfilter)
        ex = self.getExpression(sensorlist,expression,cs,xy)
       
        yaxis,keys,unitlist = self.buildYAxis(sensorlist,[n[0] for n in ex])
        for i, (name ,c) in enumerate(ex):
            #print c.head()
            dataserie = defaultdict()
            if not xy:
                json_s = c[['stime','svalue']].to_json(orient='values')
            else:
                json_s = c[['svalue0','svalue']].to_json(orient='values')
            dataserie['name']=name
            u = unitlist[i]
            dataserie['data']=json_s
            dataserie['yAxis']=keys[u]
            #dataserie['step']=True
            series.append(dataserie)
        return series,yaxis

    def getFreq(self,sensorlist,dtfilter,expression):
        series=[]
        cs = self.getSeries(sensorlist,dtfilter)
        ex = self.getExpression(sensorlist,expression,cs,False)
        for name ,c in ex:
            c = c.fillna(0)
            dataserie, rawhist = defaultdict(),numpy.histogram(c['svalue'],bins=20)
            json_s = pandas.DataFrame(rawhist[0]).to_json(orient='values')
            dataserie['name']=name
            dataserie['data']=json_s
            cat = rawhist[1].tolist()
            bins = ["%.1f-%.1f"%(l1,l2) for l1,l2 in izip(cat[:-1],cat[1:])]
            dataserie['bins']=bins
            series.append(dataserie)
            break

        return series

    def getXY(self,sensorlist,dtfilter,expression):
        series=[]
        cs = self.getSeries(sensorlist,dtfilter)
        exps = self.getExpression(sensorlist,expression,cs,False)
        labels = [(n[0],) for n in exps]
        tables = [n[1] for n in exps]
        eXY = self.getExpression(labels,'',tables,True)
        
        for name ,c in eXY:
            dataserie = defaultdict()
            x = c[['svalue0']]
            y = c[['svalue']]
            c.fillna(0,inplace='True')
            lr = LinearRegression()
            lr.fit(x,y)
            p1 = lr.predict(x.min())
            p2 = lr.predict(x.max())
            d = [[x.min()[0],p1[0]],[x.max()[0],p2[0]]]
            linereg = defaultdict()
            linereg['type']='line'
            linereg['data'] = json.dumps(d)
            linereg['name'] = 'Regression Line'
            linereg['marker'] = {'enabled' : 'False'}
            linereg['states'] = {'hover' : {'lineWidth':0}}
            json_s = c[['svalue0','svalue']].to_json(orient='values')
            dataserie['name']=name
            dataserie['data']=json_s
            dataserie['type']='scatter'
            dataserie['marker'] = {'radius' : 1}
            
            series.append(dataserie)
            series.append(linereg)

        return series

    def getPredict(self,sensorlist,dtfilter,expression,mtype,maw,pct,mname,learn):
        win = int(maw)
        a = self.getMergedData(sensorlist,dtfilter,expression,ignore_time=False)
        series = []
        means = []
        for t in a[0:]:
            t[1].fillna(0)
            t[1].index = pandas.to_datetime(t[1].pop('stime'))
            t[1]['stime']=t[1].index
            m = pandas.rolling_mean(t[1]['svalue'].values,window=win)
            for x in range(0,win):
                m[x]=m[win]
            means.append(m)

        loutput = len(means[0])-1

        inp = None
        outp = None
        for i in range(0,loutput):
            ielem = []
            for j in range(1,len(a)):
                ielem.append(means[j][i])
            oelem = [means[0][i+1]]
            if inp is None:
                inp = numpy.array([ielem])
            else:
                inp = numpy.vstack([inp,ielem])
            if outp is None:
                outp = numpy.array(oelem)
            else:
                outp = numpy.append(outp,oelem)
    #       ds.addSample(inp,outp)
        if learn:
            fore  =  Learn(inp,outp,mtype,pct,mname)
        else:
            fore = Run(inp,mname)
        pr = pandas.DataFrame(a[0][1])

        pr['svalue']=means[0].tolist()
        fore = numpy.insert(fore,0,a[0][1]['svalue'][0])
        pr['predict'] = fore.tolist()

        print pr.head(1)
        dataserie = defaultdict()
        json_s = pr[['stime','svalue']].to_json(orient='values')
        dataserie['name']=a[0][0]
        dataserie['data']=json_s
        series.append(dataserie)

        dataserie = defaultdict()
        json_s = pr[['stime','predict']].to_json(orient='values')
        dataserie['name']=a[0][0] + '_forecast'
        dataserie['data']=json_s
        series.append(dataserie)
        return series




    #special scripts
    def getRequest(self,request,dtfilter):
        if request == '' or request is None or request == 'undefined':
            return []
        rr = 'self.' + request[:-1] + ',dtfilter = ' + "'" + dtfilter + "')"
        return eval(rr)

    def select(self,type='VAV',subtype = ['RM STPT DIAL','ROOM TEMP'], floor = 0,nexp='', pattern ='{i}',cond = 'cmax(x,7)',maxn = 10, dtfilter = ''):
        env = self._genv()       
        env.init()
        l = env.getSensorsByType(type)
        lname = []

        for it in l:
            k = it.split(':')
            if floor != 0:
                fl = int(k[0].split('.')[1])
                if fl != floor:
                    continue

                if nexp != '':
                    sname = k[0].split('.')[3]
                    if not fnmatch.fnmatch(sname,nexp):
                        continue    

                if k[1] in subtype:
                    lname.append((it,env.getSensorId(it)))

        ltemp = sorted(lname,key=itemgetter(0))[:maxn]
        filt = ''
        i = 0

        f = Formatter()
        l = "{{%s}}"
        f.format(l)

        ns = ''
        exp = []
        i,m =0,len(ltemp)
        loopi=0
        while i < m:
            h = f.parse(pattern)
            for a,b,c,d in h :
                ns += a 
                if b is not None : 
                    ns += '{' + str(eval(b)) + '}'
                    i = eval(b)
                    loopi = max(i,loopi)
            if cond != '':
                ns += '.apply(lambda x:' + cond + ')'
            if loopi < m-1:
                ns += '; '
            i = loopi + 1

        cs = self.getSeries(ltemp,dtfilter)
        re = self.getExpression(ltemp,ns, cs)
        series = []
        for name ,c in re:
            dataserie = defaultdict()  
            json_s = c[['stime','svalue']].to_json(orient='values')
            dataserie['name']=name
            dataserie['data']=json_s
            series.append(dataserie)
        return series