""" Determines proporition of squarefree graphs with minimal
    vertex degree three for which every node is in a triangle. """

from nauty import geng

from colorability import find_triangles, build_node_to_triangles

def comp7():
    n = 0
    N = 0
    prev_n = 0
    for g in geng():
        if len(g) != prev_n:
            prev_n = len(g)
            print len(g), n, N
        N += 1
        triangles = find_triangles(g)
        node_to_triangles = build_node_to_triangles(g, triangles)
        if all(node_to_triangles.values()):
            n += 1

if __name__ == '__main__':
    comp7()
