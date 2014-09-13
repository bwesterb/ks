import json
import time
import math
import os.path
import kyotocabinet
from pprint import pprint

def avg(l):
    return sum(l)/len(l)
def stddev(l):
    a = avg(l)
    r = 0.0
    for x in l:
        r += (a - x)**2
    return math.sqrt(r / len(l))

class Program(object):
    def main(self):
        path = 'db.kch'
        self.db = kyotocabinet.DB()
        if not self.db.open(path, kyotocabinet.DB.OREADER
                                | kyotocabinet.DB.ONOLOCK):
            raise RuntimeError
        n_workers = 0
        names = dict()
        n_todo = 0
        for key in self.db.match_prefix('todo-'):
            n_todo += 1
        n_stale = 0
        n_working = 0
        for key in self.db.match_prefix('working-'):
            if time.time() - json.loads(self.db.get(
                    'worker-'+self.db.get(key)))[1] > 200:
                n_stale += 1
            else:
                n_working += 1
        print 'n_stale:', n_stale
        print 'n_working', n_working
        print 'n_todo:', n_todo
        for key in self.db.match_prefix('worker-'):
            if time.time() - json.loads(self.db.get(key))[1] > 200:
                continue
            n_workers += 1
            name = key.split('-',1)[1].rsplit('-',1)[0]
            if not name in names:
                names[name] = 0
            names[name] += 1
        print 'number of workers: ', n_workers
        pprint(names)
        total_duration = 0.0
        total_graphs = 0
        eff_by_worker = {}
        N = 0
        N_error = 0
        candidates = []
        for key in self.db.match_prefix('result-'):
            data = json.loads(self.db.get(key))
            result = json.loads(data[0])
            if not 'graphs generated' in result[1]:
                N_error += 1
                continue
            candidates.extend(filter(lambda x: x, result[0].split('\n')))
            duration = data[2]
            graphs_generated =  int(result[1].split(
                            'graphs generated')[0].split('>Z')[1])
            worker = data[1].split('-')[0]
            if not worker in eff_by_worker:
                eff_by_worker[worker] = []
            eff_by_worker[worker].append(float(graphs_generated) / duration)
            total_graphs += graphs_generated
            N += 1
            total_duration += duration
        with open('21.g6', 'w') as f:
            f.write('\n'.join(candidates))
        print '%s/%s errors' % (N_error, N + N_error)
        print "At %.2f%%" % (N / 1000.0)
        print total_graphs, 'graphs generated'
        print len(candidates), 'candidates'
        print total_duration / 60.0 / 60.0 / 24.0, 'comp days'
        #print "%.3f days remaining" % ((total_duration  / float(N)) * (
        #                100000 - N) / n_workers / 60.0 / 60.0 / 24.0)
        for worker in eff_by_worker:
            print "%20s %20.2f +- %-20.2f %d" % (worker,
                            avg(eff_by_worker[worker]),
                            stddev(eff_by_worker[worker]),
                            len(eff_by_worker[worker]))



if __name__ == '__main__':
    Program().main()
