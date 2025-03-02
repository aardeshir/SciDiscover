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
    if 'use_debate' not in st.session_state:
        st.session_state.use_debate = False
    if 'debate_history' not in st.session_state:
        st.session_state.debate_history = None

    # Initialize managers
    sci_agent = SciAgent()
    pubtator = PubTatorClient()

    # Add controls in sidebar
    with st.sidebar:
        st.header("Analysis Controls")

        # Analysis method selection
        analysis_method = st.radio(
            "Analysis Method",
            ["Standard Analysis", "Debate-Driven Analysis (Coscientist-style)"],
            index=0,
            help="Choose between standard analysis or multi-agent debate approach"
        )

        st.session_state.use_debate = analysis_method == "Debate-Driven Analysis (Coscientist-style)"

        # If debate is selected, show explanation
        if st.session_state.use_debate:
            st.info("""
            **Debate-Driven Analysis**

            Uses a multi-agent 'generate, debate, and evolve' methodology:
            1. Initial hypothesis generation
            2. Critical analysis and challenges
            3. Refinement and rebuttal
            4. Synthesis of strongest ideas

            This approach mimics scientific discourse for stronger analyses.
            """)

        # Novelty slider
        novelty_score = st.slider(
            "Novelty Level",
            min_value=0.0,
            max_value=1.0,
            value=st.session_state.novelty_score,
            help="0: Well-established mechanisms, 1: Novel/recent discoveries"
        )
        st.session_state.novelty_score = novelty_score

        # Include established mechanisms checkbox (only for standard analysis)
        if not st.session_state.use_debate:
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

        # Set initial status message based on analysis method
        if st.session_state.use_debate:
            status_message.info("Initiating debate-driven analysis with Claude 3.7 Sonnet...")
        else:
            status_message.info("Initiating extended thinking analysis with Claude 3.7 Sonnet...")

        progress_bar.progress(10)

        try:
            # Update status
            status_message.info("Extracting scientific concepts and preparing analysis...")
            progress_bar.progress(20)

            if st.session_state.use_debate:
                # Set debate-specific status
                status_message.info("Orchestrating multi-agent scientific debate (this may take a few minutes)...")
                progress_bar.progress(30)

                # Run the debate-driven analysis
                analysis = sci_agent.analyze_mechanism_with_debate(
                    query,
                    novelty_score=novelty_score
                )

                # Store debate history if available
                if hasattr(sci_agent.debate_orchestrator, 'debate_history'):
                    st.session_state.debate_history = sci_agent.debate_orchestrator.debate_history
            else:
                # Set standard analysis status
                status_message.info("Performing deep scientific analysis with extended thinking (this may take a few minutes)...")
                progress_bar.progress(40)

                # Run the standard analysis
                analysis = sci_agent.analyze_mechanism(
                    query,
                    novelty_score=novelty_score,
                    include_established=st.session_state.include_established
                )

                # Reset debate history
                st.session_state.debate_history = None

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

        # Display debate history if available and debate method was used
        if st.session_state.debate_history and st.session_state.use_debate:
            with st.expander("View Debate History", expanded=False):
                st.markdown("### Multi-Agent Scientific Debate")
                st.markdown("This analysis was refined through multiple rounds of scientific debate:")

                for idx, entry in enumerate(st.session_state.debate_history):
                    st.markdown(f"**Step {idx+1}: {entry['agent']} - {entry['action']}**")

                    # Format the content differently based on action type
                    if entry['action'] == 'critique':
                        if 'evaluation' in entry['content']:
                            st.markdown("**Key Points:**")

                            # Display strengths
                            if 'strengths' in entry['content']['evaluation']:
                                st.markdown("*Strengths:*")
                                for strength in entry['content']['evaluation']['strengths']:
                                    st.markdown(f"- {strength}")

                            # Display limitations
                            if 'limitations' in entry['content']['evaluation']:
                                st.markdown("*Limitations:*")
                                for limitation in entry['content']['evaluation']['limitations']:
                                    st.markdown(f"- {limitation}")

                    elif entry['action'] == 'initial_hypothesis' or entry['action'] == 'rebuttal':
                        if 'hypothesis' in entry['content']:
                            st.markdown(f"*Main Hypothesis:* {entry['content']['hypothesis']}")

                    # Add timestamp
                    st.caption(f"Timestamp: {entry['timestamp']}")
                    st.markdown("---")

        # Add citation for extended thinking capabilities
        st.markdown("---")
        st.caption("Analysis powered by Claude 3.7 Sonnet's extended thinking capabilities (128K output tokens, 32K thinking tokens)")