#!/usr/bin/env python
# vim:set ts=8 sw=4 sts=4 et:

# Copyright (c) 2012 Serban Giuroiu
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

# ------------------------------------------------------------------------------

import fsevents
import os.path
import Queue
import subprocess
import threading

PATH = os.path.normpath(os.path.expanduser('~/stage'))
REMOTE_HOST = 'server'
REMOTE_PATH = os.path.normpath('~/stage')

SYNC_COMMAND = "rsync --archive --hard-links --delete --verbose --human-readable --progress " + \
               "--exclude='.*.swp' -e ssh " + PATH + "/ " + REMOTE_HOST + ":" + REMOTE_PATH

queue = Queue.Queue(maxsize=1)
timer = None

def sync():
    subprocess.call(SYNC_COMMAND, shell=True)
    print '--------------------------------------------------------------------------------'


def process_queue(queue):
    while queue.get():
        sync()


def schedule_sync():
    try:
        queue.put(True, block=False)
    except Queue.Full:
        pass


def fs_event_callback(path, mask):
    global timer

    if timer and timer.is_alive():
        timer.cancel()

    timer = threading.Timer(0.1, schedule_sync)
    timer.start()


# ------------------------------------------------------------------------------

# TODO: Figure out why moving this stuff into the if block doesn't work

observer = fsevents.Observer()
observer.start()

stream = fsevents.Stream(fs_event_callback, PATH)
observer.schedule(stream)

if __name__ == '__main__':
    sync()

    queue_processor = threading.Thread(target=process_queue, args=[queue])
    queue_processor.run()

    observer.run()
