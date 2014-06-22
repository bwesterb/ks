""" Computation 3: check whether the candidate graphs contain unembeddable
        subgraphs. """

from helper import write_graph6, load_graph6
from subgraph import find_mono

import binascii
import os.path
import json

def main():
    candidates = []
    unemb = []
    print 'Reading candidates ...'
    with open('../graphs/candidates.g6') as f:
        for l in f:
            candidates.append((l[:-1], load_graph6(l[:-1])))
    print 'Reading minimal unembeddable graphs ...'
    with open('../graphs/min-unemb-fd3.g6') as f:
        for l in f:
            unemb.append((l[:-1], load_graph6(l[:-1])))
    print 'Checking subgraphs ...'
    for i, g_pair in enumerate(candidates):
        gname, g = g_pair
        gsname = binascii.hexlify(gname)
        path = '../graphs/candidates/%s.json' % gsname
        if os.path.exists(path):
            continue
        if i % 100 == 0:
            print i, len(candidates)
        for j, ug_pair in enumerate(unemb):
            ugname, ug = ug_pair
            mono = find_mono(ug, g)
            if mono is None:
                continue
            break
        with open(path, 'w') as f:
            json.dump({'subgraph': ugname,
                       'mono': mono}, f)

if __name__ == '__main__':
    main()
