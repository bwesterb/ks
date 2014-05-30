""" Computation 2: for those graphs that were found embeddable, but not
        <10-grid embeddable in computation 1, check <20-grid embeddable """


import os
import json
import msgpack
import binascii

from helper import write_graph6, load_graph6
from vectorsystem import full_grid, orthogonality_graph
from subgraph import find_mono

def load_grids():
    path = '../graphs/grids.msgpack'
    if os.path.exists(path):
        print 'Loading grids'
        with open(path) as f:
            return msgpack.load(f)
    print 'Computing grids'
    grids = []
    for i in xrange(24):
        vectors = full_grid(2*i+3)
        grids.append((orthogonality_graph(vectors),
                        vectors))
        print ' %s: %s vectors' % (i, len(vectors))
    with open(path, 'w') as f:
        msgpack.dump(grids, f)
    return grids

def main():
    grids = load_grids()
    dirpath = '../graphs/class'
    for fn in os.listdir(dirpath):
        path = os.path.join(dirpath, fn)
        with open(path) as f:
            result = json.load(f)
            if (result['reason'] != 'quantifier-elimination' or
                    not result['embeddable']):
                continue
            graph = load_graph6(binascii.unhexlify(fn.split('.')[0]))
            print fn
            for i, grid in tuple(enumerate(grids))[9:]:
                print i
                grid_graph, grid_vectors = grid
                mono = find_mono(graph, grid_graph)
                if mono is None:
                    continue
                print ' yes!'
                result['reason'] = 'grid-embeddable'
                result['gridEmbeddable'] = True
                result['grid'] = i
                result['embedding'] = [grid_vectors[x] for x in mono]
                with open(path, 'w') as f:
                    json.dump(result, f)
                break

if __name__ == '__main__':
    main()
