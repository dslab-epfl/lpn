#pragma once
#include<map>
#include <list>
#include <stack>
#include <memory>
#include <assert.h>
#include "place_transition.hh"

// Class to represent a graph
class Graph {
    int V; // No. of vertices'
 
    // Pointer to an array containing adjacency listsList
    std::list<int>* adj;
    std::map<std::string, int> str_int_id_map;
    std::map<int, std::string> int_str_id_map;
    std::map<int, BasePlace*> id_place_map;
    std::map<int, Transition*> id_trans_map;
    std::vector<std::string> seen_str_ids;
    int accId;
    // A function used by topologicalSort
    bool topologicalSortUtil(int v, bool visited[], bool* recStack, std::stack<int>& Stack, std::vector<int>& path);

 
public:
    Graph(int V); // Constructor
 
    // function to add an edge to graph
    int getSize();
    void addEdge(int v, int w);
    int strToIntId(const std::string& strId);
    bool isPlaceId(int id);
    BasePlace* intIdToPlaceObj(int intId);
    Transition* intIdToTransObj(int intId);
    int declPlaceWithStrId(const std::string& strId, BasePlace* place);
    int declTransWithStrId(const std::string& strId, Transition* trans);
 
    // prints a Topological Sort of the complete graph
    std::unique_ptr<std::stack<int>>  topologicalSort();
    void SCCUtil(int u, std::vector<int>& disc, std::vector<int>& low, 
                 std::stack<int>& st, std::vector<bool>& stackMember, 
                 std::vector<std::vector<int>>& sccResult);
    std::unique_ptr<std::vector<std::vector<int>>>  SCC();
    std::unique_ptr<Graph> buildSCCGraph(std::vector<int>&);
    
};


Graph::Graph(int V)
{
    this->V = V;
    accId = 0;
    adj = new std::list<int>[V];
}

int Graph::getSize()
{
    return this->V;
}

int Graph::strToIntId(const std::string& strId){
    assert(str_int_id_map.find(strId)!=str_int_id_map.end());
    return str_int_id_map[strId];
}

// or use variant
bool Graph::isPlaceId(int id){
    return id_place_map.find(id) != id_place_map.end();
}

BasePlace* Graph::intIdToPlaceObj(int intId){
   return id_place_map[intId];
}

Transition* Graph::intIdToTransObj(int intId){
    return id_trans_map[intId];
}

int Graph::declPlaceWithStrId(const std::string& strId, BasePlace* place){
    int id = accId++;
    id_place_map[id] = place;
    str_int_id_map[strId] = id;
    int_str_id_map[id] = strId;
    return 0;
}

int Graph::declTransWithStrId(const std::string& strId, Transition* trans){
    int id = accId++;
    id_trans_map[id] = trans;
    str_int_id_map[strId] = id;
    int_str_id_map[id] = strId;
    return 0;
}
 
 
void Graph::addEdge(int v, int w)
{
    printf("edge %d(%s) -> %d(%s)\n", v, int_str_id_map[v].c_str(),
                                     w, int_str_id_map[w].c_str());
    adj[v].push_back(w); // Add w to v’s list.
}

// A recursive function used by topologicalSort
bool Graph::topologicalSortUtil(int v, bool visited[], bool* recStack, std::stack<int>& Stack, std::vector<int>& path) {
    if (!visited[v]) {
        // Mark the current node as visited and part of the recursion stack
        visited[v] = true;
        recStack[v] = true;
        path.push_back(v);

        // Recur for all the vertices adjacent to this vertex
        for (int i : adj[v]) {
            if (!visited[i] && topologicalSortUtil(i, visited, recStack, Stack, path))
                return true;
            else if (recStack[i]) {
                path.push_back(i);  // Add the vertex that closes the cycle
                // Print the cycle
                std::cout << "Cycle detected: ";
                for (auto it = path.rbegin(); it != path.rend(); ++it) {
                    if (*it == i) {  // Print until the cycle completes
                        std::cout << *it << " ";
                        break;
                    }
                    std::cout << *it << " ";
                }
                std::cout << std::endl;
                return true;
            }
        }
    }

    // Remove the vertex from the recursion stack and push it to the stack
    recStack[v] = false;
    Stack.push(v);
    path.pop_back();  // Remove the vertex from the current path
    return false;
}

