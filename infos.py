#!/usr/bin/env python

import psutil
from functools import wraps
from glob import glob, iglob
import os
import os.path
import re
import time


class MonitorPoint(object):
    def __init__(self):
        self._value = self.check()
        self._label = self.checklabel()


    @property
    def label(self):
        return self._label

    @label.setter
    def label(self,lab):
        self._label=lab

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self,val):
        self._value=val

    def __call__(self, *args, **kwargs):
        '''Zakladam, ze w najprostszym przypadku etykietki brak '''
        return self.value


    def check(self):
        raise NotImplementedError

    def checklabel(self):
        return None

#Temperature(/sys/class/hwmon/hwmon1/temp1(_value|_label))


class Temperature(MonitorPoint):
    def __init__(self,path):
        self._path = path
        super(Temperature,self).__init__()

    def __call__(self, *args, **kwargs):
        return self.label,self.value

    @property
    def path(self):
        return self._path

    def check(self):
        try:
            file=open(self.path)
        except IOError:
           return 0
        return float(file.readline())/1000

    def checklabel(self):
        '''Jakis kreatywny docstring'''
        lab=re.sub(r'(input)','label',self.path)
        if os.path.exists(lab):
            file=open(lab)
            return file.readline().strip()
        return re.findall(r'(temp\d)',self.path)[0]

class TemperaturePoints:
    def __init__(self,dirpath):
        self._items=[Temperature(path)() for path in glob(dirpath+'/temp?_input')]
        self._dirpath=dirpath
        self._group=self.checkgroup()

    def __iter__(self):
        yield self._dirpath
        for item in self._items:
            yield item

    def checkgroup(self):
        name=self._dirpath+'/name'
        if os.path.exists(name):
            file=open(name)
            return file.readline().strip()
        return None



class Uptime(MonitorPoint):
    def check(self):
        file = open('/proc/uptime', 'r')
        line = file.readline()
        file.close()
        uptimes = line.split()
        uptimes = [float(values) - 3600 for values in uptimes]
        return time.strftime('%H:%M:%S', time.localtime(uptimes[0]))


y=Uptime()
print y()
for x in iglob('/sys/class/hwmon/hwmon1'):
    a=[Temperature(y)() for y in iglob(x+'/temp?_input')]

print a



y=(Temperature('/sys/class/hwmon/hwmon0/temp2_input')(),Temperature('/sys/class/hwmon/hwmon1/temp1_input')())
for i in y:
    print i
