from helper import load_graph6
from subgraph import find_mono

import multiprocessing
import subprocess
import os.path

def comp5():
    unemb = []
    with open('../graphs/min-unemb-fd3.g6') as f:
        for l in f:
            unemb.append((l[:-1], load_graph6(l[:-1])))
    if not os.path.exists('comp5/build/comp5'):
        ret = subprocess.call(['cmake', '..'], cwd='comp5/build')
        if ret != 0: raise RuntimeError, "cmake failed"
        subprocess.call(['make'], cwd='comp5/build')
        if ret != 0: raise RuntimeError, "make failed"
    worker_count = multiprocessing.cpu_count()
    for i in xrange(worker_count):
        p = multiprocessing.Process(target=worker,
                                    args=(i, worker_count, unemb))
        p.start()

def worker(worker_id, worker_count, unemb):
    possibly_embeddable_cache = {}
    for i in xrange(1, 14):
        p = subprocess.Popen(['geng -fc %s %s/%s | comp5/build/comp5'
                                % (i, worker_id, worker_count)],
                        stdout=subprocess.PIPE,
                        stderr=open('/dev/null', 'w'), shell=True)
        for l in p.stdout:
            possibly_embeddable = True
            g6, arity, pts, tpe = l[:-1].split(' ')
            if tpe in frozenset(['{00,01,10}',
                                 '{00,10,11}',
                                 '{00,01,11}']):
                continue
            g = load_graph6(g6)
            if g6 in possibly_embeddable_cache:
                possibly_embeddable = possibly_embeddable_cache[g6]
                if not possibly_embeddable:
                    continue
            else:
                for ugname, ug in unemb:
                    mono = find_mono(ug, g)
                    if mono is not None:
                        print '(found non embeddable)'
                        possibly_embeddable = False
                        break
                possibly_embeddable_cache[g6] = possibly_embeddable
            print l



if __name__ == '__main__':
    comp5()
