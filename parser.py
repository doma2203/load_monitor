#!/usr/bin/env python
import re
import time
import psutil
from functools import wraps
from glob import glob

# TODO: Procesy!

"""Funkcje wewnetrzne - nie modyfikowac, ogladac mozna :)"""

def loop(delay=2):
    '''
    Dekorator do testow funkcji, wywoluje w nieskonczonej petli funkcje w podanym odstepie czasowym.

    :param delay: opoznienie dla petli (w sekundach), domyslnie 2 sekundy
    '''
    def deco(func):
        @wraps(func)
        def wrapper(*args,**kwargs):
            while True:
                #os.system('clear')
                print func(*args,**kwargs)
                time.sleep(delay)
        return wrapper
    return deco


def _recpufreq(storage):
    procinfo=re.compile(r'(?<=processor\t:\s)\d')
    freqinfo=re.compile(r'(?<=cpu MHz\t\t:\s)\d+.\d+')
    file = open('/proc/cpuinfo', 'r')
    infos=''.join(file.readlines())
    file.close()
    cores=procinfo.findall(infos)
    corefreqs=freqinfo.findall(infos)
    for core,corefreq in zip(cores,corefreqs):
        storage['cpu'+core]=float(corefreq)


def _cpufreq(corenum,storage):
    coredata=['/sys/bus/cpu/devices/cpu'+str(i)+'/cpufreq/cpuinfo_cur_freq' for i in range(corenum)]
    for coreinfo,num in zip(coredata,range(corenum)):
        file=open(coreinfo,'r')
        storage['cpu'+str(num)]=float(file.readline())/1000
        file.close()


def _preparetemp(path):
    labelpaths=glob(path+'/temp?_label')
    valuepaths=glob(path+'/temp?_input')
    valuepaths.sort()
    labelExist = lambda dirlist: bool(len(dirlist))
    appendItem= lambda m: labels.append('temp'+str(m))
    valuenum = len(valuepaths)
    res=dict()
    isEmpty=lambda x: not bool(len(x))
    labels=list()
    for i in range(1,valuenum+1):
        if labelExist(labelpaths):
            labelfile = open(path+'/temp'+str(i)+'_label', 'r')
            labels.append(labelfile.readline().strip())
            labelfile.close()
        else:
            appendItem(i)

    for label,value in zip(labels,valuepaths):
        file=open(value,'r')
        try:
            res[label]=float(file.readline())/1000 #te nieszczesne milistopnie Celsjusza...
        except IOError:
        # problem z odczytem wartosci dla np. karty graficznej - plik pusty, trzeba obsluzyc 'No such device'
            res[label]=0
        finally:
            file.close()
    return res

"""Koniec funkcji wewnetrznych, ponizej dostepny interfejs:"""

def uptime():
    file = open('/proc/uptime','r')
    line=file.readline()
    file.close()
    uptimes=line.split()
    uptimes=[float(values)-3600 for values in uptimes]
    # TODO: Sprawdzic, czy odjecie godziny ma zwiazek ze strefa czasowa!
    return time.strftime('%H:%M:%S',time.localtime(uptimes[0]))


def cpufreqmonit(corenum=-1):
    """
    Uogolniony\* interfejs do wyswietlania obecnej czestotliwosci zegara dla kazdego z rdzeni logicznych(!).
    W razie mozliwosci korzysta z nowszego interfejsu kernela, ktory przechowuje wartosc taktowania kazdego
    z rdzeni w osobnym pliku. Jesli nie wykryje charakterystycznych dla tego interfejsu katalogow, parsuje
    standardowy plik /proc/cpuinfo.
    *Co moglam, wyciagnelam "przed nawias".

    :return: Slownik przechowujacy wartosci rdzen=taktowanie (w MHz) dla kazdego wykrytego rdzenia
    :rtype: dict
    """
    corenum=corenum
    corenum=len(glob('/sys/bus/cpu/devices/cpu?')) if -1 else corenum
    freq=dict()
    _recpufreq(freq) if corenum is 0 else _cpufreq(corenum,freq)
    return freq

def battery_status():
    batteries=glob('/sys/class/power_supply/BAT?')
    batteryinfo = dict()
    if bool(len(batteries)):
        battmatch=re.compile(r'(?<=power_supply/)(\w{3}\d)')
        for battery in batteries:
            current=open(battery+'/capacity','r')
            battid = battmatch.search(battery)
            batteryinfo[battid.group(0)]=float(current.readline())
            current.close()
    return batteryinfo

def meminfo():
    file=open('/proc/meminfo','r')
    mem=file.readline().split()

def tempinfo():
    infopaths=glob('/sys/class/hwmon/*')
    res=dict()
    for infopath in infopaths:
        group=open(infopath+'/name')
        res[group.readline().strip()]=_preparetemp(infopath)
        group.close()
    return res


'''Testy:'''
print "Uptime:\t{0}\nBateria:{1}\nTaktowania:\n{2}\nTemperatury:\n{3}"\
    .format(uptime(),battery_status().values(),cpufreqmonit(),tempinfo())