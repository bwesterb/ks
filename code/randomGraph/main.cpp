#include <unordered_map>
#include <functional>
#include <algorithm>
#include <stdexcept>
#include <iostream>
#include <fstream>
#include <cassert>
#include <random>
#include <vector>
#include <array>
#include <stack>
#include <map>

typedef uint8_t node_t;
typedef std::array<node_t, 3> triangle_t;
typedef std::array<node_t, 2> edge_t;

class base_graph
{
public:
    void find_010coloring();
};

template<typename T>
inline void vector_remove(std::vector<T> & v, const T & item)
{
    v.erase(std::remove(v.begin(), v.end(), item), v.end());
}

bool is_edge_of_triangle(edge_t e, triangle_t t)
{
    if(e[0] == t[0] && e[1] == t[1])
        return true;
    if(e[0] == t[1] && e[1] == t[2])
        return true;
    if(e[0] == t[0] && e[1] == t[2])
        return true;
    return false;
}

edge_t edge(node_t a, node_t b)
{
    std::array<node_t, 2> ret = {{a, b}};
    if(ret[0] > ret[1])
        std::swap(ret[1], ret[0]);
    return ret;
}

triangle_t triangle(node_t a, node_t b, node_t c)
{
    std::array<node_t, 3> ret = {{a, b, c}};
    if(ret[0] > ret[1])
        std::swap(ret[1], ret[0]);
    if(ret[0] > ret[2])
        std::swap(ret[2], ret[0]);
    if(ret[1] > ret[2])
        std::swap(ret[1], ret[2]);
    return ret;
}

template<typename T>
class popremoveset
{
private:
    std::map<T, size_t> map;
    std::vector<bool> removed;
    std::vector<T> list;
    bool ready;

public:
    popremoveset()
                : map(), removed(), list(), ready(false)
    {
    }

    void shuffle()
    {
        if(this->ready)
            throw std::logic_error("already shuffled");
        std::random_shuffle(this->list.begin(), this->list.end());
        for (size_t i = 0; i < this->list.size(); i++)
            this->map[this->list[i]] = i;
        this->ready = true;
    }

    T pop()
    {
        assert(this->ready);
        while(!this->list.empty()) {
            T ret = this->list.back();
            bool removed = this->removed.back();
            this->list.pop_back();
            this->removed.pop_back();
            if (!removed) {
                this->map.erase(ret);
                return ret;
            }
        }
        assert(false);
    }

    bool empty()
    {
        assert(this->ready);
        return this->map.empty();
    }

    void remove(T t)
    {
        assert(this->ready);
        assert(this->map.count(t));
        size_t index = this->map[t];
        this->map.erase(t);
        this->removed[index] = true;
    }

    bool contains(T t)
    {
        assert(this->ready);
        return this->map.count(t) == 1;
    }

    void add(T t)
    {
        assert(!this->ready);
        this->list.push_back(t);
        this->removed.push_back(false);
    }

    void emplace(T&& t)
    {
        assert(!this->ready);
        this->list.emplace_back(t);
        this->removed.push_back(false);
    }
};

template<std::size_t N>
class graph : public base_graph
{
private:
    std::array<popremoveset<node_t>, N> candidates_by_node;
    popremoveset<edge_t> candidates;
    bool use_candidates_by_node;

    // basic structure
    std::array<std::array<bool, N>, N> adj;
    std::array<std::vector<node_t>, N> neigh;

    // derived structure
    std::array<std::array<bool, N>, N> ts_adj;
    std::array<std::vector<node_t>, N> ts_neigh;
    std::array<std::vector<triangle_t>, N> triangles_of;

public:
    graph()
                : candidates_by_node(), candidates(), adj(), neigh(),
                         ts_adj(), ts_neigh(), triangles_of()
    {
        this->use_candidates_by_node = true;
        for (int i = 0; i < N; i++) {
            for (int j = i+1; j < N; j++) {
                this->candidates_by_node[i].emplace(j);
                this->candidates_by_node[j].emplace(i);
            }
        }
        for (int i = 0; i < N; i++)
            this->candidates_by_node[i].shuffle();
    }

