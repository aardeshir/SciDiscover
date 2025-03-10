import streamlit as st
import plotly.graph_objects as go
import networkx as nx
from ..collaboration.gamification import GamificationManager
import time

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
            help="Rate the strength of supporting evidence (40 points max)"
        )
    with col2:
        novelty_score = st.slider(
            "Novelty Score",
            0.0, 1.0, 0.5,
            help="Rate how novel this contribution is (30 points max)"
        )

    # References
    references = st.text_area(
        "Supporting References",
        help="Enter PubMed IDs or DOIs, one per line. Each reference = 5 points (20 points max)"
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

            # Show detailed point breakdown
            st.success(f"Contribution added! Earned {contribution_obj.points} points.")
            with st.expander("View Point Breakdown"):
                st.markdown("""
                **Points Breakdown:**
                - Evidence Strength: {:.0f} points (based on evidence strength slider)
                - Novelty Score: {:.0f} points (based on novelty assessment)
                - References: {:.0f} points ({} references provided)
                """.format(
                    evidence_score * 40,  # Max 40 points for evidence
                    novelty_score * 30,   # Max 30 points for novelty
                    min(len(references) * 5, 20),  # Max 20 points for references
                    len([ref for ref in references if ref.strip()])
                ))

                # Show progress to next level
                achievements = gamification_manager.get_user_achievements(
                    st.session_state.get('user_id', 'anonymous')
                )
                st.markdown(f"""
                **Current Level:** {achievements['expertise_level']}

                **How to earn more points:**
                - Add strong scientific evidence (up to 40 points)
                - Contribute novel insights (up to 30 points)
                - Include more references (5 points each, up to 20 points)
                """)

                # Calculate points needed for next level
                current_score = achievements['total_score']
                next_level_threshold = next((
                    threshold for threshold in [100, 500, 1000, 5000] 
                    if threshold > current_score
                ), 5000)

                st.markdown(f"""
                **Points needed for next level:** {next_level_threshold - current_score}

                **Level Progression:**
                - Research Assistant → Postdoc Researcher: 100 points
                - Postdoc Researcher → Senior Scientist: 500 points
                - Senior Scientist → Principal Investigator: 1000 points
                - Principal Investigator → Distinguished Researcher: 5000 points
                """)

def render_level_progress_bar(current_score: int, current_level: str):
    """Render an animated progress bar showing research level progress"""
    # Define level thresholds
    level_thresholds = {
        "Research Assistant": (0, 100),
        "Postdoc Researcher": (100, 500),
        "Senior Scientist": (500, 1000),
        "Principal Investigator": (1000, 5000),
        "Distinguished Researcher": (5000, 5000)
    }

    # Get current level range
    start_points, end_points = level_thresholds[current_level]

    # Calculate progress percentage
    progress = (current_score - start_points) / (end_points - start_points)
    progress = min(1.0, max(0.0, progress))  # Clamp between 0 and 1

    # Create animated progress bar
    st.markdown("### Research Progress")

    progress_bar = st.progress(0.0)
    status_text = st.empty()

    # Animate progress bar
    for i in range(int(progress * 100)):
        progress_bar.progress(i/100)
        current_points = int(start_points + (i/100) * (end_points - start_points))
        status_text.text(f"{current_points} / {end_points} points")
        time.sleep(0.01)

    # Set final value
    progress_bar.progress(progress)
    status_text.text(f"{current_score} / {end_points} points")

    # Show level milestones
    st.markdown("""
    #### Level Milestones
    📚 Research Assistant → Postdoc Researcher: 100 points
    🔬 Postdoc Researcher → Senior Scientist: 500 points
    🧪 Senior Scientist → Principal Investigator: 1000 points
    🎓 Principal Investigator → Distinguished Researcher: 5000 points
    """)

def render_user_achievements(gamification_manager: GamificationManager):
    """Render user achievements and stats with animated progress"""
    st.sidebar.subheader("Your Research Impact")

    user_id = st.session_state.get('user_id', 'anonymous')
    achievements = gamification_manager.get_user_achievements(user_id)

    # Display basic stats
    st.sidebar.metric("Total Score", achievements["total_score"])
    st.sidebar.metric("Contributions", achievements["contributions"])
    st.sidebar.metric("Top Contribution", achievements["top_contribution"])

    # Show animated level progress
    level = achievements['expertise_level']
    st.sidebar.markdown(f"""
    ### Research Level
    **Current Level:** {level}
    """)

    # Add animated progress bar
    render_level_progress_bar(achievements["total_score"], level)