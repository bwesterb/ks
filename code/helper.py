from cStringIO import StringIO

def write_graph6(g):
    """ Writes a graph to graph6 format """
    ret = ''
    if len(g) > 62:
        raise NotImplementedError
    keys = list(g)
    ret += chr(len(g) + 63)
    bitmap = []
    x = 0
    y = 1
    while True:
        bitmap.append(int(keys[y] in g[keys[x]]))
        x += 1
        if x == y:
            x = 0
            y += 1
            if y == len(g):
                break
    for i in xrange(0, len(bitmap), 6):
        v = 0
        for m in xrange(6):
            v *= 2
            if i + m < len(bitmap):
                v += bitmap[i + m]
        ret += chr(v + 63)
    return ret

def load_graph6(s):
    """ Loads a graph from graph6 format """
    c = s[0]
    if not 63 <= ord(c) and ord(c) <= 63 + 62:
        raise NotImplementedError
    n = ord(c) - 63
    bitmap = []
    for i in xrange(1, len(s)):
        for j in xrange(6):
            bitmap.append(((ord(s[i]) - 63) >> (5 - j)) & 1 == 1)
    x = 0
    y = 1
    g = {}
    for i in xrange(n):
        g[i] = set()
    for value in bitmap:
        if value:
            g[x].add(y)
            g[y].add(x)
        x += 1
        if x == y:
            x = 0
            y += 1
            if y == n:
                break
    return g

def load_arends(g):
    """ Loads a graph stored in the format used by Felix Arends. """
    f = StringIO(g)
    ret = {}
    n = int(f.readline()[:-1])
    for i in xrange(n):
        ret[i] = set()
    for v in xrange(n):
        bits = map(int, f.readline()[:-1].split(' '))
        assert bits[0] == len(bits) - 1
        for w in bits[1:]:
            ret[v].add(w)
    for v in ret:
        for w in ret[v]:
            assert v in ret[w]
    return ret
