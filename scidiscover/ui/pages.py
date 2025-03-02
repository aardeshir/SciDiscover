import streamlit as st
from ..reasoning.sci_agent import SciAgent
from ..knowledge.pubtator import PubTatorClient
from ..collaboration.gamification import GamificationManager
from .components import (
    render_collaborative_hypothesis,
    render_user_achievements,
    render_concept_network
)

def main_page():
    st.title("SciDiscover")
    st.markdown("""
    A scientific discovery framework for analyzing molecular mechanisms and pathways.
    Powered by advanced language models and scientific knowledge bases.
    """)

    # Initialize managers
    sci_agent = SciAgent()
    pubtator = PubTatorClient()
    gamification = GamificationManager()

    # Initialize session state
    if 'analysis_results' not in st.session_state:
        st.session_state.analysis_results = None
    if 'current_query' not in st.session_state:
        st.session_state.current_query = ""
    if 'novelty_score' not in st.session_state:
        st.session_state.novelty_score = 0.5
    if 'include_established' not in st.session_state:
        st.session_state.include_established = True

    # Add novelty controls in sidebar
    with st.sidebar:
        st.header("Analysis Controls")

        # Novelty slider with session state
        novelty_score = st.slider(
            "Novelty Level",
            min_value=0.0,
            max_value=1.0,
            value=st.session_state.novelty_score,
            help="0: Well-established mechanisms, 1: Novel/recent discoveries",
            key="novelty_slider"
        )
        st.session_state.novelty_score = novelty_score

        # Include established mechanisms checkbox with session state
        include_established = st.checkbox(
            "Include established mechanisms",
            value=st.session_state.include_established,
            help="Always include well-known pathways regardless of novelty setting",
            key="established_checkbox"
        )
        st.session_state.include_established = include_established

        # Render user achievements
        render_user_achievements(gamification)

    query = st.text_area(
        "Enter your scientific query:",
        height=100,
        help="Describe the molecular mechanism or pathway you want to analyze",
        value=st.session_state.current_query
    )

    analyze_clicked = st.button("Analyze", type="primary")

    if analyze_clicked and query:
        st.session_state.current_query = query
        with st.spinner("Performing deep scientific analysis..."):
            analysis = sci_agent.analyze_mechanism(
                query,
                novelty_score=novelty_score,
                include_established=include_established
            )
            st.session_state.analysis_results = analysis

    # Display results if available
    if st.session_state.analysis_results:
        analysis = st.session_state.analysis_results

        if "error" in analysis:
            st.error("Error in analysis. Please try again.")
            return

        # Display Primary Analysis
        st.header("Molecular Mechanism Analysis")

        # Show confidence score
        confidence = analysis.get("confidence_score", 0)
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Analysis Confidence Score", f"{confidence:.2f}")
        with col2:
            st.metric("Novelty Level", f"{novelty_score:.2f}")

        # Display pathways
        st.subheader("Key Molecular Pathways")
        for pathway in analysis["primary_analysis"]["pathways"]:
            st.markdown(f"- {pathway}")

        # Display genes and their roles
        st.subheader("Relevant Genes and Their Roles")
        for gene in analysis["primary_analysis"]["genes"]:
            st.markdown(f"- **{gene['name']}**: {gene['role']}")

        # Display detailed mechanisms
        st.subheader("Detailed Molecular Mechanisms")
        st.markdown(analysis["primary_analysis"]["mechanisms"])

        # Display temporal sequence
        st.subheader("Temporal Sequence of Events")
        for idx, event in enumerate(analysis["primary_analysis"]["timeline"], 1):
            st.markdown(f"{idx}. {event}")

        # Display experimental evidence
        st.subheader("Supporting Experimental Evidence")
        for evidence in analysis["primary_analysis"]["evidence"]:
            st.markdown(f"- {evidence}")

        # Display implications
        st.subheader("Clinical and Therapeutic Implications")
        st.markdown(analysis["primary_analysis"]["implications"])

        # Show validation insights
        with st.expander("View Validation Analysis"):
            st.markdown(analysis["validation"])

        # Add collaborative hypothesis building
        st.markdown("---")
        render_collaborative_hypothesis(
            gamification,
            hypothesis_id=query[:50]  # Use truncated query as hypothesis ID
        )

        # Display concept network
        if "graph_analysis" in analysis:
            st.markdown("---")
            st.header("Knowledge Graph Visualization")
            render_concept_network(analysis["graph_analysis"].get("concept_paths"))