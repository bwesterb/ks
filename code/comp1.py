""" Computation 1: decides for square-free graphs of minimal vertex order 3,
    whether they are embeddable. """

import os
import json
import binascii

import nauty
from helper import write_graph6, load_graph6
from vectorsystem import full_grid, orthogonality_graph
from subgraph import find_mono
from sphereEmbeddable import find_assignments, check_sphere_embeddability

class LenientJsonEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, set):
            return list(obj)
        return json.JSONEncoder.default(self, obj)

def check_for_result(graph):
    if os.path.exists("../graphs/class/%s.json" % binascii.hexlify(
                                                    write_graph6(graph))):
        return True
    return False

def write_result(graph, result):
    with open('../graphs/class/%s.json' % binascii.hexlify(write_graph6(graph)),
            'w') as f:
        json.dump(result, f, cls=LenientJsonEncoder)

def main():
    minimal_unembeddable = []
    print 'Loading previously computed minimally unembeddable fd3 graphs'
    with open('../graphs/min-unemb-fd3.g6', 'r') as f:
        for l in f:
            minimal_unembeddable.append(load_graph6(l[:-1]))
    print 'Computing grids'
    grids = []
    for i in xrange(10):
        vectors = full_grid(2*i+3)
        grids.append((orthogonality_graph(vectors),
                        vectors))
    print 'Considering graphs'
    for graph in nauty.geng(15, canonical_labeling=True):
        if check_for_result(graph):
            continue
        result = {}
        print write_graph6(graph)
        found_unemb_subgraph = False
        print ' checking for unembeddable subgraph'
        for unemb in minimal_unembeddable:
            mono = find_mono(unemb, graph)
            if mono is not None:
                result['embeddable'] = False
                result['reason'] = 'unembeddable-subgraph'
                result['subgraph'] = write_graph6(unemb)
                result['mono'] = mono
                print '  yes'
                found_unemb_subgraph = True
                break
        if found_unemb_subgraph:
            write_result(graph, result)
            continue
        print ' computing cross-product assignments'
        assignments = find_assignments(graph)
        assignment_index = 0
        guessing = False
        grid_index = 0
        embeddable = None
        decided_embeddability = False
        decided_grid_embeddability = False
        while ((assignment_index < len(assignments)
                        and not decided_embeddability) or
                    (grid_index < len(grids)
                        and not decided_grid_embeddability)):
            if (assignment_index < len(assignments)
                    and not decided_embeddability):
                assignment = assignments[assignment_index]
                if guessing:
                    print ('  checking embeddability with assignment %s with'+
                            ' guessing') % assignment_index
                else:
                    print ('  checking embeddability with assignment %s'+
                            ' without guessing') % assignment_index
                ret = check_sphere_embeddability(graph, assignment, guessing)
                if ret is not None:
                    embeddability, reduce_script = ret
                    if embeddability:
                        print '   yes'
                    else:
                        print '   no'
                    result['embeddable'] = embeddability
                    result['reason'] = 'quantifier-elimination'
                    result['assignment'] = assignment
                    result['reduce-script'] = reduce_script
                    if not embeddability:
                        decided_grid_embeddability = True
                        minimal_unembeddable.append(graph)
                        with open('../graphs/min-unemb-fd3.g6', 'a') as f:
                            f.write(write_graph6(graph))
                            f.write("\n")
                    decided_embeddability = True
                else:
                    if not guessing:
                        guessing = True
                    else:
                        assignment_index += 1
                        guessing = False
                        if assignment_index == len(assignments):
                            break
            if (grid_index < len(grids) and not decided_grid_embeddability):
                print ' checking %s-grid embeddability' % grid_index
                grid_graph, grid_vectors = grids[grid_index]
                mono = find_mono(graph, grid_graph)
                if mono is not None:
                    print '   yes'
                    decided_grid_embeddability = True
                    decided_embeddability = True
                    result['reason'] = 'grid-embeddable'
                    result['embeddable'] = True
                    result['gridEmbeddable'] = True
                    result['grid'] = grid_index
                    result['embedding'] = [grid_vectors[x] for x in mono]
                else:
                    grid_index += 1
        write_result(graph, result)
        

if __name__ == '__main__':
    main()
