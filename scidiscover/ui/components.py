import streamlit as st
import plotly.graph_objects as go
import networkx as nx
from ..collaboration.gamification import GamificationManager

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

    # Create a spring layout
    pos = nx.spring_layout(graph, k=2, iterations=50)

    # Create edges
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

    # Create nodes
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

        node_type = node[1].get('type', 'concept')
        description = node[1].get('description', '')
        hover_text = f"{node[0]}<br>Type: {node_type}<br>{description}"
        node_text.append(hover_text)

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

    # Create figure
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

    # Add legend
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

def render_collaborative_hypothesis(gamification_manager: GamificationManager, hypothesis_id: str):
    """Render collaborative hypothesis building interface"""
    st.subheader("Collaborative Hypothesis Building")

    # Add contribution
    contribution = st.text_area(
        "Add to this hypothesis:",
        help="Suggest refinements, additional mechanisms, or evidence"
    )

    # Evidence and novelty scoring
    col1, col2 = st.columns(2)
    with col1:
        evidence_score = st.slider(
            "Evidence Strength",
            0.0, 1.0, 0.5,
            help="Rate the strength of supporting evidence"
        )
    with col2:
        novelty_score = st.slider(
            "Novelty Score",
            0.0, 1.0, 0.5,
            help="Rate how novel this contribution is"
        )

    # References
    references = st.text_area(
        "Supporting References",
        help="Enter PubMed IDs or DOIs, one per line"
    ).split('\n')

    if st.button("Submit Contribution"):
        if contribution and references:
            contribution_obj = gamification_manager.add_contribution(
                user_id=st.session_state.get('user_id', 'anonymous'),
                hypothesis_id=hypothesis_id,
                content=contribution,
                evidence_score=evidence_score,
                novelty_score=novelty_score,
                references=[ref.strip() for ref in references if ref.strip()]
            )
            st.success(f"Contribution added! Earned {contribution_obj.points} points.")

def render_user_achievements(gamification_manager: GamificationManager):
    """Render user achievements and stats"""
    st.sidebar.subheader("Your Research Impact")

    user_id = st.session_state.get('user_id', 'anonymous')
    achievements = gamification_manager.get_user_achievements(user_id)

    st.sidebar.metric("Total Score", achievements["total_score"])
    st.sidebar.metric("Contributions", achievements["contributions"])
    st.sidebar.metric("Top Contribution", achievements["top_contribution"])
    st.sidebar.markdown(f"**Level**: {achievements['expertise_level']}")