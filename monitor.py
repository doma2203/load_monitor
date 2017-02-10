#!/usr/bin/env python
import os

if os.getuid() is not 0:
    raise ImportWarning('Aby uruchomic program wykorzystujacy modul monitor, potrzebujesz praw roota!')

import psutil
from glob import glob
import os.path
import re
import time
from pySMART import DeviceList


''' Wersja obiektowa kodu jest skonstruowana tak, aby jak najmniej czesci wspolnych dla modulu sie powtarzalo,
zeby mozliwa byla specjalizacja jednego konkretnego elementu (klasy) w kontekscie wielu odczytow, poprzez dziedziczenie
i metody abstrakcyjne. Kazdy odczyt posiada te same metody, ale dla kazdego elementu realizowane sa inaczej, z uwagi
na rozne pliki, z ktorych czytaja oraz inny sposob etykietowania i nazywania konkretnych odczytow. Kod z tego powodu
moze wydawac sie troche dluzszy, ale jest sporo czytelniejszy (szczegolnie widac to na przykladzie temperatury).
Wszystkie klasy poszczegolnych parametrow sa "callable" - zeby mozliwe bylo zwrocenie czytelnych i sensownych wartosci,
a te, ktore zorganizowane sa w bardziej zlozone typy danych - takze "iterable", zeby uzytkownik mogl sobie intuicyjnie
iterowac po rdzeniach, procesach i obszarach monitorowania temperatury. '''


class MonitorPoint(object):
    def __init__(self):
        self._value = self.check()
        self._label = self.checklabel()

    @property
    def label(self):
        return self._label

    @label.setter
    def label(self, lab):
        self._label = lab

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, val):
        self._value = val

    def __call__(self, *args, **kwargs):
        '''Zakladam, ze w najprostszym przypadku etykietki brak. Tak jest na przyklad z Uptime()'''
        return self.value

    def check(self):
        raise NotImplementedError

    def checklabel(self):
        return None


class Temperature(MonitorPoint):
    def __init__(self, path):
        self._path = path
        super(Temperature, self).__init__()

    def __call__(self, *args, **kwargs):
        return self.label, self.value

    @property
    def path(self):
        return self._path

    def check(self):
        file = open(self.path)
        try:
            return float(file.readline()) / 1000
        except IOError:
            # problemy z niektorymi urzadzeniami nie udostepniajacymi informacji (niektore karty graficzne)
            return 0

    def checklabel(self):
        '''Jako glowny parametr klasy dostajemy plik z odczytem poniewaz zakladamy, ze takowy bedzie istnial zawsze,
        czego nie mozna powiedziec np. o etykietkach. Jedyna zmiana, jaka musimy poczynic, zeby plik z odczytem zmienil
        sie w plik kandydujacy do pliku z etykieta (nie jestesmy 100% pewni, gdzie i co posiada etykiety, stad exist())
        jest podmiana czesci sciezki za pomoca re.sub-a.'''
        lab = re.sub(r'(input)', 'label', self.path)
        if os.path.exists(lab):
            file = open(lab)
            return file.readline().strip()
        return re.findall(r'(temp\d)', self.path)[0]


class TemperaturePoints:
    def __init__(self, dirpath):
        self._dirpath = dirpath
        self._items = [Temperature(path)() for path in glob(self._dirpath + '/temp?_input')]
        self._group = self.checkgroup()

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
        return self.group, self.items

    def __iter__(self):
        '''przyklad dzialania iteratora:
        for i in iglob('/sys/class/hwmon/hwmon?'):
            for k in TemperaturePoints(i):
                print k
        Dla wiekszej przejrzystosci dodano Temperatures() (implementacja ponizej)'''
        yield self.group
        for item in self.items:
            yield item

    def checkgroup(self):
        name = self._dirpath + '/name'
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
    def __init__(self, path):
        self._path = path
        super(Frequency, self).__init__()

    def __call__(self, *args, **kwargs):
        return self.label, self.value

    @property
    def path(self):
        return self._path

    def check(self):
        file = open(self.path + 'cpuinfo_cur_freq')
        return float(file.readline()) / 1000  # zamiana na MHz

    def checklabel(self):
        return re.findall(r'(cpu\d)', self.path)[0]


class Cores:
    def __init__(self):
        self._dirpath = '/sys/bus/cpu/devices/cpu?/cpufreq/'
        self._cores = self.sortcores()

    def __call__(self, *args, **kwargs):
        return self.cores

    def __iter__(self):
        for core in self.cores:
            yield core

    @property
    def cores(self):
        return self._cores

    def sortcores(self):
        # Wypadalo posortowac...
        cores = [Frequency(path)() for path in glob(self._dirpath)]
        return sorted(cores, key=lambda m: m[0])


