""" Methods to check properties of graphs related to 010-coloring. """

def build_node_to_triangles(adj, triangles):
    """ Build a node to triangle dictionary for a graph given by adj
            with given triangles. """
    node_to_triangles = dict()
    for node in adj:
        node_to_triangles[node] = set()
    for triangle in triangles:
        for node in triangle:
            node_to_triangles[node].add(triangle)
    return node_to_triangles

def find_triangles(adj):
    """ Find triangles of the graph given by adj. """
    triangles = set()
    for p in adj:
        for n1 in adj[p]:
            for n2 in adj[p]:
                if n1 == n2:
                    continue
                if n1 in adj[n2]:
                    key = tuple(sorted([n1, n2, p]))
                    triangles.add(key)
    return triangles

def find_ncoloring(adj, n):
    """ Tries to find a n-coloring of the graph given by adj. """
    mapping = {}
    for node in adj:
        mapping[node] = None
    todo = list(adj)
    stack = [(mapping, tuple(todo))]
    N = 0
    while stack:
        N += 1
        mapping, todo = stack.pop()
        if not todo:
            return mapping
        node = todo[0]
        allowed = set(range(n))
        for neighbour in adj[node]:
            color = mapping[neighbour]
            if color in allowed:
                allowed.remove(color)
        for color in allowed:
            new_mapping = dict(mapping)
            new_mapping[node] = color
            stack.append((new_mapping, todo[1:]))
    return None

def find_010coloring(adj):
    """ Tries to find a 010-coloring of the graph given by adj. """
    triangles = find_triangles(adj)
    node_to_triangles = build_node_to_triangles(adj, triangles)
    mapping = {}
    for node in adj:
        mapping[node] = None
    todo = list(adj)
    todo.sort(key=lambda node: -len(adj[node]))
    stack = [(mapping, tuple(todo))]
    N = 0
    while stack:
        N += 1
        mapping, todo = stack.pop()
        if not todo:
            return mapping
        node = todo[0]
        todo = todo[1:]
        can_be_true = True
        can_be_false = True
        for neighbour in adj[node]:
            if mapping[neighbour] is True:
                can_be_true = False
                break
        for triangle in node_to_triangles[node]:
            other1, other2 = frozenset(triangle) - frozenset((node,))
            if mapping[other1] is False and mapping[other2] is False:
                can_be_false = False
            if mapping[other1] is True or mapping[other2] is True:
                can_be_true = False
        if can_be_false:
            new_mapping = dict(mapping)
            new_mapping[node] = False
            stack.append((new_mapping, todo))
        if can_be_true:
            new_mapping = dict(mapping)
            new_mapping[node] = True
            stack.append((new_mapping, todo))

def find_color_fixed_pairs(adj):
    """ Tries to find a pair of points in the graph given by adj,
        for which not all possible colorings are possible. """
    triangles = find_triangles(adj)
    node_to_triangles = build_node_to_triangles(adj, triangles)
    mapping = {}
    to_be_seen = {}
    pairs = set()
    for v in adj:
        for w in adj:
            if v >= w:
                continue
            pairs.add((v, w))
    for a in (True, False):
        for b in (True, False):
            to_be_seen[a,b] = set(pairs)
    for v in adj:
        for w in adj[v]:
            if v >= w:
                continue
            to_be_seen[True, True].remove((v, w))
    for node in adj:
        mapping[node] = None
    todo = list(adj)
    todo.sort(key=lambda node: -len(adj[node]))
    stack = [(mapping, tuple(todo))]
    N = 0
    while stack:
        N += 1
        mapping, todo = stack.pop()
        if not todo:
            for v in mapping:
                for w in mapping:
                    if v >= w:
                        continue
                    key = (v, w)
                    clr = (mapping[v], mapping[w])
                    if key in to_be_seen[clr]:
                        to_be_seen[clr].remove(key)
            finished = True
            for clr in to_be_seen:
                if to_be_seen[clr]:
                    finished = False
                    break
            if finished:
                return None
            continue
        node = todo[0]
        todo = todo[1:]
        can_be_true = True
        can_be_false = True
        for neighbour in adj[node]:
            if mapping[neighbour] is True:
                can_be_true = False
                break
        for triangle in node_to_triangles[node]:
            other1, other2 = frozenset(triangle) - frozenset((node,))
            if mapping[other1] is False and mapping[other2] is False:
                can_be_false = False
            if mapping[other1] is True or mapping[other2] is True:
                can_be_true = False
        if can_be_false:
            new_mapping = dict(mapping)
            new_mapping[node] = False
            stack.append((new_mapping, todo))
        if can_be_true:
            new_mapping = dict(mapping)
            new_mapping[node] = True
            stack.append((new_mapping, todo))
    # Convert to types
    ret = {}
    for clr, pairs in to_be_seen.iteritems():
        for pair in pairs:
            if not pair in ret:
                ret[pair] = []
            ret[pair].append(clr)
    return ret

def find_color_fixed_points(adj):
    """ Tries to find a point in the graph given by adj, which must always
        have the same color. """
    triangles = find_triangles(adj)
    node_to_triangles = build_node_to_triangles(adj, triangles)
    mapping = {}
    to_be_seen_true = set(adj)
    to_be_seen_false = set(adj)
    for node in adj:
        mapping[node] = None
    todo = list(adj)
    todo.sort(key=lambda node: -len(adj[node]))
    stack = [(mapping, tuple(todo))]
    N = 0
    while stack:
        N += 1
        mapping, todo = stack.pop()
        if not todo:
            for node in mapping:
                if mapping[node]:
                    if node in to_be_seen_true:
                        to_be_seen_true.remove(node)
                else:
                    if node in to_be_seen_false: 
                        to_be_seen_false.remove(node)
                if not to_be_seen_false and not to_be_seen_true:
                    return None
            continue
        node = todo[0]
        todo = todo[1:]
        can_be_true = True
        can_be_false = True
        for neighbour in adj[node]:
            if mapping[neighbour] is True:
                can_be_true = False
                break
        for triangle in node_to_triangles[node]:
            other1, other2 = frozenset(triangle) - frozenset((node,))
            if mapping[other1] is False and mapping[other2] is False:
                can_be_false = False
            if mapping[other1] is True or mapping[other2] is True:
                can_be_true = False
        if can_be_false:
            new_mapping = dict(mapping)
            new_mapping[node] = False
            stack.append((new_mapping, todo))
        if can_be_true:
            new_mapping = dict(mapping)
            new_mapping[node] = True
            stack.append((new_mapping, todo))
    return (to_be_seen_false, to_be_seen_true)
