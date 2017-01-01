#!/usr/bin/env python
import re
import time
import psutil
from functools import wraps
from glob import glob
import os

"""Funkcje wewnetrzne - nie modyfikowac, ogladac mozna :)"""
exist = lambda dirlist: bool(len(dirlist))


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

    appendItem = lambda m: labels.append('temp'+str(m))
    #isEmpty = lambda x: not bool(len(x))
    valuenum = len(valuepaths)
    res=dict()
    labels=list()

    for i in range(1,valuenum+1):
        if exist(labelpaths):
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


def _processinfo():
    processinfo = list()
    for process in psutil.process_iter():
        processinfo.append(process.as_dict(attrs=['pid', 'name', 'memory_percent', 'memory_info', 'cpu_percent']))
    return sorted(processinfo, key=lambda k: (k['cpu_percent'], k['memory_percent'],
                                              k['memory_info'][0], k['memory_info'][1]), reverse=True)[:5]


"""Koniec funkcji wewnetrznych, ponizej dostepny interfejs:"""



def cpufreqmonit(corenum=-1):
    """Uogolniony\* interfejs do wyswietlania obecnej czestotliwosci zegara dla kazdego z rdzeni logicznych(!).
    W razie mozliwosci korzysta z nowszego interfejsu kernela, ktory przechowuje wartosc taktowania kazdego
    z rdzeni w osobnym pliku. Jesli nie wykryje charakterystycznych dla tego interfejsu katalogow, parsuje
    standardowy plik /proc/cpuinfo.\n
    *Co moglam, wyciagnelam "przed nawias".\n
    :return: Slownik przechowujacy wartosci rdzen=taktowanie (w MHz) dla kazdego wykrytego rdzenia
    :rtype: dict"""
    corenum=corenum
    corenum=len(glob('/sys/bus/cpu/devices/cpu?')) if -1 else corenum
    freq=dict()
    _recpufreq(freq) if corenum is 0 else _cpufreq(corenum,freq)
    return freq

def battery_status():
    batteries=glob('/sys/class/power_supply/BAT?')
    batteryinfo = dict()
    if exist(batteries):
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


def uptime():
    file = open('/proc/uptime', 'r')
    line = file.readline()
    file.close()
    uptimes = line.split()
    uptimes = [float(values) - 3600 for values in uptimes]
    # TODO: Sprawdzic, czy odjecie godziny ma zwiazek ze strefa czasowa!
    return time.strftime('%H:%M:%S', time.localtime(uptimes[0]))

def tempinfo():
    infopaths=glob('/sys/class/hwmon/*')
    res=dict()
    for infopath in infopaths:
        group=open(infopath+'/name')
        res[group.readline().strip()]=_preparetemp(infopath)
        group.close()
    return res


@loop()
def processes():
    """Kolezanka (funkcja) wymaga specjalnego traktowania, gdyz najlepiej czuje sie w obecnosci petli, tudziez dekoratora
    z takowa. Bez tego nie zwraca poprawnie 'cpu_percent' (dzialanie przewidziane i zgodne z dokumentacja biblioteki),
    ale sortuje po pozostalych parametrach, wiec te bardziej zasobozerne (co do pamieci) wyswietla nadal poprawnie.\n
    :return:
    :rtype: dict """
    info = _processinfo()
    for item in info:
    # TODO: Wyprowadzic ludzki format listy!!!
        pass

'''Testy:'''

print "Uptime:\t{0}\nBateria:{1}\nTaktowania:\n{2}\nTemperatury:\n{3}\n".format(uptime(),battery_status(),cpufreqmonit(),tempinfo())
