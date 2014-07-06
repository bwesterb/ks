# Generates random graphs

import random

from colorability import find_010coloring
from helper import write_graph6, load_graph6
from subgraph import find_mono

class Program():
    def check(self, g):
        self.checked += 1
        for hname, h in self.unemb:
            if find_mono(h, g):
                return
        print 'might be...', write_graph6(g)

    def main(self, N):
        self.unemb = []
        self.checked = 0
        print 'loading unembeddable subgraphs ...'
        with open('../graphs/min-unemb-fd3.g6') as f:
            for l in f:
                self.unemb.append((l[:-1], load_graph6(l[:-1])))
        print 'randomly generating graphs ...'
        runs = 0
        while True:
            runs += 1
            if runs % 1000 == 0:
                print self.checked, runs
            self.one_run(N)

    def one_run(self, N):
        def norm(edge):
            if edge[0] < edge[1]:
                return edge
            return (edge[1], edge[0])
        path = []
        # initialize empty graph
        g = {} # adjacency dictionary
        for v in xrange(N):
            g[v] = set()
        unconnected = set()
        candidates = set()
        for v in xrange(N):
            for w in xrange(N):
                if v >= w:
                    continue
                unconnected.add((v,w))
                candidates.add((v,w))
        # Randomly add edges
        while candidates:
            edge = random.choice(tuple(candidates))
            path.append(edge)
            candidates.remove(edge)
            g[edge[0]].add(edge[1])
            g[edge[1]].add(edge[0])
            for v in g[edge[0]]:
                for w in g[edge[1]]:
                    forbidden = norm((v, w))
                    if forbidden in candidates:
                        candidates.remove(forbidden)
            for v in g[edge[0]]:
                for w in g[v]:
                    forbidden = norm((w, edge[1]))
                    if forbidden in candidates:
                        candidates.remove(forbidden)
            for v in g[edge[1]]:
                for w in g[v]:
                    forbidden = norm((w, edge[0]))
                    if forbidden in candidates:
                        candidates.remove(forbidden)
        for edge in reversed(path):
            if find_010coloring(g) is not None:
                break
            self.check(g)
            g[edge[0]].remove(edge[1])
            g[edge[1]].remove(edge[0])

if __name__ == '__main__':
    Program().main(31)
