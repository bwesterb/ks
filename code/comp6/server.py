import zmq
import time
import json
import os.path
import kyotocabinet

BITS=100000

class Server(object):
    def __init__(self):
        self.workers = {}
    def open_db(self):
        path = 'db.kch'
        self.db = kyotocabinet.DB()
        if os.path.exists(path):
            print 'Opening db ...'
            if not self.db.open(path, kyotocabinet.DB.OWRITER):
                raise RuntimeError
            n_replaced = 0
            for key in self.db.match_prefix('result-'):
                data = json.loads(self.db.get(key))
                result = json.loads(data[0])
                if not 'graphs generated' in result[1]:
                    n_replaced += 1
                    self.db.set(key.replace('result-', 'todo-'), None)
                    self.db.remove(key)
            for key in self.db.match_prefix('working-'):
                if time.time() - json.loads(self.db.get(
                        'worker-'+self.db.get(key)))[1] > 200:
                    n_replaced += 1
                    self.db.set(key.replace('working-', 'todo-'), None)
                    self.db.remove(key)
            print '  reset {} results'.format(n_replaced)
            print '    done'
            return
        print 'Creating db ...'
        if not self.db.open(path, kyotocabinet.DB.OWRITER |
                                  kyotocabinet.DB.OCREATE):
            raise RuntimeError
        for i in xrange(BITS):
            self.db.set('todo-{}'.format(i), None)
        print '     done'

    def main(self):
        self.open_db()
        self.last_sync = 0
        zctx = zmq.Context()
        s = zctx.socket(zmq.REP)
        s.bind('tcp://*:5558')
        while True:
            msg = s.recv_json()
            if time.time() - self.last_sync > 100:
                self.last_sync = time.time()
                self.db.synchronize()
            if not isinstance(msg, list) or not msg:
                s.send_json(['error', 'malformed request'])
                continue
            if msg[0] == 'ping':
                if (not len(msg) == 3 or not isinstance(msg[1], str)
                                or not isinstance(msg[2], int)):
                    s.send_json(['error', 'malformed request'])
                    continue
                worker_id = msg[1]
                task = msg[2]
                self.db.set('worker-{}'.format(worker_id),
                            json.dumps([task, time.time()]))
                s.send_json(['pong'])
                continue
            if msg[0] == 'request':
                if (not len(msg) == 2 or not isinstance(msg[1], str)):
                    s.send_json(['error', 'malformed request'])
                    continue
                worker_id = msg[1]
                keys = self.db.match_prefix('todo-', 1)
                if not keys:
                    s.send_json(['none'])
                    continue
                key = keys[0]
                self.db.remove(key)
                task = int(key.split('-')[1])
                self.db.set('working-{}'.format(task), worker_id)
                s.send_json(['task', task])
                continue
            if msg[0] == 'result':
                if (not len(msg) == 5 or not isinstance(msg[1], str)
                                       or not isinstance(msg[2], int)
                                       or not isinstance(msg[3], basestring)
                                       or not isinstance(msg[4], float)):
                    s.send_json(['error', 'malformed request'])
                    continue
                worker_id = msg[1]
                task = msg[2]
                result = msg[3]
                duration = msg[4]
                self.db.remove('working-{}'.format(task))
                self.db.set('result-{}'.format(task), 
                            json.dumps([result, worker_id, duration]))
                s.send_json(['ok'])
                print 'result for {} from {} in {}'.format(task, worker_id,
                                        duration)
                continue
            s.send_json(['error', 'unknown message'])

if __name__ == '__main__':
    Server().main()
