
def orthogonality_graph(vs):
    """ Returns the orthogonality graph of a set of vectors. """
    g = dict()
    for i in xrange(len(vs)):
        g[i] = []
    for i, v in enumerate(vs):
        for j, w in enumerate(vs):
            if j >= i:
                continue
            if v[0] * w[0] + v[1]*w[1] + v[2]*w[2] == 0:
                g[i].append(j)
                g[j].append(i)
    return g

def full_grid(n):
    """ Returns all vectors on the n x n x n grid. """
    ret = list()
    for rv1 in xrange(n):
        for rv2 in xrange(n):
            v1 = 2*rv1 - n + 1
            v2 = 2*rv2 - n + 1
            ret.append((v1,v2,n-1))
            ret.append((v1,n-1,v2))
            ret.append((n-1,v1,v2))
    ret = list(set([x if x[0] >= 0 else tuple([-y for y in x]) for x in ret]))
    return ret
