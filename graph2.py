__author__ = 'eric'
from collections import defaultdict
import sqlite3
import json
import gviz_api
from pandas.io import sql
import pandas


page_template = """
<html>
<head>
    <script type='text/javascript' src='http://www.google.com/jsapi'></script>
    <script type='text/javascript'>
    google.load('visualization', '1', {packages:['annotationchart']});

    google.setOnLoadCallback(drawChart);
    function drawChart() {

        var chart = new google.visualization.AnnotationChart(document.getElementById('chart_div'));
        var options = {
          displayAnnotations: false,
          allowRedraw:false,

        };
        var json_data = new google.visualization.DataTable(%(json)s, 0.6);

        chart.draw(json_data, options);
    }
  </script>
  </head>
  <body>
    <H1>%(name)s</H1>
    <div id='chart_div' style='width: 1400px; height: 500px;'></div>
  </body>
</html>
"""
page_template_lin = """
<html>
<head>
    <script type='text/javascript' src='http://www.google.com/jsapi'></script>
    <script type='text/javascript'>
    google.load('visualization', '1', {packages:['corechart']});

    google.setOnLoadCallback(drawChart);
    function drawChart() {

        var chart = new google.visualization.AnnotationChart(document.getElementById('chart_div'));
        var options = {
         curveType:'function',
         lineWidth: 2,
        };
        var json_data = new google.visualization.DataTable(%(json)s, 0.6);

        chart.draw(json_data, options);
    }
  </script>
  </head>
  <body>
    <H1>%(name)s</H1>
    <div id='chart_div' style='width: 1200px; height: 500px; position:absolute;top:100px;left:150px'></div>
  </body>
</html>
"""

cnx = "/var/www/mysite/databases/localdb"
data_cnx= "/var/www/mysite/databases/db"
class Graph(object):


    def existData(self,sensorid):
        global data_cnx
        cnx = sqlite3.connect(data_cnx)
        e = sql.table_exists  ('sensor_'+  str(id),con=cnx)
        cnx.close()
        return e


    def getSensorData(self,id,force=False):
        global data_cnx
        cnx = sqlite3.connect(data_cnx)
        data = sql.read_frame('select * from sensor_'+  str(id),con=cnx)
        cnx.close()
        return data

    def getMSTF(self, name,sensorid):
        series = []
        data = self.getSensorData(sensorid)
        data.index = pandas.to_datetime(data.pop('stime'))

        mean = pandas.rolling_mean(data.values,window=20)
        st = pandas.rolling_std(data.values,window=20)

        data['MA'] = mean
        data['std2'] = mean + 2*st
        data['std_2'] = mean - 2*st
        data['stime'] = data.index

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
        return json.dumps(series)

    def getRegular(self,sensorlist):
        series =[]
        #[{
		#		name : 'AAPL',
		#		data : data,
		#	}]
        for name,id in sensorlist:
            dataserie = defaultdict()
            data1 = self.getSensorData(id)
            data1.index = pandas.to_datetime(data1['stime'])
            data1['stime'] = data1.index
            json_s = data1[['stime','svalue']].to_json(orient='values')
            dataserie['name']=name
            dataserie['data']=json_s
            series.append(dataserie)
        print json.dumps(series)
        return json.dumps(series)

    def getDiff(self, name1,sensorid1,name2,sensorid2):
        name = name1 + ' - ' + name2
        data = self.getSensorData(sensorid1)
        data.index = pandas.to_datetime(data.pop('stime'))

        data2 = self.getSensorData(sensorid2)
        data2.index = pandas.to_datetime((data2.pop('stime')))
        data['svalue'] = data['svalue'] - data2['svalue']
        data['stime'] = data.index
        dict = data.to_dict('records')

        data_table = gviz_api.DataTable({'stime':'datetime','svalue':'number'})
        data_table.LoadData(dict)
        json = data_table.ToJSon(columns_order=('stime','svalue'),order_by=('stime'))
        return json

    def getXY(self, name1,sensorid1,name2,sensorid2):
        name = name1 + ' - ' + name2
        data = self.getSensorData(sensorid1)
        data.index = pandas.to_datetime(data.pop('stime'))

        data2 = self.getSensorData(sensorid2)
        data2.index = pandas.to_datetime((data2.pop('stime')))
        data[name1] = data['svalue'] - data2['svalue']
        data.pop('stime')
        dict = data.to_dict('records')

        data_table = gviz_api.DataTable({name1:'number',name2:'number'})
        data_table.LoadData(dict)
        json = data_table.ToJSon(columns_order=('stime','svalue'),order_by=('stime'))
        txt =  page_template % vars()
        return json
