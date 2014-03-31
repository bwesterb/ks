from helper import load_graph6

def plot(g):
    print g

if __name__ == '__main__':
    with open('../graphs/ks33.g6') as f:
        plot(load_graph6(f.readline()[:-1]))
