from os import (
    fork, _exit, umask, chdir, sysconf_names, setsid, sysconf, open, mkdir, close, getpid, write,
    EX_OK, dup2, O_RDWR, O_CREAT, O_RDONLY
)
from signal import signal, SIGHUP
import errno
import logging


class Config:
    def __init__(self):
        self.threshold=65
        self.compress=True
        self.modules={'default':True}

    def changeThreshold(self,threshold):
        self.threshold=threshold

    def compressLog(self,compress):
        self.compress=compress

    def moduleControl(self,name,action=None):
       if action is 'enable':
            self.modules.update({name:True})
       elif action is 'disable':
            self.modules.update({name:False})
       else:
           raise ValueError('Nieznana akcja!')


def mkconfig(defaultconf=None):

def reloadconfig():
           conffd=open(confdir+'load_monitor.conf', O_RDONLY)
    except OSError as e:
        if e.errno == errno.ENOENT:
            conffd=open(confdir+'load_monitor.conf', O_RDWR | O_CREAT)

            write(open)

    finally:
        # TODO: To bierzem, to co dostałam z socketa i wrzucam do configfile


        close(conffd)



def daemonize():

    pid = fork()
    if pid > 0:
        _exit(EX_OK)
    # TODO: Obsluga sygnalow!
    signal(SIGHUP, reloadconfig)
    setsid()
    pid2 = fork()
    if pid2 > 0:
        _exit(EX_OK)
    umask(0O22)
    chdir('/')
    mkdir(confdir)
    # FIXME: Jaki katalog roboczy wybrać dla daemona?
    for f in range(sysconf(sysconf_names['SC_OPEN_MAX']), 0, -1):
        try:
            close(f)
        except OSError:
            pass

    null = open('/dev/null', O_RDWR)
    dup2(null, 2)
    dup2(null, 0)

    # FIXME: A jakby otworzyć sobie stdout jako socket? :)