    // Removes an edge.
    // WARNING this will make this object inconsistent as it does not update
    // several structures like ts_adj.
    void _remove(const edge_t& e)
    {
        assert(this->adj[e[0]][e[1]]);
        this->adj[e[0]][e[1]] = false;
        this->adj[e[1]][e[0]] = false;
        vector_remove(this->neigh[e[0]], e[1]);
        vector_remove(this->neigh[e[1]], e[0]);
        std::vector<triangle_t> triangles = this->triangles_of[e[0]];
        for (triangle_t t : triangles) {
            if (!is_edge_of_triangle(e, t))
                continue;
            vector_remove(this->triangles_of[t[0]], t);
            vector_remove(this->triangles_of[t[1]], t);
            vector_remove(this->triangles_of[t[2]], t);
        }
    }

    void add(const edge_t& e)
    {
        // Update basic structures
        this->adj[e[0]][e[1]] = true;
        this->adj[e[1]][e[0]] = true;
        this->neigh[e[0]].emplace_back(e[1]);
        this->neigh[e[1]].emplace_back(e[0]);

        // Update triangles_of
        for(node_t v : this->neigh[e[0]]) {
            if(this->adj[v][e[1]]) {
                triangle_t t = triangle(e[0], e[1], v);
                this->triangles_of[e[0]].emplace_back(t);
                this->triangles_of[e[1]].emplace_back(t);
                this->triangles_of[v].emplace_back(t);
            }
        }

        // Update twostep
        for(node_t v : this->neigh[e[0]]) {
            if (v == e[1])
                continue;
            assert(!this->ts_adj[e[1]][v]);
            this->ts_adj[e[1]][v] = true; 
            this->ts_adj[v][e[1]] = true; 
            this->ts_neigh[e[1]].emplace_back(v);
            this->ts_neigh[v].emplace_back(e[1]);
        }
        for(node_t v : this->neigh[e[1]]) {
            if (v == e[0])
                continue;
            assert(!this->ts_adj[e[0]][v]);
            this->ts_adj[e[0]][v] = true; 
            this->ts_adj[v][e[0]] = true; 
            this->ts_neigh[e[0]].emplace_back(v);
            this->ts_neigh[v].emplace_back(e[0]);
        }

        // Prevent squares
        for(node_t v : this->ts_neigh[e[0]])
            this->forbid(e[1], v);
        for(node_t v : this->ts_neigh[e[1]])
            this->forbid(e[0], v);
        for(node_t v : this->neigh[e[0]])
            for(node_t w : this->neigh[e[1]])
                this->forbid(v, w);
    }

    void forbid(node_t e1, node_t e2)
    {
        if (this->use_candidates_by_node) {
            if (this->candidates_by_node[e1].contains(e2)) {
                this->candidates_by_node[e1].remove(e2);
                this->candidates_by_node[e2].remove(e1);
            }
            return;
        }
        edge_t e = edge(e1, e2);
        if(this->candidates.contains(e))
            this->candidates.remove(e);
    }

    bool compare_nodes(const node_t& a, const node_t& b)
    {
        if (this->triangles_of[a].size() > this->triangles_of[b].size())
            return true;
        if (this->neigh[a].size() > this->neigh[b].size())
            return true;
        return false;
    }

