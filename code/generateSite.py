""" Generates the graph pages on the site. """

import os
import json
import binascii

from helper import load_graph6

import yaml
import pydot

class literal_str(unicode): pass
def yaml_literal_str_representer(dumper, data):
    return dumper.represent_scalar(u'tag:yaml.org,2002:str', data, style='|')
yaml.add_representer(literal_str, yaml_literal_str_representer)

def main():
    dirname = '../graphs/class'
    fns = os.listdir(dirname)
    for i, fn in enumerate(fns):
        if i % 10 == 0:
            print '%s/%s' % (i, len(fns))
        path = os.path.join(dirname, fn)
        with open(path) as f:
            result = json.load(f)
        graph_safe_name = fn.split('.')[0]
        graph_name = binascii.unhexlify(graph_safe_name)
        graph = load_graph6(graph_name)
        if len(graph) >= 14:
            continue
        dot = pydot.Dot('G', graph_type='graph', splines='true')
        for v in graph:
            dot.add_node(pydot.Node(str(v)))
        for v in graph:
            for w in graph[v]:
                if v >= w:
                    continue
                dot.add_edge(pydot.Edge(str(v), str(w)))
        image = graph_safe_name + '.svg'
        dot.write_svg(os.path.join('../site/smallGraphs/', image), prog='fdp')
        front_matter = {
                'layout': 'smallGraph',
                'unembeddableSubgraph': (result['subgraph'],
                                         binascii.hexlify(result['subgraph']),
                                         result['mono'])
                                            if 'subgraph' in result else None,
                'title': graph_name,
                'image': image,
                'reduce_script': literal_str(result['reduce-script'])
                                if 'reduce-script' in result else None,
                'safe_name': graph_safe_name,
                'n_vertices': len(graph),
                'embeddable': result.get('embeddable'),
                'minimally_unembeddable':
                        result.get('reason') == 'quantifier-elimination',
                'gridEmbeddable': result['grid']*2+3
                        if 'grid' in result else False,
                'embedding': result.get('embedding')}
        with open('../site/smallGraphs/%s.markdown' % graph_safe_name, 'w') as f:
            f.write('---\n')
            yaml.dump(front_matter, f, default_flow_style=False)
            f.write('---\n')


if __name__ == '__main__':
    main()
