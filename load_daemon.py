#!/usr/bin/python3

#ps -eo comm,ppid,pid,sid,tty,state|grep "load_daemon*"

import logging
import signal
import errno
from time import sleep
from os import (
    fork, _exit, umask, chdir, sysconf_names, setsid, sysconf, open, close, write,
    EX_OK, lockf, EX_OSERR,O_RDWR, O_CREAT, F_TLOCK,
)


def daemonize():

    pid = fork()
    if pid > 0:
        _exit(EX_OK)
    # TODO: Obsluga sygnalow!
    setsid()
    pid2 = fork()
    if pid2 > 0:
        _exit(EX_OK)

    umask(0)
    chdir('/var/lock')
    for f in range(2, -1, -1):
            close(f)
    # FIXME:tworzenie lockfile'a = tylko jedna instancja daemona :)
    #lockfile = open('load_daemon.lock', O_RDWR | O_CREAT, 0o720)
    #if lockf(lockfile, F_TLOCK, 0) < 0:
    #    exit(EX_OK)
    #else:
    #    write(pid2, str(pid2))


def main():
    daemonize()
    while True:
        sleep(200)


if __name__ == '__main__':
    main()