// The function to do Topological Sort. It uses recursive
// topologicalSortUtil()
std::unique_ptr<std::stack<int>> Graph::topologicalSort() {
    std::unique_ptr<std::stack<int>> stack_ptr = std::make_unique<std::stack<int>>();
    std::stack<int>& Stack = *stack_ptr;
    std::vector<int> path; // To store the path traversed

    // Mark all the vertices as not visited and not part of recursion stack
    bool* visited = new bool[V];
    bool* recStack = new bool[V];
    for (int i = 0; i < V; i++) {
        visited[i] = false;
        recStack[i] = false;
    }

    // Call the recursive helper function to store Topological Sort
    // starting from all vertices one by one
    for (int i = 0; i < V; i++) {
        if (!visited[i]) {
            if (topologicalSortUtil(i, visited, recStack, Stack, path)) {
                return nullptr;
            }
        }
    }

    // Print contents of stack if no cycle was detected
    return stack_ptr;

}

void Graph::SCCUtil(int u, std::vector<int>& disc, std::vector<int>& low, 
                 std::stack<int>& st, std::vector<bool>& stackMember, 
                 std::vector<std::vector<int>>& sccResult) {
        static int time = 0;

        // Initialize discovery time and low value
        disc[u] = low[u] = ++time;
        st.push(u);
        stackMember[u] = true;

        // Go through all vertices adjacent to this
        for (int v : adj[u]) {
            // If v is not visited yet, then recur for it
            if (disc[v] == -1) {
                SCCUtil(v, disc, low, st, stackMember, sccResult);
                // Check if the subtree rooted with 'v' has a 
                // connection to one of the ancestors of 'u'
                low[u] = std::min(low[u], low[v]);
            }
            // Update low value of 'u' only if 'v' is still in stack
            else if (stackMember[v] == true)
                low[u] = std::min(low[u], disc[v]);
        }

        // head node found, pop the stack and generate an SCC
        int w = 0; // To store stack extracted vertices
        if (low[u] == disc[u]) {
            std::vector<int> currentSCC;
            while (st.top() != u) {
                w = st.top();
                currentSCC.push_back(w);
                stackMember[w] = false;
                st.pop();
            }
            w = st.top();
            currentSCC.push_back(w);
            stackMember[w] = false;
            st.pop();
            // Add the SCC to the result
            sccResult.push_back(currentSCC);
        }
    }

std::unique_ptr<std::vector<std::vector<int>>> Graph::SCC() {
        std::vector<int> disc(V, -1), low(V, -1);
        std::stack<int> st;
        std::vector<bool> stackMember(V, false);
        std::vector<std::vector<int>> sccResult;

        // Call the recursive helper function to find strongly 
        // connected components in DFS tree with vertex 'i'
        for (int i = 0; i < V; i++)
            if (disc[i] == -1)
                SCCUtil(i, disc, low, st, stackMember, sccResult);

        int i = 0;
        for(auto& sccg : sccResult){
            printf("group %d\n", i++);
            for(int node_id : sccg){
                if(isPlaceId(node_id)){
                   printf("%s\n", intIdToPlaceObj(node_id)->id.c_str());
                }else{
                   printf("%s\n", intIdToTransObj(node_id)->id.c_str());
                }
            }
        }

        return std::make_unique<std::vector<std::vector<int>>>(sccResult);
    }

std::unique_ptr<Graph> Graph::buildSCCGraph(std::vector<int>& nodeToSCCIndex){
    auto sccs = SCC(); // Get SCCs using previously defined SCC function
    int numSCCs = sccs->size();
    auto sccGraph = std::make_unique<Graph>(numSCCs);
    // Map each node to its SCC index
    for (int i = 0; i < numSCCs; ++i) {
        for (int node : (*sccs)[i]) {
            nodeToSCCIndex[node] = i;
        }
    }
    // Add edges to the SCC graph
    for (int i = 0; i < V; ++i) {
        int sccIndexOfI = nodeToSCCIndex[i];
        for (int j : adj[i]) {
            int sccIndexOfJ = nodeToSCCIndex[j];
            if (sccIndexOfI != sccIndexOfJ) {
                sccGraph->addEdge(sccIndexOfI, sccIndexOfJ);
            }
        }
    }
    return sccGraph;
}