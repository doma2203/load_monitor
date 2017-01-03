#!/usr/bin/env python

import psutil
from functools import wraps
from glob import glob, iglob
import os
import re
import time

def loop(delay=2):
    """Dekorator do testow funkcji, wywoluje w nieskonczonej petli funkcje w podanym odstepie czasowym.\n
    :param delay: opoznienie dla petli (w sekundach), domyslnie 2 sekundy"""
    def deco(func):
        @wraps(func)
        def wrapper(*args,**kwargs):
            while True:
                os.system('clear')
                print func(*args,**kwargs)
                time.sleep(delay)
        return wrapper
    return deco

class Monit(object):
    def __init__(self):
        self.cores = [core for core in Monit.numofcores()]
        self.batteries = [battery for battery in Monit.setbatteries()]
        self.measurepoints = [points for points in Monit.measurepoints()]
        self.labels=Monit.templabels()


    @staticmethod
    def amount(path):
        return len(glob(path))

    @staticmethod
    def numofcores():
        num = Monit.amount('/sys/bus/cpu/devices/cpu?')
        for i in range(num):
            # mogloby byc yield from, jakby to byl Python > 3.3 :/
            yield 'cpu'+str(i)

    @staticmethod
    def measurepoints():
        names = sorted(glob('/sys/class/hwmon/hwmon?/name'))
        for name in names:
            file = open(name, 'r')
            yield (file.readline().strip())


    @staticmethod
    def setbatteries():
        for path in glob('/sys/class/power_supply/BAT?'):
            a = re.findall(r'power_supply/(BAT\d)', path)
            yield a[0]

    # @staticmethod
    # def temperatures(paths = glob('/sys/class/hwmon/hwmon?')):
    #     paths.sort()
    #     for path in paths:
    #         labels=glob(path + '/temp?_label')
    #         values=glob(path + '/temp?_input')
    #         labels.sort()
    #         labelnum = len(labels)
    #         valuenum=len(values)
    #         res=dict()
    #         lab=list()
    #         for label,i in zip(labels,range(1,valuenum+1)):
    #             if bool(labelnum):
    #                 labelfile = open(label)
    #                 lab.append(labelfile.readline().strip())
    #                 labelfile.close()
    #             else:
    #                 lab.append('temp'+str(i))
    #             namefile = open(path + '/name', 'r')
    #             res[namefile.readline().strip()]=dict.fromkeys(lab)
    #             namefile.close()
    #             # file=open(value,'r')
    #             # try:
    #             #     val=float(file.readline())/1000
    #             # except IOError:
    #             #     val=0
    #             # file.close()
    #             # res[name] = dict(lab=val)
    #             return res
    @staticmethod
    def templabels(paths=glob('/sys/class/hwmon/*')):
        paths=sorted(paths)
        for path in paths:
            name=glob(path+'/name')[0]
            labels=glob(path+'temp?_label')
            labels=sorted(labels)
            labelnum=len(labels)
            valuenum=len(glob(path+'temp?_input'))
            lab = list()
            res=dict()
            for label,i in zip(labels,range(1,valuenum+1)):
                if bool(labelnum):
                    labelfile=open(label,'r')
                    lab.append(labelfile.readline().strip())
                    labelfile.close()
                else:
                    lab.append('temp'+str(i))
            namefile = open(name, 'r')
            res[namefile.readline().strip()]=dict.fromkeys(lab)
            namefile.close()
        return res


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
        uptimes = file.readline().split()
        file.close()
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
        return [(proc['name'],proc['pid']) for proc in processinfo]


x=Monit()
print x.cpufreq()
print x.uptime()
print x.batteryinfo()
print x.processinfo()
print x.labels
# print x.temperatures()