from time import sleep
from os import (
    fork, _exit, umask, chdir, sysconf_names, setsid, sysconf, open, close, getpid, write,
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
    chdir('/')

    for f in range(sysconf(), -1, -1):
        try:
            close(f)
        except OSError:
            pass



