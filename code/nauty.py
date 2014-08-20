""" Interface to the nauty package. """

from cStringIO import StringIO
import subprocess

from helper import load_graph6, write_graph6

def geng(until=None, minimal_vertex_degree=3, squarefree=True,
                            connected=False, canonical_labeling=False):
    """ Generates graphs using the geng util """
    i = 0
    while True:
        i += 1
        args = '-d%s' % minimal_vertex_degree
        if canonical_labeling:
            args += 'l'
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

def graph_to_nauty_format(g):
    """ Convert a graph to a format nauty understands. """
    io = StringIO()
    for i in g:
        io.write(str(i))
        io.write(' : ')
        for j in g[i]:
            io.write(str(j))
            io.write(' ')
        io.write(';\n')
    return io.getvalue()

def canonize(g):
    """ Canonizes the graph g. """
    p = subprocess.Popen(['labelg'],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    stdin=subprocess.PIPE)
    p.stdin.write(write_graph6(g))
    p.stdin.write("\n")
    p.stdin.close()
    return load_graph6(p.stdout.readline())

def orbits_of(g, fixed):
    """ Determines the orbits of g using dreadnaut
        with the given fixed nodes. """
    instructions = StringIO()
    instructions.write('n=%s\n' % len(g))
    instructions.write('g\n')
    instructions.write(graph_to_nauty_format(g))
    if fixed:
        instructions.write('f=[%s]\n' % '|'.join(map(str, fixed)))
    instructions.write('x\n')
    instructions.write('"start-of-the-orbits"\n')
    instructions.write('o\n')
    instructions.write('q\n')
    p = subprocess.Popen(['dreadnaut'],
                    stdin=subprocess.PIPE,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE)
    p.stdin.write(instructions.getvalue())
    orbit_line = p.stdout.read().split('start-of-the-orbits')[-1].replace(
                        '\n', '').strip()
    orbits = []
    for orbit_bit in orbit_line.strip().split(';'):
        orbit = set()
        if not orbit_bit:
            continue
        orbit_elements = orbit_bit.strip().split(' ')
        for orbit_element in orbit_elements:
            if ':' in orbit_element:
                start_end = map(int, orbit_element.split(':', 1))
                orbit.update(range(start_end[0], start_end[1]+1))
            else:
                orbit.add(int(orbit_element))
        orbits.append(orbit)
    return orbits
