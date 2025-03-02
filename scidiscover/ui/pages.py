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
    if 'high_demand_mode' not in st.session_state:
        st.session_state.high_demand_mode = True
    if 'live_debate_updates' not in st.session_state:
        st.session_state.live_debate_updates = []
    if 'analysis_running' not in st.session_state:
        st.session_state.analysis_running = False

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

        # Add thinking mode selection
        st.markdown("---")
        st.subheader("Extended Thinking Configuration")
        thinking_mode = st.radio(
            "Claude's Thinking Mode",
            ["High-Demand", "Low-Demand"],
            index=0 if st.session_state.high_demand_mode else 1,
            help="High-Demand: Deeper analysis with 64K thinking tokens. Low-Demand: More efficient with 32K thinking tokens."
        )
        st.session_state.high_demand_mode = (thinking_mode == "High-Demand")

        # Display current configuration based on selected mode
        if st.session_state.high_demand_mode:
            st.info("""
            **High-Demand Mode**
            - 64K thinking tokens
            - 80K max tokens output
            - Best for complex queries
            """)
        else:
            st.info("""
            **Low-Demand Mode**
            - 32K thinking tokens
            - 64K max tokens output
            - Faster for simpler queries
            """)

        # Add information about extended thinking capabilities
        st.markdown("---")
        with st.expander("🧠 Extended Thinking", expanded=True):
            st.markdown("""
            **Enhanced with Claude 3.7 Sonnet's Extended Thinking**

            Analysis now powered by:
            - {output_tokens}K token output capacity
            - {thinking_tokens}K token thinking budget
            - Advanced multi-step reasoning
            - Deeper scientific analysis
            """.format(
                output_tokens="80" if st.session_state.high_demand_mode else "64",
                thinking_tokens="64" if st.session_state.high_demand_mode else "32"
            ))

    # Initialize managers with user's thinking mode preference
    sci_agent = SciAgent(high_demand_mode=st.session_state.high_demand_mode)
    pubtator = PubTatorClient()

    # Main query input
    query = st.text_area(
        "Enter your scientific query:",
        height=100,
        help="Describe the molecular mechanism or pathway you want to analyze",
        value=st.session_state.current_query
    )

    analyze_clicked = st.button("Analyze", type="primary")

    # Create a container for live debate updates
    live_debate_container = st.empty()

    # Display live updates if analysis is running
    if st.session_state.analysis_running:
        with live_debate_container.container():
            st.subheader("🔄 Scientific Analysis in Progress")
            st.info("The analysis is running. You'll see live updates from the scientific agents below.")

            if st.session_state.live_debate_updates:
                st.markdown("### Live Scientific Agent Updates")
                for update in st.session_state.live_debate_updates:
                    with st.expander(f"{update['agent']} - {update['action']}", expanded=True):
                        # Format based on action type
                        if update['action'] == 'critique' and 'evaluation' in update['content']:
                            st.markdown("**Key Points:**")

                            # Display strengths
                            if 'strengths' in update['content']['evaluation']:
                                st.markdown("*Strengths:*")
                                for strength in update['content']['evaluation']['strengths']:
                                    st.markdown(f"- {strength}")

                            # Display limitations
                            if 'limitations' in update['content']['evaluation']:
                                st.markdown("*Limitations:*")
                                for limitation in update['content']['evaluation']['limitations']:
                                    st.markdown(f"- {limitation}")

                        elif update['action'] == 'initial_hypothesis' or update['action'] == 'rebuttal':
                            if 'hypothesis' in update['content']:
                                st.markdown(f"*Main Hypothesis:* {update['content']['hypothesis']}")

    # Handle the analysis process
    if analyze_clicked and query:
        st.session_state.current_query = query
        st.session_state.analysis_running = True
        st.session_state.live_debate_updates = []  # Reset live updates

        # Initialize the live update container
        with live_debate_container.container():
            st.subheader("🔄 Scientific Analysis in Progress")
            st.info("The analysis is running. You'll see live updates from the scientific agents below.")

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

            # Register the callback to update debate history in real-time
            def update_debate_callback(entry):
                st.session_state.live_debate_updates.append(entry)
                # Force a rerun to update the UI
                st.experimental_rerun()

            # Pass the callback to the sci_agent
            sci_agent.set_debate_callback(update_debate_callback)

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
            st.session_state.analysis_running = False
            status_message.empty()
            progress_bar.empty()
            live_debate_container.empty()  # Clear the live updates container

        except Exception as e:
            # Show error and clear progress displays
            progress_bar.empty()
            status_message.error(f"Error in analysis: {str(e)}")
            st.error("The extended thinking analysis encountered an error. Please try again with a different query or check the logs for details.")
            st.session_state.analysis_running = False
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
        st.caption("Analysis powered by Claude 3.7 Sonnet's extended thinking capabilities ({0}K output tokens, {1}K thinking tokens)".format(
            "80" if st.session_state.high_demand_mode else "64",
            "64" if st.session_state.high_demand_mode else "32"
        ))