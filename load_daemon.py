#!/usr/bin/env python3

import logging
import signal
from os import (
    fork, _exit, umask, chdir, sysconf_names, sysconf, close, EX_OK, EX_OSERR
)


def demonize():
    try:
        p = fork()
    except OSError:
        _exit(EX_OSERR)
    else:
        _exit(EX_OK)

    umask(0)
    chdir('/')
    fdv = sysconf(sysconf_names['SC_OPEN_MAX'])
    closestats = [close(fd) for fd in range(fdv, 0, -1)]
    if -1 in closestats:
        raise OSError('Unsuccessful detaching from control terminal. Demonization aborted.')


def main():
    pass

if __name__ == '__main__':
    main()

