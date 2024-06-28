import networkx as nx
import inspect
import json
import numpy as np
from sklearn.cluster import AgglomerativeClustering
from scipy.spatial.distance import pdist, squareform
import matplotlib.pyplot as plt
import inspect  # Import the inspect module to get the source code of functions
import json
from ..lpn_place import Place
from typing import List

def get_params_value(func):
    param_str = ""
    if len(func.args) == 0:
        return ""
    args = func.args
    param_types = func.edge_expr.param_types.items()
    for i, (key, expected_type) in enumerate(param_types):
        value = args[i]
        if isinstance(value, Place):
            value = value.id
        if isinstance(value, List):
            for i, v in enumerate(value):
                if isinstance(v, Place):
                    value[i] = v.id
        param_str += f"{key} = {value}\\n"
        # print(f"{key}:{expected_type.__name__} = {value}")
    return param_str

def generate_cytoscape_js(places, transitions):
    
    def string_similarity(str1, str2):
        # Example similarity metric (e.g., Jaccard similarity)
        return int(str1[:2] == str2[:2])
        set1 = set(str1)
        set2 = set(str2)
        return len(set1.intersection(set2)) / len(set1.union(set2))

    def create_distance_matrix(node_ids, similarity_func):
        # Create a square matrix initialized with zeros
        size = len(node_ids)
        distance_matrix = np.zeros((size, size))
        
        # Populate the distance matrix with 1 - similarity
        for i in range(size):
            for j in range(size):
                if i != j:
                    similarity = similarity_func(node_ids[i], node_ids[j])
                    distance_matrix[i][j] = 1 - similarity
                else:
                    distance_matrix[i][j] = 0  # Zero distance to itself
        
        return distance_matrix

    # Example usage with node IDs
    node_ids = [node.id for node in places] + [transition.id for transition in transitions]
    distance_matrix = create_distance_matrix(node_ids, string_similarity)

    # Perform clustering
    clustering = AgglomerativeClustering(n_clusters=15, affinity='precomputed', linkage='complete')
    clustering.fit(distance_matrix)
    cluster = {}
    clusters = set()
    # Assign cluster labels to nodes in the NetworkX graph
    for i, node_id in enumerate(node_ids):
        cluster[node_id] = clustering.labels_[i]
        clusters.add(cluster[node_id])
    print(cluster)
    nodes = []
    for place in places:
        type_annotations = json.dumps(list(place.type_annotations))  # Assuming type_annotations is a dictionary or list
        nodes.append(f"{{ data: {{ id: '{place.id}', type: 'place', group: \"nodes\", parent: '{cluster[place.id]}', type_annotations: {type_annotations} }} }}")
        # nodes.append(f"{{ data: {{ id: '{place.id}', type: 'place' }} }}")
    for transition in transitions:
        func_name = transition.delay_f.edge_expr.name
        func_body = get_params_value(transition.delay_f)
        func_body += inspect.getsource(transition.delay_f.edge_expr.func).replace('\n', '\\n').replace('"', '\\"')
        if transition.pip != None:
            func_name = func_name + "& pip_func=" + transition.pip.edge_expr.name
            extra_func_body = "\n=== pip function ==="
            extra_func_body = get_params_value(transition.pip)
            extra_func_body += inspect.getsource(transition.pip.edge_expr.func).replace('\n', '\\n').replace('"', '\\"')
            func_body += "\\n\\n"+extra_func_body     

        nodes.append(f"{{ data: {{ id: '{transition.id}', type: 'transition', group: \"nodes\", parent: '{cluster[transition.id]}', label: '{func_name}', functionBody: \"{func_body}\" }} }}")

    edges = []
    for transition in transitions:
        for i, place in enumerate(transition.p_input):
            func_name = transition.pi_w[i].edge_expr.name
            func_body = get_params_value(transition.pi_w[i])
            func_body += inspect.getsource(transition.pi_w[i].edge_expr.func).replace('\n', '\\n').replace('"', '\\"')
            if len(transition.pi_guard) > 0:
                if transition.pi_guard[i] != None:
                    func_name = func_name + "& guard=" + transition.pi_guard[i].edge_expr.name
                    extra_func_body = inspect.getsource(transition.pi_guard[i].edge_expr.func).replace('\n', '\\n').replace('"', '\\"')
                func_body += "\\n\\n"+extra_func_body     

            edges.append(f"{{ data: {{ id: 'e_{place.id}_{transition.id}', source: '{place.id}', target: '{transition.id}', label: '{func_name}', functionBody: \"{func_body}\" }} }}")
        
        for i, place in enumerate(transition.p_output):
            func_name = transition.po_w[i].edge_expr.name
            func_body = get_params_value(transition.po_w[i])
            func_body += inspect.getsource(transition.po_w[i].edge_expr.func).replace('\n', '\\n').replace('"', '\\"')
            edges.append(f"{{ data: {{ id: 'e_{transition.id}_{place.id}', source: '{transition.id}', target: '{place.id}', label: '{func_name}', functionBody: \"{func_body}\" }} }}")
    
    elements = ',\n      '.join(nodes + edges)

    # nodes = []
    # for place in places:
    #     nodes.append(f"{{ data: {{ id: '{place.id}', type: 'place' }} }}")
    # for transition in transitions:
    #     nodes.append(f"{{ data: {{ id: '{transition.id}', type: 'transition' }} }}")
    
    # edges = []
    # for transition in transitions:
    #     for i, place in enumerate(transition.p_input):
    #         func_name = transition.pi_w[i].__name__ if callable(transition.pi_w[i]) else str(transition.pi_w[i])
    #         edges.append(f"{{ data: {{ id: 'e_{place.id}_{transition.id}', source: '{place.id}', target: '{transition.id}', label: '{func_name}' }} }}")
    #     for i, place in enumerate(transition.p_output):
    #         func_name = transition.po_w[i].__name__ if callable(transition.po_w[i]) else str(transition.po_w[i])
    #         edges.append(f"{{ data: {{ id: 'e_{transition.id}_{place.id}', source: '{transition.id}', target: '{place.id}', label: '{func_name}' }} }}")
    
    # elements = ',\n      '.join(nodes + edges)
    
    html_content = f"""<!DOCTYPE html>
<html>
<head>
  <title>Petri Net Visualization</title>
  <script src='https://cdnjs.cloudflare.com/ajax/libs/cytoscape/3.19.1/cytoscape.min.js'></script>
  <style>
    #cy {{
      width: 80vw;
      height: 100vh;
      border: 1px solid black;
      float: left;
    }}
    #functionInfo {{
      white-space: pre;
      width: 19vw;
      height: 100vh;
      float: right;
      overflow-y: scroll;
      border: 1px solid black;
    }}
    #container {{
        display: grid;
        grid-template-columns: 4fr 1fr;
    }}
  </style>
</head>
<body>

<div>
  <label for="searchBox">Search: </label>
  <input type="text" id="searchBox">
</div>
<div id="container">
  <div id='cy'></div>
  <div id='functionInfo'>Additional info panel, click edges/nodes to see</div>
</div>

<script>
  var cy = cytoscape({{
    container: document.getElementById('cy'),
    elements: [
      {elements}
    ],
    style: [
      {{
        selector: 'node[type="place"]',
        style: {{
          'background-opacity': 0, 
          'background-color': 'transparent',
          'border-color': 'black',
          'border-width': 2,
          'label': 'data(id)'
        }}
      }},
      {{
        selector: 'node[type="transition"]',
        style: {{
          'background-opacity': 0, 
          'background-color': 'transparent',
          'border-color': 'black',
          'border-width': 2,
          'shape': 'polygon',
          'shape-polygon-points': '-0.5 -1 0.5 -1 0.5 1 -0.5 1', 
          'label': 'data(id)'
        }}
      }},
      {{
        selector: 'edge',
        style: {{
           'label': 'data(label)',
           'curve-style': 'bezier',
           'target-arrow-shape': 'triangle-backcurve',
           'line-color': 'grey',
           'target-arrow-color': 'grey',
           'width': '2px',
           'arrow-scale': 2

        }}
      }}
    ],
    
    layout: {{
        name: 'breadthfirst',
        directed: true,
    }}

  }});
  

   // Initial font size, shape size, and edge width
    var initialFontSize = 20;
    var initialShapeSize = 30;
    var initialEdgeWidth = 4;
    var initialBorderWidth = 2;
    var initialArrowScale = 2;

    cy.on('zoom', function(event) {{
        var zoomLevel = cy.zoom();
        var newFontSize = initialFontSize / zoomLevel;
        var newShapeSize = initialShapeSize / zoomLevel;
        var newEdgeWidth = initialEdgeWidth / zoomLevel;
        var newBorderWidth = initialBorderWidth / zoomLevel;
        var newArrowScale = initialArrowScale / zoomLevel;
        
        cy.style()
        .selector('node')
        .style({{
            'font-size': newFontSize + 'px',
            'width': newShapeSize + 'px',
            'height': newShapeSize + 'px',
            'border-width': newBorderWidth
        }})
        .selector('edge')
        .style({{
            'font-size': newFontSize + 'px',
            'width': newEdgeWidth,
            'text-opacity': 0,
            'arrow-scale': newArrowScale
        }})
        .update();
    }});

    function resetStyles() {{
        cy.nodes().forEach(function(node) {{
            node.style({{
                'background-opacity': 0, 
                'background-color': 'transparent',
                'border-color': 'black',
                'border-width': 2,
                'border-opacity': 1,
                'text-opacity': 1
            }});
        }});
        cy.edges().forEach(function(edge) {{
            edge.style({{
                'curve-style': 'bezier',
                'target-arrow-shape': 'triangle',
                'line-color': 'grey',
                'target-arrow-color': 'grey',
                'width': '2px',
                'opacity': 1 
            }});
        }});
    }}

    function dimAllNodes() {{
        cy.nodes().forEach(function(node) {{
        node.style({{
            'background-color': 'transparent',
            'border-color': 'black',
            'border-opacity': 0.2,
            'text-opacity': 0.2
        }});
        }});
    }}

    function dimAllEdges() {{
        cy.edges().style({{
            'line-color': 'grey',
            'text-opacity': 0,
            'opacity': 0.2 
        }});
    }}

    function highlightConnectedEdges(node) {{
        node.connectedEdges().style({{
            'line-color': 'grey',
            'text-opacity': 1,
            'opacity': 1
        }});
    }}


    function highlightNode(node) {{
        node.style({{
            'background-opacity': 0, 
            'background-color': 'transparent',
            'border-color': 'black',
            'border-width': 2,
            'border-opacity': 1,
            'text-opacity': 1
        }});
        node.connectedEdges().forEach(function(edge) {{
        edge.connectedNodes().forEach(function(connectedNode) {{
            connectedNode.style({{
            'background-opacity': 0, 
            'background-color': 'transparent',
            'border-color': 'black',
            'border-width': 2,
            'border-opacity': 1,
            'text-opacity': 1
            }});
        }});
        edge.style({{ 'text-opacity': 1 }});  // Show edge label
        }});
    }}
    
    cy.on('tap', 'node', function(event) {{
        resetStyles();  // Reset all nodes to their default style
        dimAllNodes();  // Dim all nodes
        dimAllEdges();  // Dim all edges
        var tappedNode = event.target;
        highlightNode(tappedNode);  // Highlight the tapped node and its connected nodes
        highlightConnectedEdges(tappedNode);  // Highlight edges connected to the tapped node
        if (tappedNode.data('type') === 'place') {{
            const typeAnnotations = tappedNode.data('type_annotations');
            document.getElementById('functionInfo').innerText = `Place Annotations: \n${{JSON.stringify(typeAnnotations, null, 2)}}`;
        }}
        if (tappedNode.data('type') === 'transition') {{
            const functionName = tappedNode.data('label');
            const functionBody = tappedNode.data('functionBody');  // Assuming you've stored the function body here
            document.getElementById('functionInfo').innerText = `Delay Function: ${{functionName}}\n\nBody:\n${{functionBody}}`;
        }}
    }});

    cy.on('tap', 'edge', function(evt){{
        const edge = evt.target;
        console.log("Function Body: ", edge.data('functionBody'));
        const functionName = edge.data('label');
        const functionBody = edge.data('functionBody');  // Assuming you've stored the function body here
        document.getElementById('functionInfo').innerText = `Function: ${{functionName}}\n\nBody:\n${{functionBody}}`;
    }});
    
    cy.on('tap', function(event) {{
        if (event.target === cy) {{
            resetStyles();
        }}
    }});

    function handleSearch() {{
      const searchBox = document.getElementById('searchBox');
      searchBox.addEventListener('input', function() {{
        const query = searchBox.value;
        resetStyles();  // Reset styles before highlighting new node

        if (query) {{
          const node = cy.getElementById(query);
          if (node.length) {{  // Check if node exists
            resetStyles();  // Reset all nodes to their default style
            dimAllNodes();  // Dim all nodes
            dimAllEdges();  // Dim all edges
            highlightNode(node);
            highlightConnectedEdges(node);
          }}
        }}
      }});
    }}

    handleSearch();

</script>

</body>
</html>"""
    
    with open("petri_net_visualization.html", "w") as f:
        f.write(html_content)