    bool find_010coloring()
    {
        // Types used in algorithm
        struct frame_t {
            std::vector<node_t> todo;
            std::array<uint8_t, N> val; 
            bool choice;
        };

        std::stack<frame_t> stack;

        // Create inital frames
        frame_t initial_frame1;
        for(node_t i = 0; i < N; i++) {
            initial_frame1.val[i] = 2;
            initial_frame1.todo.push_back(i);
        }
        // std::sort(initial_frame1.todo.begin(),
        //           initial_frame1.todo.end(),
        //           std::bind(&graph<N>::compare_nodes,
        //                     this,
        //                         std::placeholders::_1,
        //                         std::placeholders::_2));

        frame_t initial_frame2 = initial_frame1;
        initial_frame1.choice = true;
        initial_frame2.choice = false;
        stack.push(initial_frame2);
        stack.push(initial_frame1);

        unsigned long steps = 0;
        while(!stack.empty())
        {
            bool consistent = true;
            steps++;
            frame_t f = stack.top();
            stack.pop();
            node_t node;
            while(true) {
                if (f.todo.empty()) {
                    return true;
                }
                node = f.todo.back();
                f.todo.pop_back();
                if (f.val[node] == 2)
                    break;
            }
            std::stack<node_t> to_consider;
            f.val[node] = f.choice ? 1 : 0;
            to_consider.push(node);

            while(!to_consider.empty() && consistent) {
                // Consider the consequences of our choice
                node_t node = to_consider.top();
                to_consider.pop();
                if(f.val[node] == 1) {
                    // All neighbours must be 0
                    for(node_t other : this->neigh[node]) {
                        if(f.val[other] == 1) {
                            consistent = false;
                            break;
                        }
                        if(f.val[other] == 2) {
                            f.val[other] = 0;
                            to_consider.push(other);
                        }
                    }
                } else { // f.val[node] == 0
                    // If there is one node left undetermined in one of its
                    // triangles, then it must be a 1.
                    for (triangle_t triangle : this->triangles_of[node]) {
                        node_t other1, other2;
                        if (triangle[0] == node) {
                            other1 = triangle[1];
                            other2 = triangle[2];
                        } else if (triangle[1] == node) {
                            other1 = triangle[0];
                            other2 = triangle[2];
                        } else {
                            other1 = triangle[0];
                            other2 = triangle[1];
                        }
                        if(f.val[other1] == 2 && f.val[other2] == 0) {
                            f.val[other1] = 1;
                            to_consider.push(other1);
                        } else if(f.val[other2] == 2 && f.val[other1] == 0) {
                            f.val[other2] = 1;
                            to_consider.push(other2);
                        } else if (f.val[other1] == 0 && f.val[other2] == 0) {
                            consistent = false;
                            break;
                        }
                    }
                }
            }
            if (!consistent)
                continue;
            frame_t new_frame1 = f;
            frame_t new_frame2 = f;
            new_frame1.choice = true;
            new_frame2.choice = false;
            stack.push(new_frame2);
            stack.push(new_frame1);
        }
        return false;
    }

    bool run()
    {
        // First, make sure every node has at least vertex degree 3.
        for(int i = 0; i < N; i++) {
            if(this->neigh[i].size() < 3) {
                if(this->candidates_by_node[i].empty()) {
                    std::cerr << "can't reach -d3" << std::endl;
                    return false;
                }
                node_t n = this->candidates_by_node[i].pop();
                this->candidates_by_node[n].remove(i);
                this->add(edge(i, n));
            }
        }

        // Collect all candidates
        // TODO improve performance
        for (int i = 0; i < N; i++) {
            while (!this->candidates_by_node[i].empty()) {
                node_t n = this->candidates_by_node[i].pop();
                this->candidates_by_node[n].remove(i);
                this->candidates.emplace(edge(i, n));
            }
        }

        this->candidates.shuffle();
        this->use_candidates_by_node = false;
        std::vector<edge_t> path;

        // Now, add as many edges as possible
        while (!this->candidates.empty()) {
            edge_t e = this->candidates.pop();
            this->add(e);
            path.emplace_back(e);
        }
        
        // Check colorability
        std::string output;
        bool found_coloring = false;
        while(!this->find_010coloring()) {
            found_coloring = true;
            output = this->to_graph6();
            this->_remove(path.back());
            path.pop_back();
            if(path.empty())
                break;
        }
        if(found_coloring)
            std::cout << output << std::endl;
        return found_coloring;
    }

    std::string to_graph6()
    {
        std::string ret;
        ret.push_back(63 + N);
        uint8_t v = 0;
        uint8_t e = 0;
        for (node_t y = 0; y < N; y++) {
            for (node_t x = 0; x < y; x++) {
                e++;
                v *= 2;
                if (this->adj[x][y])
                    v++;
                if (e == 6) {
                    ret.push_back(63 + v);
                    v = 0;
                    e = 0;
                }
            }
        }
        for(; e < 6; e++)
            v *= 2;
        ret.push_back(63 + v);
        return ret;
    }
};

int main()
{
    int N = 0, n = 0;
    while(true) {
        graph<31> g;
        N++;
        if(g.run())
            n++;
        if(N % 10000 == 0)
            std::cerr << n << "/" << N << std::endl;
    }
}
