#!/usr/bin/python

# ps -eo comm,ppid,pid,sid,tty,state|grep "load_daemon*"

import logging
import signal
import errno
import monitor



def main():
    print monitor.Batteries()()
    print monitor.RAM()()
    pass

if __name__ == '__main__':
    main()