# Your Place and Transition classes and example objects would go here
# ...

# Example usage:
# generate_cytoscape_js(places, transitions)

def extract_edges(transitions):
    arcs = []
    for transition in transitions:
        for i, place in enumerate(transition.p_input):
            func_name = transition.pi_w[i].__name__ if callable(transition.pi_w[i]) else str(transition.pi_w[i])
            arcs.append((place.id, transition.id, func_name))
        for i, place in enumerate(transition.p_output):
            func_name = transition.po_w[i].__name__ if callable(transition.po_w[i]) else str(transition.po_w[i])
            arcs.append((transition.id, place.id, func_name))
    return arcs


def lpn_visualize(places, transitions):
    generate_cytoscape_js(places, transitions)


def generate_cytoscape_js_graph_only(places, transitions, html_file, clock_value, active_transition):
    
    def string_similarity(str1, str2):
        # Example similarity metric (e.g., Jaccard similarity)
        return int(str1[:2] == str2[:2])
        set1 = set(str1)
        set2 = set(str2)
        return len(set1.intersection(set2)) / len(set1.union(set2))

    def create_distance_matrix(node_ids, similarity_func):
        # Create a square matrix initialized with zeros
        size = len(node_ids)
        distance_matrix = np.zeros((size, size))
        
        # Populate the distance matrix with 1 - similarity
        for i in range(size):
            for j in range(size):
                if i != j:
                    similarity = similarity_func(node_ids[i], node_ids[j])
                    distance_matrix[i][j] = 1 - similarity
                else:
                    distance_matrix[i][j] = 0  # Zero distance to itself
        
        return distance_matrix

    # Example usage with node IDs
    node_ids = [node.id for node in places] + [transition.id for transition in transitions]
    distance_matrix = create_distance_matrix(node_ids, string_similarity)

    # Perform clustering
    # clustering = AgglomerativeClustering(n_clusters=15, affinity='precomputed', linkage='complete')
    # clustering.fit(distance_matrix)
    # cluster = {}
    # clusters = set()
    # # Assign cluster labels to nodes in the NetworkX graph
    # for i, node_id in enumerate(node_ids):
    #     cluster[node_id] = clustering.labels_[i]
    #     clusters.add(cluster[node_id])
    # print(cluster)
    nodes = []
    for place in places:
        token_count = place.token_len()
        type_annotations = json.dumps(list(place.type_annotations))  # Assuming type_annotations is a dictionary or list
        if token_count > 0:
            nodes.append(f"{{ data: {{ id: '{place.id}', type: 'place', token_count: '{place.id} [ {token_count} ]', type_annotations: {type_annotations} }} }}")
        else:
            nodes.append(f"{{ data: {{ id: '{place.id}', type: 'place', token_count: '{place.id}', type_annotations: {type_annotations} }} }}")

    for transition in transitions:
        func_name = transition.delay_f.edge_expr.name
        func_body = get_params_value(transition.delay_f)
        func_body += inspect.getsource(transition.delay_f.edge_expr.func).replace('\n', '\\n').replace('"', '\\"')
        if transition.pip != None:
            func_name = func_name + "& pip_func=" + transition.pip.edge_expr.name
            extra_func_body = "\n=== pip function ==="
            extra_func_body = get_params_value(transition.pip)
            extra_func_body += inspect.getsource(transition.pip.edge_expr.func).replace('\n', '\\n').replace('"', '\\"')
            func_body += "\\n\\n"+extra_func_body     

        nodes.append(f"{{ data: {{ id: '{transition.id}', type: 'transition', label: '{func_name}' }} }}")

    edges = []
    for transition in transitions:
        for i, place in enumerate(transition.p_input):
            func_name = transition.pi_w[i].edge_expr.name
            func_body = get_params_value(transition.pi_w[i])
            func_body += inspect.getsource(transition.pi_w[i].edge_expr.func).replace('\n', '\\n').replace('"', '\\"')
            if len(transition.pi_guard) > 0:
                if transition.pi_guard[i] != None:
                    func_name = func_name + "& guard=" + transition.pi_guard[i].edge_expr.name
                    extra_func_body = inspect.getsource(transition.pi_guard[i].edge_expr.func).replace('\n', '\\n').replace('"', '\\"')
                func_body += "\\n\\n"+extra_func_body     

            edges.append(f"{{ data: {{ id: 'e_{place.id}_{transition.id}', source: '{place.id}', target: '{transition.id}', label: '{func_name}' }} }}")
        
        for i, place in enumerate(transition.p_output):
            func_name = transition.po_w[i].edge_expr.name
            func_body = get_params_value(transition.po_w[i])
            func_body += inspect.getsource(transition.po_w[i].edge_expr.func).replace('\n', '\\n').replace('"', '\\"')
            edges.append(f"{{ data: {{ id: 'e_{transition.id}_{place.id}', source: '{transition.id}', target: '{place.id}', label: '{func_name}' }} }}")
    
    elements = ',\n      '.join(nodes + edges)

    html_content = f"""<!DOCTYPE html>
<html>
<head>
  <title>Petri Net Visualization</title>
  <script src='https://cdnjs.cloudflare.com/ajax/libs/cytoscape/3.19.1/cytoscape.min.js'></script>
  <style>
    #cy {{
      width: 80vw;
      height: 100vh;
      border: 1px solid black;
      float: left;
    }}
    #clock {{
      font-size: 60px;
      position: absolute;
      top: 20px;
      right: 20px;
      background: white;
      padding: 10px;
      border-radius: 10px;
      border: 1px solid #ccc;
    }}
    #container {{
        display: grid;
        grid-template-columns: 4fr 1fr;
    }}
  </style>
</head>
<body>

<div id="container">
  <div id='cy'></div>
  <div id='clock'>Clock: {clock_value}</div>
</div>

<script>
  var cy = cytoscape({{
    container: document.getElementById('cy'),
    elements: [
      {elements}
    ],
    style: [
      {{
        selector: 'node[type="place"]',
        style: {{
        'content': 'data(token_count)', 
        'color': 'red',
        'font-size': '40px',
        'background-opacity': 0, 
        'background-color': 'transparent',
        'border-color': 'black',
        'border-width': 2,
        'shape': 'ellipse',
        }}
      }},
      {{
        selector: 'node[type="transition"]',
        style: {{
          'background-opacity': 0, 
          'background-color': 'transparent',
          'border-color': 'black',
          'border-width': 2,
          'shape': 'polygon',
          'shape-polygon-points': '-0.5 -1 0.5 -1 0.5 1 -0.5 1', 
          'label': 'data(id)'
        }}
      }},
      {{
        selector: 'edge',
        style: {{
           'label': 'data(label)',
           'curve-style': 'bezier',
           'target-arrow-shape': 'triangle-backcurve',
           'line-color': 'grey',
           'target-arrow-color': 'grey',
           'width': '2px',
           'arrow-scale': 2

        }}
      }}
    ],
    
    layout: {{
        name: 'breadthfirst',
        directed: true,
    }}

  }});

   // Initial font size, shape size, and edge width
    var initialFontSize = 20;
    var initialShapeSize = 30;
    var initialEdgeWidth = 4;
    var initialBorderWidth = 2;
    var initialArrowScale = 2;

    cy.on('zoom', function(event) {{
        var zoomLevel = cy.zoom();
        var newFontSize = initialFontSize / zoomLevel;
        var newShapeSize = initialShapeSize / zoomLevel;
        var newEdgeWidth = initialEdgeWidth / zoomLevel;
        var newBorderWidth = initialBorderWidth / zoomLevel;
        var newArrowScale = initialArrowScale / zoomLevel;
        
        cy.style()
        .selector('node')
        .style({{
            'font-size': newFontSize + 'px',
            'width': newShapeSize + 'px',
            'height': newShapeSize + 'px',
            'border-width': newBorderWidth
        }})
        .selector('edge')
        .style({{
            'font-size': newFontSize + 'px',
            'width': newEdgeWidth,
            'text-opacity': 0,
            'arrow-scale': newArrowScale
        }})
        .update();
    }});

    function resetStyles() {{
        cy.nodes().forEach(function(node) {{
            node.style({{
                'background-opacity': 0, 
                'background-color': 'transparent',
                'border-color': 'black',
                'border-width': 2,
                'border-opacity': 1,
                'text-opacity': 1
            }});
        }});
        cy.edges().forEach(function(edge) {{
            edge.style({{
                'curve-style': 'bezier',
                'target-arrow-shape': 'triangle',
                'line-color': 'grey',
                'target-arrow-color': 'grey',
                'width': '2px',
                'opacity': 1 
            }});
        }});
    }}

    function dimAllNodes() {{
        cy.nodes().forEach(function(node) {{
        node.style({{
            'background-color': 'transparent',
            'border-color': 'black',
            'border-opacity': 0.2,
            'text-opacity': 0.2
        }});
        }});
    }}

    function dimAllEdges() {{
        cy.edges().style({{
            'line-color': 'grey',
            'text-opacity': 0,
            'opacity': 0.2 
        }});
    }}

    function highlightConnectedEdges(node) {{
        node.connectedEdges().style({{
            'line-color': 'grey',
            'text-opacity': 1,
            'opacity': 1
        }});
    }}


    function highlightNode(node) {{
        node.style({{
            'background-opacity': 0, 
            'background-color': 'transparent',
            'border-color': 'black',
            'border-width': 2,
            'border-opacity': 1,
            'text-opacity': 1
        }});
        node.connectedEdges().forEach(function(edge) {{
        edge.connectedNodes().forEach(function(connectedNode) {{
            connectedNode.style({{
            'background-opacity': 0, 
            'background-color': 'transparent',
            'border-color': 'black',
            'border-width': 2,
            'border-opacity': 1,
            'text-opacity': 1
            }});
        }});
        edge.style({{ 'text-opacity': 1 }});  // Show edge label
        }});
    }}
    
    cy.on('tap', 'node', function(event) {{
        resetStyles();  // Reset all nodes to their default style
        dimAllNodes();  // Dim all nodes
        dimAllEdges();  // Dim all edges
        var tappedNode = event.target;
        highlightNode(tappedNode);  // Highlight the tapped node and its connected nodes
        highlightConnectedEdges(tappedNode);  // Highlight edges connected to the tapped node
        if (tappedNode.data('type') === 'place') {{
            const typeAnnotations = tappedNode.data('type_annotations');
            document.getElementById('functionInfo').innerText = `Place Annotations: \n${{JSON.stringify(typeAnnotations, null, 2)}}`;
        }}
        if (tappedNode.data('type') === 'transition') {{
            const functionName = tappedNode.data('label');
            const functionBody = tappedNode.data('functionBody');  // Assuming you've stored the function body here
            document.getElementById('functionInfo').innerText = `Delay Function: ${{functionName}}\n\nBody:\n${{functionBody}}`;
        }}
    }});

    cy.on('tap', 'edge', function(evt){{
        const edge = evt.target;
        console.log("Function Body: ", edge.data('functionBody'));
        const functionName = edge.data('label');
        const functionBody = edge.data('functionBody');  // Assuming you've stored the function body here
        document.getElementById('functionInfo').innerText = `Function: ${{functionName}}\n\nBody:\n${{functionBody}}`;
    }});
    
    cy.on('tap', function(event) {{
        if (event.target === cy) {{
            resetStyles();
        }}
    }});

    function highlightNodeById(nodeId) {{
    var node = cy.getElementById(nodeId);
    if (node.length === 0) {{
        return;
    }}
    resetStyles();  // Reset styles for all nodes and edges
    dimAllNodes();  // Dim other nodes
    dimAllEdges();  // Dim other edges
    highlightNode(node);  // Apply highlight style to the target node
    highlightConnectedEdges(node);  // Highlight edges connected to the target node
  }}

  // Call the highlight function on page load for a specific node ID
  document.addEventListener('DOMContentLoaded', function() {{
    highlightNodeById('{active_transition.id if active_transition != None else ""}');
  }});


</script>

</body>
</html>"""
    
    with open(html_file, "w") as f:
        f.write(html_content)


def lpn_viz_graph_only(places, transitions, html_file, clk, active_transition):
    generate_cytoscape_js_graph_only(places, transitions, html_file, clk, active_transition)

