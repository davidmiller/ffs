"""
Demo HTTP stuffs.

Start a server in another thread, then interact with it.
"""
import os
import sys
import multiprocessing
import time

from ffs.contrib import http

def runserver():
    from SimpleHTTPServer import test as goservergo
    goservergo()

servit = multiprocessing.Process(target=runserver)
servit.start()

briefly = 0.54321
time.sleep(briefly)

p = http.HTTPPath('localhost:8000')
with p as page:
    for i, line in enumerate(page):
        print line
        if i > 5:
            break
    print page.headers
    print page.ls()

