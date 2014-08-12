# Generates random graphs

import random
import subprocess

from colorability import find_010coloring
from helper import load_graph6, write_graph6
from subgraph import find_mono

class Program():
    def check(self, g):
        self.checked += 1
        for hname, h in self.unemb:
            if find_mono(h, g):
                return
        print 'might be...', write_graph6(g)
        import sys
        sys.exit(1)

    def main(self):
        self.unemb = []
        self.checked = 0
        print 'loading unembeddable subgraphs ...'
        with open('../graphs/min-unemb-fd3.g6') as f:
            for l in f:
                self.unemb.append((l[:-1], load_graph6(l[:-1])))
        print 'randomly generating graphs ...'
        rg = subprocess.Popen(['randomGraph/rg'], stdout=subprocess.PIPE)
        for l in rg.stdout:
            g = load_graph6(l[:-1])
            assert find_010coloring(g) is None
            assert find_mono({0:[1,3], 1:[2,0], 2:[3,1], 3:[0,2]}, g) is None
            #assert min([len(g[v]) for v in g]) >= 3
            self.check(g)

if __name__ == '__main__':
    Program().main()
