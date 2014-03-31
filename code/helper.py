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
