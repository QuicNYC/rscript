import datetime
from django.utils import timezone
from django.db import models
SENSORLIST_COLS=['sensorid', 'buildingid' ,'sensorname', 'sensortype', 'sensorfloor',
 'sensor_deviceid', 'sensor_units']


class Floor(models.Model):
    sensorfloor=models.CharField(max_length=10)
    def __unicode__(self):
        return self.sensorfloor

class Sensor(models.Model):
    sensorid=models.IntegerField('sensorid')
    buildingid=models.IntegerField('buildingid')
    sensorname=models.CharField(max_length=48)
    sensortype=models.CharField(max_length=10)
    sensorfloor=models.CharField(max_length=10)
    sensor_deviceid=models.CharField(max_length=10)
    sensor_units=models.CharField(max_length=10)
    def __unicode__(self):
        return self.sensorname

