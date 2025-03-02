import streamlit as st
import plotly.graph_objects as go
import networkx as nx

def render_header():
    st.title("SciDiscover")
    st.markdown("""
    A scientific discovery framework for hypothesis generation and concept connection.
    """)

def render_search_box():
    return st.text_input("Enter scientific concepts or keywords:", "")

def render_concept_network(knowledge_graph):
    """Render network visualization of concepts"""
    if not isinstance(knowledge_graph, nx.Graph):
        graph = getattr(knowledge_graph, 'graph', nx.Graph())
    else:
        graph = knowledge_graph

    if len(graph.nodes()) == 0:
        st.warning("No concepts to display in the network.")
        return

    # Create a spring layout with more space between nodes
    pos = nx.spring_layout(graph, k=2, iterations=50)

    # Create edges with relationship labels
    edge_x = []
    edge_y = []
    edge_text = []

    for edge in graph.edges(data=True):
        x0, y0 = pos[edge[0]]
        x1, y1 = pos[edge[1]]
        edge_x.extend([x0, x1, None])
        edge_y.extend([y0, y1, None])
        edge_text.append(edge[2].get('type', ''))

    edge_trace = go.Scatter(
        x=edge_x, y=edge_y,
        line=dict(width=1, color='#888'),
        hoverinfo='text',
        text=edge_text,
        mode='lines'
    )

    # Create nodes with metadata
    node_x = []
    node_y = []
    node_text = []
    node_color = []

    color_map = {
        'chemical': '#1f77b4',
        'biological_system': '#2ca02c',
        'biological_process': '#d62728',
        'developmental_stage': '#9467bd',
        'intervention': '#e377c2',
        'mechanism': '#17becf'
    }

    for node in graph.nodes(data=True):
        x, y = pos[node[0]]
        node_x.append(x)
        node_y.append(y)

        # Create hover text with node metadata
        node_type = node[1].get('type', 'concept')
        description = node[1].get('description', '')
        hover_text = f"{node[0]}<br>Type: {node_type}<br>{description}"
        node_text.append(hover_text)

        # Assign color based on node type
        node_color.append(color_map.get(node_type, '#7f7f7f'))

    node_trace = go.Scatter(
        x=node_x, y=node_y,
        mode='markers+text',
        hoverinfo='text',
        text=[node[0] for node in graph.nodes(data=True)],
        textposition="top center",
        hovertext=node_text,
        marker=dict(
            showscale=False,
            color=node_color,
            size=20,
            line=dict(width=1, color='#888')
        )
    )

    # Create the figure with custom layout
    fig = go.Figure(
        data=[edge_trace, node_trace],
        layout=go.Layout(
            showlegend=False,
            hovermode='closest',
            margin=dict(b=20, l=5, r=5, t=40),
            xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
            yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            width=800,
            height=600
        )
    )

    st.plotly_chart(fig)

    # Add legend for node types
    st.markdown("### Concept Types")
    cols = st.columns(3)
    for i, (type_name, color) in enumerate(color_map.items()):
        cols[i % 3].markdown(
            f'<div style="color: {color}">● {type_name.replace("_", " ").title()}</div>',
            unsafe_allow_html=True
        )

def render_hypothesis_output(hypothesis):
    st.subheader("Generated Hypothesis")
    st.write(hypothesis)

def render_entity_table(entities):
    if entities is not None and not entities.empty:
        st.subheader("Identified Entities")
        st.table(entities)
    else:
        st.warning("No entities were identified.")