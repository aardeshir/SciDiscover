import streamlit as st
from ..reasoning.sci_agent import SciAgent
from ..knowledge.pubtator import PubTatorClient

def main_page():
    st.title("SciDiscover")
    st.markdown("""
    A scientific discovery framework for analyzing molecular mechanisms and pathways.
    Powered by advanced language models and scientific knowledge bases.
    """)

    # Initialize session state
    if 'analysis_results' not in st.session_state:
        st.session_state.analysis_results = None
    if 'current_query' not in st.session_state:
        st.session_state.current_query = ""
    if 'novelty_score' not in st.session_state:
        st.session_state.novelty_score = 0.5
    if 'include_established' not in st.session_state:
        st.session_state.include_established = True
    if 'show_thinking' not in st.session_state:
        st.session_state.show_thinking = True
    if 'analysis_error' not in st.session_state:
        st.session_state.analysis_error = None

    # Initialize managers
    sci_agent = SciAgent()
    pubtator = PubTatorClient()

    # Add novelty controls in sidebar
    with st.sidebar:
        st.header("Analysis Controls")

        # Enable thinking process toggle
        show_thinking = st.checkbox(
            "Show thinking process",
            value=st.session_state.show_thinking,
            help="Display Claude's reasoning steps during analysis"
        )
        st.session_state.show_thinking = show_thinking

        # Novelty slider
        novelty_score = st.slider(
            "Novelty Level",
            min_value=0.0,
            max_value=1.0,
            value=st.session_state.novelty_score,
            help="0: Well-established mechanisms, 1: Novel/recent discoveries"
        )
        st.session_state.novelty_score = novelty_score

        # Include established mechanisms checkbox
        include_established = st.checkbox(
            "Include established mechanisms",
            value=st.session_state.include_established,
            help="Always include well-known pathways regardless of novelty setting"
        )
        st.session_state.include_established = include_established

        # Model information
        st.markdown("---")
        st.markdown("### Model Information")
        st.markdown("Using Claude 3.7 Sonnet with extended thinking capability")
        st.markdown("Extended thinking allows Claude to show its reasoning process during complex analysis tasks.")

    # Main query input
    query = st.text_area(
        "Enter your scientific query:",
        height=100,
        help="Describe the molecular mechanism or pathway you want to analyze",
        value=st.session_state.current_query
    )

    analyze_clicked = st.button("Analyze", type="primary")

    # Clear previous errors
    if analyze_clicked:
        st.session_state.analysis_error = None

    if analyze_clicked and query:
        st.session_state.current_query = query
        with st.spinner("Performing deep scientific analysis with extended thinking..."):
            try:
                analysis = sci_agent.analyze_mechanism(
                    query,
                    novelty_score=novelty_score,
                    include_established=include_established,
                    enable_thinking=show_thinking
                )

                # Check for errors
                if "error" in analysis:
                    st.session_state.analysis_error = analysis["error"]
                    st.session_state.analysis_results = None
                else:
                    st.session_state.analysis_results = analysis
                    st.session_state.analysis_error = None
            except Exception as e:
                st.session_state.analysis_error = f"Error in analysis: {str(e)}"
                st.session_state.analysis_results = None

    # Display any errors that occurred
    if st.session_state.analysis_error:
        st.error(st.session_state.analysis_error)

    # Display results if available
    if st.session_state.analysis_results:
        analysis = st.session_state.analysis_results

        # Show thinking process if enabled and available
        if show_thinking and "thinking_process" in analysis and analysis["thinking_process"]:
            with st.expander("View Analysis Thinking Process", expanded=True):
                st.markdown("### Claude's Reasoning Process")
                st.markdown(analysis["thinking_process"])

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
        if analysis["primary_analysis"]["pathways"]:
            for pathway in analysis["primary_analysis"]["pathways"]:
                st.markdown(f"- {pathway}")
        else:
            st.info("No specific pathways identified in this analysis.")

        # Display genes and their roles
        st.subheader("Relevant Genes and Their Roles")
        if analysis["primary_analysis"]["genes"]:
            for gene in analysis["primary_analysis"]["genes"]:
                st.markdown(f"- **{gene['name']}**: {gene['role']}")
        else:
            st.info("No specific genes identified in this analysis.")

        # Display detailed mechanisms
        st.subheader("Detailed Molecular Mechanisms")
        st.markdown(analysis["primary_analysis"]["mechanisms"])

        # Display temporal sequence
        st.subheader("Temporal Sequence of Events")
        if analysis["primary_analysis"]["timeline"]:
            for idx, event in enumerate(analysis["primary_analysis"]["timeline"], 1):
                st.markdown(f"{idx}. {event}")
        else:
            st.info("No specific temporal sequence identified in this analysis.")

        # Display experimental evidence
        st.subheader("Supporting Experimental Evidence")
        if analysis["primary_analysis"]["evidence"]:
            for evidence in analysis["primary_analysis"]["evidence"]:
                st.markdown(f"- {evidence}")
        else:
            st.info("No specific experimental evidence identified in this analysis.")

        # Display implications
        st.subheader("Clinical and Therapeutic Implications")
        if analysis["primary_analysis"]["implications"]:
            for implication in analysis["primary_analysis"]["implications"]:
                st.markdown(f"- {implication}")
        else:
            st.info("No specific clinical implications identified in this analysis.")

        # Show validation insights
        with st.expander("View Validation Analysis"):
            st.markdown(analysis["validation"])