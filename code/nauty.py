""" Interface to the nauty package. """

import subprocess
from helper import load_graph6

def geng(until=None, minimal_vertex_degree=3, squarefree=True,
                            connected=False):
    """ Generates graphs using the geng util """
    i = 0
    while True:
        i += 1
        args = '-d%s' % minimal_vertex_degree
        if squarefree:
            args += 'f'
        if connected:
            args += 'c'
        p = subprocess.Popen(['geng', args, str(i)],
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE)
        while True:
            l = p.stdout.readline()
            if not l:
                break
            yield load_graph6(l[:-1])
        if i == until:
            return

