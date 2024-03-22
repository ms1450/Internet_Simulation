import networkx as nx
import plotly.graph_objects as go
import plotly.io as pio
import kaleido
import csv


# Function to create a graph and its visualization
def create_graph(nodes, edges, edge_types, exclude_ixp=False):
    G = nx.Graph()
    for node, attributes in nodes.items():
        if not exclude_ixp or ('IXP' not in attributes['type']):
            G.add_node(node, type=attributes['type'])
    for edge, edge_type in zip(edges, edge_types):
        if not exclude_ixp or (edge_type != 'IXP'):
            G.add_edge(edge[0], edge[1])

    node_color_map = {'Tier 1 AS': 'red', 'Transit AS': 'orange', 'Stub AS': 'yellow'}
    edge_color_map = {'P2P': 'blue', 'P2C': 'green'}
    pos = nx.spring_layout(G, k=0.15, iterations=200)

    node_color = [node_color_map.get(nodes[node]['type'], 'grey') for node in G.nodes()]

    node_trace = go.Scatter(
        x=[pos[node][0] for node in G.nodes()],
        y=[pos[node][1] for node in G.nodes()],
        text=[node for node in G.nodes()],
        mode='markers+text',
        hoverinfo='text',
        textposition='middle center',
        marker=dict(
            showscale=False,
            size=35,
            color=node_color,
            line_width=2
        ),
        textfont=dict(
            color='black',
            size=10
        )
    )

    edge_traces = []
    for edge in G.edges():
        x0, y0 = pos[edge[0]]
        x1, y1 = pos[edge[1]]
        edge_trace = go.Scatter(
            x=[x0, x1, None], y=[y0, y1, None],
            line=dict(width=1, color=edge_color_map.get(edge_types[edges.index(edge)], 'grey')),
            mode='lines',
            hoverinfo='none'
        )
        edge_traces.append(edge_trace)

    fig = go.Figure(data=edge_traces + [node_trace],
                    layout=go.Layout(
                        showlegend=False,
                        hovermode='closest',
                        margin=dict(b=0, l=0, r=0, t=0),
                        xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                        yaxis=dict(showgrid=False, zeroline=False, showticklabels=False))
                    )

    return fig


if __name__ == '__main__':
    # Load node and edge data
    nodes = {}
    edges = []
    edge_types = []

    # Read the node data
    with open('./Topology/Topology_Nodes_50.csv', 'r') as csvfile:
        csvreader = csv.reader(csvfile)
        next(csvreader)  # Skip the header
        for row in csvreader:
            nodes[row[0]] = {'type': row[1]}

    # Read the edge data
    with open('./Topology/Topology_Links_50.csv', 'r') as csvfile:
        csvreader = csv.reader(csvfile)
        next(csvreader)  # Skip the header
        for row in csvreader:
            edges.append((row[2], row[3]))
            edge_types.append(row[1])

    # Create and show the first graph (including all connections)
    print("[+]\tShowing Network Graph of ASes and IXPs")
    fig1 = create_graph(nodes, edges, edge_types)
    pio.write_image(fig1, './Topology/Topology_Complete.png', width=1920, height=1080)
    # fig1.show()

    # Create and show the second graph (excluding IXPs)
    print("[+]\tShowing Network Graph of ASes")
    fig2 = create_graph(nodes, edges, edge_types, exclude_ixp=True)
    pio.write_image(fig2, './Topology/Topology_ASes.png', width=1920, height=1080)
    # fig2.show()
