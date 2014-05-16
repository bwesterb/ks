
def is_subgraph_of(smallg, largeg):
    """ Checks whether smallg is a subgraph of largeg """
    todo = list(smallg)
    avail = frozenset(largeg)
    todo.sort(key=lambda node: -len(smallg[node]))
    mapping = {}
    for node in smallg:
        mapping[node] = None
    stack = [(mapping, tuple(todo), avail)]
    N = 0
    while stack:
        N += 1
        mapping, todo, avail = stack.pop()
        if not todo:
            return True
        node = todo[0]
        todo = todo[1:]
        for target in avail:
            if len(largeg[target]) < len(smallg[node]):
                continue
            ok = True
            for neighbour in smallg[node]:
                if mapping[neighbour] is None:
                    continue
                if mapping[neighbour] not in largeg[target]:
                    ok = False
                    break
            if not ok:
                continue
            new_mapping = dict(mapping)
            new_avail = avail - frozenset([target])
            new_mapping[node] = target
            stack.append((new_mapping, todo, new_avail))
    return False
