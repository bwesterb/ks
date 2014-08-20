// Computation 5
// Find all graphs squarefree connected graphs with less than 16 vertices
// which contain non-trivial 1- or 2-types.
// Use comp5.py to run the computation

#include <functional>
#include <iostream>
#include <memory>
#include <fstream>
#include <array>
#include <set>
#include <stack>
#include <stdexcept>
#include <cassert>
#include <vector>

const size_t MAX_N = 16;

typedef uint8_t node_t;
typedef std::array<node_t, 3> triangle_t;


class base_graph
{
public:
    virtual void find_nontrivial_types() = 0;
    virtual ~base_graph() {};
};

std::array<node_t, 3> triangle(node_t a, node_t b, node_t c)
{
    std::array<node_t, 3> ret = {{a, b, c}};
    if(ret[0] > ret[1])
        std::swap(ret[1], ret[0]);
    if(ret[1] > ret[2])
        std::swap(ret[1], ret[2]);
    return ret;
}

template<std::size_t N>
class graph : public base_graph
{
    static_assert(0 < N && N < 62, "Only 0 < N < 62 is supported");

private:
    std::string graph6;
    std::array<std::array<bool, N>, N> adj;
    std::array<std::vector<node_t>, N> neigh;
    std::array<std::vector<triangle_t>, N> triangles_of;

public:
    graph (std::string graph6)
                : graph6(graph6), adj(), neigh(), triangles_of()
    {
        // First, sanity checks.
        if(graph6.empty())
            throw std::runtime_error("graph6 should not be empty");
        unsigned int runtime_N =  graph6[0] - 63;
        if(runtime_N != N)
            throw std::runtime_error("graph size unsupported");

        // Now, load the adjacency matrix and neighbourhood lists
        int x = 0, y = 1;
        for(int i = 1; i < graph6.length(); i++) {
            for(int j = 0; j < 6; j++) {
                bool value = (((graph6[i] - 63) >> (5 - j)) & 1) == 1;
                this->adj[x][y] = value;
                this->adj[y][x] = value;
                if(value) {
                    this->neigh[x].push_back(y);
                    this->neigh[y].push_back(x);
                }
                if(++x == y) {
                    y++;
                    if (y == N)
                        break;
                    x = 0;
                }
            }
            if (y == N)
                break;
        }

        // Now, find the triangles
        for(node_t x = 0; x < N; x++) {
            for(node_t y : this->neigh[x]) {
                if (y < x) continue;
                for(node_t z: this->neigh[y]) {
                    if (z < y) continue;
                    if(!this->adj[z][x]) continue;
                    triangle_t t = triangle(x, y, z);
                    this->triangles_of[x].push_back(t);
                    this->triangles_of[y].push_back(t);
                    this->triangles_of[z].push_back(t);
                }
            }
        }
    }

    bool compare_nodes(const node_t& a, const node_t& b)
    {
        if (this->triangles_of[a].size() > this->triangles_of[b].size())
            return true;
        if (this->neigh[a].size() > this->neigh[b].size())
            return true;
        return false;
    }

    virtual void find_nontrivial_types()
    {
        std::array<std::array<std::array<std::array<bool, 2>, 2>, N>, N> seen;

        for (node_t i = 0; i < N; i++)
            for (node_t j = i; j < N; j++)
                for (int ci : {0, 1})
                    for (int cj : {0, 1})
                        seen[i][j][ci][cj] = false;

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
            bool should_continue = false;
            steps++;
            frame_t f = stack.top();
            stack.pop();
            node_t node;
            while(true) {
                if (f.todo.empty()) {
                    // TODO now we update seen at the "leafs".  If we update it,
                    //      instead, in the nodes, it will be faster.

                    for (node_t i = 0; i < N; i++)
                        for (node_t j = i; j < N; j++)
                            seen[i][j][f.val[i]][f.val[j]] = true;

                    should_continue = true;
                    break;
                }
                node = f.todo.back();
                f.todo.pop_back();
                if (f.val[node] == 2)
                    break;
            }

            if (should_continue)
                continue;

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

        for (node_t i = 0; i < N; i++) {
            for (node_t j = i; j < N; j++) {
                bool nontrivial_type = false;
                for (int ci : {0, 1}) {
                    for (int cj : {0, 1}) {
                        // Missing (0, 1) and (1, 0) for the a pair of the
                        // same node, is trivial.
                        if (i == j && ci != cj)
                            continue;

                        // Missing (1, 1) for adjacent nodes is trivial
                        if (this->adj[i][j] && ci && cj)
                            continue;

                        if (!seen[i][j][ci][cj])
                            nontrivial_type = true;
                    }
                }

                if (!nontrivial_type)
                    continue;

                std::cout << this->graph6 << " ";

                if (i == j)
                    std::cout << "1-type (" << (int)i << ") ";
                else
                    std::cout << "2-type (" << (int)i << "," << (int)j << ") ";

                std::cout << "{";
                bool first = true;

                if(i == j) {
                    for (int c : {0, 1}) {
                        if (seen[i][i][c][c]) {
                            if (first) first = false;
                            else std::cout << ",";
                            std::cout << (c ? "1" : "0");
                        }
                    }
                } else {
                    for (int ci : {0, 1}) {
                        for (int cj : {0, 1}) {
                            if (seen[i][j][ci][cj]) {
                                if (first) first = false;
                                else std::cout << ",";
                                std::cout << (ci ? "1" : "0")
                                          << (cj ? "1" : "0");
                            }
                        }
                    }
                }

                std::cout << "}" << std::endl;
            }
        }
    }
};

template<std::size_t N>
std::unique_ptr<base_graph>
_load_graph6(std::size_t n, std::string graph6)
{
    static_assert(0 < N && N < MAX_N, "Unsupported graph size");
    if (n == N)
        return std::unique_ptr<base_graph>(new graph<N>(graph6));
    return _load_graph6<N+1>(n, graph6);
}

template<>
std::unique_ptr<base_graph>
_load_graph6<MAX_N>(std::size_t n, std::string graph6)
{
    throw std::runtime_error("Unsupported graph size");
}

std::unique_ptr<base_graph>
load_graph6(std::string graph6)
{
    unsigned int n =  graph6[0] - 63;
    return _load_graph6<1>(n, graph6);
}

int main()
{
    std::string line;
    while (std::getline(std::cin, line)) {
        std::unique_ptr<base_graph> graph(load_graph6(line));
        graph->find_nontrivial_types();
    }
}
