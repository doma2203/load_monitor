#!/usr/bin/env python

import psutil
from functools import wraps
from glob import glob
import os
import re
import time


class Monit(object):
    def __init__(self):
        self.cores = ['cpu' + str(i) for i in Monit.numofcores()]
       #! self.labels = [label for label in Monit.label((path for path in Monit.monitpaths()))]
        self.batteries = [battery for battery in Monit.setbatteries()]
        self.measurepoints = [points for points in Monit.measurepoints()]


    @staticmethod
    def amount(path):
        return len(glob(path))

    @staticmethod
    def numofcores():
        num = Monit.amount('/sys/bus/cpu/devices/cpu?')
        for i in range(num):
            # mogloby byc yield from, jakby to byl Python > 3.3 :/
            yield i

    @staticmethod
    def measurepoints():
        names = sorted(glob('/sys/class/hwmon/hwmon?/name'))
        for name in names:
            file = open(name, 'r')
            yield (file.readline().strip())

    @staticmethod
    def monitpaths():
        for path in glob('/sys/class/hwmon/hwmon?'):
            yield path

    @staticmethod
    def setbatteries():
        for path in glob('/sys/class/power_supply/BAT?'):
            a = re.findall(r'power_supply/(BAT\d)', path)
            yield a[0]

    @staticmethod
    # TODO popraw!
    def label(path):
        labelnum = Monit.amount(path + '/temp?_label')
        valuenum = Monit.amount(path + '/temp?_input')
        for i in range(1, valuenum + 1):
            if bool(labelnum):
                labelfile = open(path + '/temp' + str(i) + '_label')
                yield labelfile.readline().strip()
            else:
                yield 'temp' + str(i)

    def cpufreq(self):
        cores = len(self.cores)
        res = dict()
        values = ('/sys/bus/cpu/devices/cpu' + str(i) + '/cpufreq/cpuinfo_cur_freq' for i in range(cores))
        for lab, value in zip(self.cores, values):
            file = open(value, 'r')
            res[lab] = float(file.readline()) / 1000
            file.close()
        return res

    def batteryinfo(self):
        batteries=self.batteries
        values=('/sys/class/power_supply/'+i+'/capacity' for i in batteries)
        res=dict()
        for battery, value in zip(batteries,values):
            file=open(value)
            res[battery]=float(file.readline())
            file.close()
        return res

    @staticmethod
    def uptime():
        file = open('/proc/uptime', 'r')
        line = file.readline()
        file.close()
        uptimes = line.split()
        uptimes = [float(values) - 3600 for values in uptimes]
        # TODO: Sprawdzic, czy odjecie godziny ma zwiazek ze strefa czasowa!
        return time.strftime('%H:%M:%S', time.localtime(uptimes[0]))

    @staticmethod
    def processinfo(numofproc=5):
        processinfo = list()
        for process in psutil.process_iter():
            processinfo.append(process.as_dict(attrs=['pid', 'name', 'memory_percent', 'memory_info', 'cpu_percent']))
        processinfo=sorted(processinfo, key=lambda k: (k['cpu_percent'], k['memory_percent'],
                                                 k['memory_info'][0], k['memory_info'][1]), reverse=True)[:numofproc]
        return [(x['name'],x['pid']) for x in processinfo]

x=Monit()
print x.cpufreq()
print x.uptime()
print x.batteryinfo()
print x.processinfo()