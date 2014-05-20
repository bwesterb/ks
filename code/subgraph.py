import igraph

def to_igraph(g):
    ret = igraph.Graph()
    ret.add_vertices(len(g))
    for v in g:
        for w in g[v]:
            if v >= w: continue
            ret.add_edges([(v, w)])
    return ret

def find_mono(smallg, largeg):
    """ Tries to find an embedding of smallg into largeg.
        Returns None if there is none. """
    found_one, mapping = to_igraph(largeg).subisomorphic_lad(to_igraph(smallg),
                            return_mapping=True)
    if not found_one:
        return None
    return mapping
