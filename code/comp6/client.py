import sys
import zmq
import json
import time
import random
import threading
import subprocess
import multiprocessing

class Client(object):
    def worker(self):
        while True:
            with self.cond:
                self.cond.wait()
                if self.task == -1:
                    continue
                task = self.task
            print 'working on task %s' % task
            self.result = subprocess.Popen(['./run-batch', str(task)],
                                stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE).communicate()
            print '     done!'
            with self.cond:
                self.cond.notify()

    def main(self):
        self.cond = threading.Condition()
        self.result = None
        self.task = -1
        self.start_time = 0
        identifier = str(random.randint(0,10000000))
        if len(sys.argv) > 1:
            identifier = sys.argv[1] + '-' + identifier
        self.worker = threading.Thread(target=self.worker)
        self.worker.start()
        zctx = zmq.Context()
        s = zctx.socket(zmq.REQ)
        s.connect('tcp://sw.w-nz.com:5558')
        while True:
            s.send_json(['ping', identifier, self.task])
            s.recv_json()
            with self.cond:
                if self.result is not None:
                    while True:
                        s.send_json(['result', identifier, self.task,
                                                    json.dumps(self.result),
                                            time.time() - self.start_time])
                        msg = s.recv_json()
                        if msg[0] == 'ok':
                            break
                        print 'result not accepted: %s; retrying' % msg
                        time.sleep(1)
                    self.task = -1
                    self.result = None
                if self.task == -1:
                    s.send_json(['request', identifier])
                    msg = s.recv_json()
                    if msg[0] == 'done':
                        return
                    self.task = msg[1]
                    self.start_time = time.time()
                    self.cond.notify()
                self.cond.wait(60)

def main():
    Client().main()

if __name__ == '__main__':
    if len(sys.argv) > 2:
        cpu_count = int(sys.argv[2])
    else:
        cpu_count = multiprocessing.cpu_count()
    for i in xrange(cpu_count):
        print 'starting worker', i
        threading.Thread(target=main).start()