class Processes:
    def __init__(self, number=5):
        self._number = number
        self._pslist = self.processlist()

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
        '''Po wyjasnienia 'dlaczego tak nieczytelnie' zapraszam do dokumentacji psutil, czytelniej sie nie dalo.
        Lambda to handmade, sortowanie jest przeprowadzane poprawnie, nawet jesli nie uruchamiamy jej w petli
        (od niej zalezy cpu_percent), bo sortuje wtedy wedlug zuzucia RAM-u, a potem przez przydzial pamieci :)
        Zwracamy liste (wazna kolejnosc!!!) skladajaca sie z nazwy i PID-u - umozliwia to szybkie reczne 'ubicie'
        procesu naduzywajacego naszej goscinnosci... '''
        proclist = list()
        for ps in psutil.process_iter():
            proclist.append(ps.as_dict(attrs=['pid', 'name', 'memory_percent', 'memory_info', 'cpu_percent']))
        proclist = sorted(proclist, key=lambda k: (k['cpu_percent'], k['memory_percent'], k['memory_info'][0],
                                                   k['memory_info'][1]), reverse=True)[:self.number]
        return [(proc['name'], proc['pid']) for proc in proclist]


class RAMunit(MonitorPoint):
    def __init__(self, mode):
        self._mode = mode
        super(RAMunit, self).__init__()

    def __call__(self, *args, **kwargs):
        return self.mode, self.value

    @property
    def mode(self):
        return self._mode

    def check(self):
        ''' Co sie tu dzieje: Wyrazenia regularne typu: "positive lookbehind assertion" nie przyjmuja w czesci
        okreslajacej poprzednik zmiennej dlugosci wyrazow (w tym wypadku spacji),wiec nie przejdzie ani
         \s{4,11}, ani tym bardziej \s+. Ilosc spacji zalezy od... dlugosci liczby okreslajacej pamiec w kB, wiec
         trzeba cyklicznie rzucac wyjatkiem i go obslugiwac, zmieniajac wyrazenie. '''
        file = open('/proc/meminfo')
        info = file.readlines()
        if self.mode is 'total':
            return RAMunit.findsize(10, 5, 'MemTotal', info[0])
        elif self.mode is 'free':
            # nie wiem, kto wymyslil taka ilosc spacji, otrzymane po zmudnym liczeniu w terminalu :D
            return RAMunit.findsize(11, 4, 'MemFree', info[1])
        else:
            raise NotImplementedError

    @staticmethod
    def findsize(upperbound, lowerbound, parameter, text):
        for spacenum in range(upperbound, lowerbound, -1):
            regexp = r'(?<=' + parameter + ':\s{' + str(spacenum) + '})(\d+)'  # "skladanie" regexpa :)
            try:
                res = re.search(regexp, text)
                return float(res.group(0)) / 1024
            except AttributeError:
                continue


class RAM:
    def __init__(self):
        self._avaliable = RAMunit('total')
        self._free = RAMunit('free')

    def __call__(self, *args, **kwargs):
        return self.available(), self.free()

    @property
    def available(self):
        return self._avaliable

    @property
    def free(self):
        return self._free


class Battery(MonitorPoint):
    def __init__(self, path):
        self._path = path
        super(Battery, self).__init__()

    def __call__(self, *args, **kwargs):
        return self.label, self.value

    @property
    def path(self):
        return self._path

    def check(self):
        if os.path.exists(self.path + '/capacity'):
            file = open(self.path + '/capacity')
            return float(file.readline())

    def checklabel(self):
        if os.path.exists(self.path):
            battlab = re.search('(?<=power_supply/)(BAT\d)', self.path)
            return battlab.group(0)


class Batteries:
    def __init__(self):
        self._path = '/sys/class/power_supply/BAT?'
        self._battlist = [Battery(i)() for i in glob(self.path)]

    def __call__(self, *args, **kwargs):
        return self.batterylist

    def __iter__(self):
        for battery in self.batterylist:
            yield battery

    @property
    def path(self):
        return self._path

    @property
    def batterylist(self):
        return self._battlist


def Temperatures():
    # opakowane w ladniejsza funkcje
    for i in glob('/sys/class/hwmon/hwmon?'):
        for k in TemperaturePoints(i):
            yield k


class HDD:
    '''Znalazlam modul do odczytu S.M.A.R.T-a! :D'''
    def __init__(self):
        self._devices = [i for i in DeviceList().devices]
        self.gettemp = lambda k: int(str(k.attributes[194]).split()[-1])

    @property
    def devices(self):
        return self._devices

    def __call__(self, *args, **kwargs):
        return [(device.name, self.gettemp(device)) for device in self.devices]

    def __iter__(self):
        for dev in self.devices:
            yield dev.name, self.gettemp(dev)
