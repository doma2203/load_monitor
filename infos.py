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
        file=open(self.path)
        try:
            return float(file.readline())/1000
        except IOError:
            return 0

    def checklabel(self):
        '''Jako glowny parametr klasy dostajemy plik z odczytem poniewaz zakladamy, ze takowy bedzie istnial zawsze,
        czego nie mozna powiedziec np. o etykietkach. Jedyna zmiana, jaka musimy poczynic, zeby plik z odczytem zmienil
        sie w plik z etykieta (ktorego, obecnosc w systemie plikow weryfikujemy), jest podmiana czesci
        sciezki za pomoca re.sub-a.'''
        lab=re.sub(r'(input)','label',self.path)
        if os.path.exists(lab):
            file=open(lab)
            return file.readline().strip()
        return re.findall(r'(temp\d)',self.path)[0]


class TemperaturePoints:
    def __init__(self,dirpath):
        self._dirpath = dirpath
        self._items=[Temperature(path)() for path in glob(self._dirpath+'/temp?_input')]
        self._group=self.checkgroup()

    @property
    def group(self):
        return self._group

    @property
    def items(self):
        return self._items

    @property
    def dirpath(self):
        return self._dirpath

    def __call__(self, *args, **kwargs):
        return self.group,self.items

    def __iter__(self):
        '''przyklad dzialania iteratora:
        for i in iglob('/sys/class/hwmon/hwmon?'):
            for k in TemperaturePoints(i):
                print k '''
        yield self.group
        for item in self.items:
            yield item

    def checkgroup(self):
        name = self._dirpath+'/name'
        if os.path.exists(name):
            file = open(name)
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


class Frequency(MonitorPoint):
    def __init__(self,path):
        self._path=path
        super(Frequency,self).__init__()

    def __call__(self, *args, **kwargs):
        return self.label, self.value

    @property
    def path(self):
        return self._path

    def check(self):
        file=open(self.path+'cpuinfo_cur_freq')
        return float(file.readline())/1000  # zamiana na MHz

    def checklabel(self):
        return re.findall(r'(cpu\d)',self.path)[0]


class FrequencyPoints:
    def __init__(self,dirpath):
        self._dirpath=dirpath
        self._cores=[Frequency(path)() for path in glob(self.dirpath)]

     def __call__(self, *args, **kwargs):
         return self.cores

    def __iter__(self):
        for core in self.cores:
            yield core

    @property
    def cores(self):
        return self._cores


class Processes:
    def __init__(self,number=5):
        self._number=number
        self.pslist=self.processlist()

    def __call__(self, *args, **kwargs):
        return self.pslist

    def __iter__(self):
        for process in self.pslist:
            yield process

    @property
    def number(self):
        return self._number

    @property
    def pslist(self):
        return self._pslist

    def processlist(self):
        proclist=list()
        for ps in psutil.process_iter():
            proclist.append(ps.as_dict(attrs=['pid', 'name', 'memory_percent', 'memory_info', 'cpu_percent']))
        proclist=sorted(proclist, key=lambda k: (k['cpu_percent'], k['memory_percent'],
                                                     k['memory_info'][0], k['memory_info'][1]), reverse=True)[:self.number]
        return [(proc['name'],proc['pid']) for proc in proclist]
