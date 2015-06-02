#!/usr/bin/python -O
import time
import hashlib
import urllib2
from collections import defaultdict
import mysql.connector
import sqlite3
import csv
import datetime
import gviz_api
from pandas.io import sql
import pandas
from pandas import DataFrame
from local_settings import CONNEXION_PATH
cnx = sqlite3.connect(CONNEXION_PATH+"/mysite/databases/localdb")
data_cnx=sqlite3.connect(CONNEXION_PATH+"/mysite/databases/db")
import matplotlib.pyplot as plt

hash=defaultdict(lambda: defaultdict())
__author__ = 'eric'

DATASET_COLS=['datasetid', 'buildingid' ,'collection_interval', 'start_date', 'end_date',
              'timings', 'reportid', 'sensorid', 'record_count']
SENSORLIST_COLS=['sensorid', 'buildingid' ,'sensorname', 'sensortype', 'sensorfloor',
                 'sensor_deviceid', 'sensor_units']

class Connect(object):

    def __init__(self):
        self.config = {
            'user': 'bpluser',
            'password': 'bplpass',
            'host': '192.168.2.44',
            'database' : 'bpl_20140410_dev',}

        #'database': 'bpl_performance_lab',}
        self.csql = mysql.connector.connect(**self.config)
    def download_sensors(self):
        global cnx
        print "building_sensor"
        self.sensorlist=sql.read_frame('select * from sensors where buildingid=1',con=self.csql)
        self.sensorlist['id']=self.sensorlist.index
        sql.write_frame(self.sensorlist,name="building_sensor",con=cnx,if_exists='replace')
        floorlist = sql.read_frame('select distinct sensorfloor from building_sensor',con=cnx)
        floorlist['id']=floorlist.index
        sql.write_frame(floorlist,name='building_floor',con=cnx,if_exists='replace')
        self.dataset=sql.read_frame('select * from datasets where buildingid=1',con=self.csql)
        self.dataset['id']=self.dataset.index
        print self.dataset.head()
        #sql.write_frame(self.dataset,name="dataset",con=data_cnx,if_exists='replace')



    def existsData(self,sensorid):
        cnx = sqlite3.connect(CONNEXION_PATH+"/mysite/databases/db")
        e = sql.table_exists('sensor_'+  str(id),cnx,'sqlite')
        cnx.close()
        return e

    def getSensorData(self,name,force=False):
        val=None
        cols = self.sensorlist['sensorname']
        id = int(self.sensorlist[cols == name].sensorid)
        print "sensor",name,"id=",id
        if self.existsData(id):
            maxdate = max(sql.read_frame(('select * from sensor_%d')%(id),data_cnx).index)
            keyword='append'
        else:
            maxdate = 0
            keyword='replace'

        dsids = self.dataset[(self.dataset.sensorid==id) & (self.dataset.collection_interval==15)].datasetid
        print "name", dsids
        for dsid in dsids:
            v2 = None
            try:
                v2 = sql.read_frame(("select stime as `stime` , cast(svalue as decimal(10,3)) as 'svalue' from data_item where datasetid = %d;")%(dsid),con=self.csql) 
                v2['svalue']=v2['svalue'].astype('float64')
            except:
                print "something wrong with dsid",dsid,v2.head()
            if v2 is None :
                continue
            if val is None :
                val = v2
            else:
                val =  val.append(v2[v2.index.values >= maxdate])
        if val is None or len(val) == 0:
            print "table ",'sensor_'+str(id), "nothing to write"
        else:
            val['stime']=val['stime'].apply(lambda x: x.strftime('%Y-%m-%d %H:%M:%S'))
            print val[['stime','svalue']].head()
            sql.write_frame(val[['stime','svalue']],name='sensor_'+str(id),con=data_cnx,if_exists=keyword)
            print "table ",'sensor_'+str(id), "written"
        return val


def connect_test():
    connect = Connect()
    name='JJCEX.SCHWP.PH.08.VFD.SPD'
    vall = connect.getSensorData(name)

    vall.index = pandas.to_datetime(vall.pop('stime'))
    mean = pandas.rolling_mean(vall.values,window=20)
    st = pandas.rolling_std(vall.values,window=20)
    vall['MA'] = mean
    vall['std2'] = mean + 2*st
    vall['std_2'] = mean - 2*st

    print vall.index
    vall['stime'] = vall.index
    vall.plot()
    dict = vall.to_dict('records')

    data_table = gviz_api.DataTable({'stime':'datetime','svalue':'number','MA':'number','std_2':'number','std2':'number'})
    data_table.LoadData(dict)


    json = data_table.ToJSon(columns_order=('stime','svalue','MA','std_2','std2'),order_by=('stime'))

    txt =  page_template % vars()

    f = open("t.html",mode='w')
    print >>f,txt
    f.close()
    plt.show()

if  __name__ == "__main__":
    c = Connect()

    while (True):
        print "downloading sensors"
        c.download_sensors()
        for n in  c.sensorlist['sensorname']:
            print 'downloading ',n
            c.getSensorData(n)