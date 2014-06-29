""" Computation 4: checks whether the graphs found by Felix Arends
        are embeddable. """

from helper import load_arends, load_graph6
from subgraph import find_mono
from colorability import find_010coloring

import os.path
import json
import os

def main():
    candidates = []
    unemb = []
    print 'Reading candidates ...'
    base = '../graphs/arends'
    for fn in os.listdir(base):
        if not fn.endswith('.txt'):
            continue
        path = os.path.join(base, fn)
        with open(path) as f:
            g = load_arends(f.read())
            candidates.append((fn, g))
    print 'Checking properties of candidates ...'
    for gname, g in candidates:
        if find_010coloring(g) is not None:
            print gname, 'seems 010colorable'
    print 'Reading minimal unembeddable graphs ...'
    with open('../graphs/min-unemb-fd3.g6') as f:
        for l in f:
            unemb.append((l[:-1], load_graph6(l[:-1])))
    print 'Checking subgraphs ...'
    candidate_left = False
    for i, g_pair in enumerate(candidates):
        g_name, g = g_pair
        ok = False
        for j, ug_pair in enumerate(unemb):
            ugname, ug = ug_pair
            mono = find_mono(ug, g)
            if mono is None:
                continue
            print g_name, 'has unembeddable subgraph', ugname
            ok = True
            break
        if not ok:
            candidate_left = True
            print g_name, 'might be embeddable'
    if not candidate_left:
        print 'All these graphs are unembeddable'


if __name__ == '__main__':
    main()
