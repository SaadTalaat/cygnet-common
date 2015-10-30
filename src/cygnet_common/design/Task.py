import threading
import time


class TaskInterval(threading.Thread):
    def __init__(self, interval, task, args=None):
        self.task = task
        self.interval = interval
        self.args = args
        threading.Thread.__init__(self)
        self.setDaemon(True)
        print "[Task Interval] Registered"

    def run(self):
        print "[Task Interval] Running"
        while True:
            time.sleep(self.interval)
            if self.args:
                apply(self.task, self.args)
            else:
                apply(self.task)
