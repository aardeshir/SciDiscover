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

    # Initialize managers
    sci_agent = SciAgent()
    pubtator = PubTatorClient()

    # Add novelty controls in sidebar
    with st.sidebar:
        st.header("Analysis Controls")

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

        # Add information about extended thinking capabilities
        st.markdown("---")
        with st.expander("🧠 Extended Thinking", expanded=True):
            st.markdown("""
            **Enhanced with Claude 3.7 Sonnet's Extended Thinking**

            Analysis now powered by:
            - 128K token output capacity
            - 32K token thinking budget
            - Advanced multi-step reasoning
            - Deeper scientific analysis
            """)

    # Main query input
    query = st.text_area(
        "Enter your scientific query:",
        height=100,
        help="Describe the molecular mechanism or pathway you want to analyze",
        value=st.session_state.current_query
    )

    analyze_clicked = st.button("Analyze", type="primary")

    if analyze_clicked and query:
        st.session_state.current_query = query

        # Create a progress bar and status message
        progress_bar = st.progress(0)
        status_message = st.empty()

        status_message.info("Initiating extended thinking analysis with Claude 3.7 Sonnet...")
        progress_bar.progress(10)

        try:
            # Update status
            status_message.info("Extracting scientific concepts and preparing analysis...")
            progress_bar.progress(20)

            # First status update
            status_message.info("Performing deep scientific analysis with extended thinking (this may take a few minutes)...")
            progress_bar.progress(40)

            # Run the analysis
            analysis = sci_agent.analyze_mechanism(
                query,
                novelty_score=novelty_score,
                include_established=include_established
            )

            # Final status update
            status_message.success("Analysis complete!")
            progress_bar.progress(100)

            # Store results and clear status displays
            st.session_state.analysis_results = analysis
            status_message.empty()
            progress_bar.empty()

        except Exception as e:
            # Show error and clear progress displays
            progress_bar.empty()
            status_message.error(f"Error in analysis: {str(e)}")
            st.error("The extended thinking analysis encountered an error. Please try again with a different query or check the logs for details.")
            return

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
        pathways = analysis["primary_analysis"]["pathways"]
        if pathways:
            for pathway in pathways:
                st.markdown(f"- {pathway}")
        else:
            st.info("No specific pathways identified for this query.")

        # Display genes and their roles
        st.subheader("Relevant Genes and Their Roles")
        genes = analysis["primary_analysis"]["genes"]
        if genes:
            for gene in genes:
                st.markdown(f"- **{gene['name']}**: {gene['role']}")
        else:
            st.info("No specific genes identified for this query.")

        # Display detailed mechanisms
        st.subheader("Detailed Molecular Mechanisms")
        mechanisms = analysis["primary_analysis"]["mechanisms"]
        if mechanisms and mechanisms != "No mechanism analysis available":
            st.markdown(mechanisms)
        else:
            st.info("No detailed mechanisms identified for this query.")

        # Display temporal sequence
        st.subheader("Temporal Sequence of Events")
        timeline = analysis["primary_analysis"]["timeline"]
        if timeline:
            for idx, event in enumerate(timeline, 1):
                st.markdown(f"{idx}. {event}")
        else:
            st.info("No temporal sequence identified for this query.")

        # Display experimental evidence
        st.subheader("Supporting Experimental Evidence")
        evidence = analysis["primary_analysis"]["evidence"]
        if evidence:
            for evidence_item in evidence:
                st.markdown(f"- {evidence_item}")
        else:
            st.info("No supporting evidence identified for this query.")

        # Display implications
        st.subheader("Clinical and Therapeutic Implications")
        implications = analysis["primary_analysis"]["implications"]
        if implications and implications != "No implications available":
            if isinstance(implications, list):
                for implication in implications:
                    st.markdown(f"- {implication}")
            else:
                st.markdown(implications)
        else:
            st.info("No clinical implications identified for this query.")

        # Show validation insights
        with st.expander("View Validation Analysis"):
            st.markdown(analysis["validation"])

        # Add citation for extended thinking capabilities
        st.markdown("---")
        st.caption("Analysis powered by Claude 3.7 Sonnet's extended thinking capabilities (128K output tokens, 32K thinking tokens)")