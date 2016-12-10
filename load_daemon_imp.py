#!/usr/bin/python3

# ps -eo comm,ppid,pid,sid,tty,state|grep "load_daemon*"
from time import sleep
import daemon


def main():

    with daemon.daemonize('var/lock/lock.pid'):
        sleep(200)


if __name__ == '__main__':
    main()

