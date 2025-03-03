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
    if 'analysis_stage' not in st.session_state:
        st.session_state.analysis_stage = 0
    if 'thinking_mode' not in st.session_state:
        st.session_state.thinking_mode = "high"
    if 'use_elo_evaluation' not in st.session_state:
        st.session_state.use_elo_evaluation = False

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

            # Add Elo evaluation option (only when debate is selected)
            use_elo = st.checkbox(
                "Use Elo-based hypothesis evaluation", 
                value=st.session_state.use_elo_evaluation,
                help="Enable comparative hypothesis scoring with Elo ratings (inspired by Google's Coscientist)"
            )

            st.session_state.use_elo_evaluation = use_elo

            if use_elo:
                st.info("""
                **Elo-Based Hypothesis Evaluation**

                Hypotheses compete in direct comparisons and are assigned Elo ratings:
                - Higher ratings indicate stronger scientific explanations
                - Final tournament determines the most robust hypothesis
                - Similar to Google's Coscientist approach

                This method enables more objective evaluation through direct competition.
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
            ["High-Demand", "Low-Demand", "None"],
            index=0 if st.session_state.thinking_mode == "high" else (1 if st.session_state.thinking_mode == "low" else 2),
            help="Choose the level of extended thinking capabilities"
        )

        # Map the radio selection to the thinking mode
        if thinking_mode == "High-Demand":
            st.session_state.thinking_mode = "high"
        elif thinking_mode == "Low-Demand":
            st.session_state.thinking_mode = "low"
        else:  # None
            st.session_state.thinking_mode = "none"

        # For backward compatibility
        st.session_state.high_demand_mode = (thinking_mode == "High-Demand")

        # Display current configuration based on selected mode
        if thinking_mode == "High-Demand":
            st.info("""
            **High-Demand Mode**
            - 64K thinking tokens
            - 80K max tokens output
            - Best for complex queries
            - Slowest processing time
            """)
        elif thinking_mode == "Low-Demand":
            st.info("""
            **Low-Demand Mode**
            - 32K thinking tokens
            - 64K max tokens output
            - Balanced for typical queries
            - Moderate processing time
            """)
        else:  # None
            st.info("""
            **No Extended Thinking**
            - 0 thinking tokens
            - 32K max tokens output
            - Suitable for simple queries
            - Fastest processing time
            """)

        # Add information about extended thinking capabilities
        st.markdown("---")
        with st.expander("🧠 Extended Thinking", expanded=True):
            st.markdown("""
            **Enhanced with Claude 3.7 Sonnet's Extended Thinking**

            Analysis now powered by:
            - {output_tokens}K token output capacity
            - {thinking_tokens} token thinking budget
            - {level} scientific analysis
            """.format(
                output_tokens="80" if thinking_mode == "High-Demand" else ("64" if thinking_mode == "Low-Demand" else "32"),
                thinking_tokens="64K" if thinking_mode == "High-Demand" else ("32K" if thinking_mode == "Low-Demand" else "0"),
                level="Deep multi-step" if thinking_mode != "None" else "Standard"
            ))

    # Initialize managers with user's thinking mode preference
    sci_agent = SciAgent(high_demand_mode=st.session_state.high_demand_mode)
    # Update the thinking mode to match the radio selection
    sci_agent.set_thinking_mode(st.session_state.thinking_mode)
    # Configure Elo evaluation if enabled
    if st.session_state.use_debate and st.session_state.use_elo_evaluation:
        sci_agent.enable_elo_evaluation(True)
    else:
        sci_agent.enable_elo_evaluation(False)

    pubtator = PubTatorClient()

    # Main query input
    query = st.text_area(
        "Enter your scientific query:",
        height=100,
        help="Describe the molecular mechanism or pathway you want to analyze",
        value=st.session_state.current_query
    )

    analyze_clicked = st.button("Analyze", type="primary")

    # Create a container for analysis progress
    analysis_progress_container = st.empty()

    # Display analysis progress if running
    if st.session_state.analysis_running:
        # Define the analysis stages for different analysis methods
        if st.session_state.use_debate:
            stages = [
                "Initiating scientific debate orchestration...",
                "Extracting and defining key scientific concepts...",
                "Generating initial hypothesis by Scientist Agent...",
                "Critical evaluation by Critic Agent (Round 1)...",
                "Hypothesis refinement by Expander Agent (Round 1)...",
                "Scientific rebuttal by Scientist Agent (Round 1)...",
                "Merging hypothesis improvements (Round 1)...",
                "Critical evaluation by Critic Agent (Round 2)...",
                "Hypothesis refinement by Expander Agent (Round 2)...",
                "Scientific rebuttal by Scientist Agent (Round 2)...",
                "Merging hypothesis improvements (Round 2)...",
                "Critical evaluation by Critic Agent (Round 3)...",
                "Hypothesis refinement by Expander Agent (Round 3)...",
                "Scientific rebuttal by Scientist Agent (Round 3)...",
                "Synthesizing final analysis from debate..."
            ]

            # Add Elo tournament stage if enabled
            if st.session_state.use_elo_evaluation:
                stages.insert(-1, "Running Elo-based hypothesis tournament...")
        else:
            stages = [
                "Initiating scientific analysis with extended thinking...",
                "Extracting and defining key scientific concepts...",
                "Performing knowledge graph reasoning...",
                "Analyzing molecular mechanisms and pathways...",
                "Validating findings against scientific literature...",
                "Synthesizing comprehensive analysis...",
                "Finalizing results with confidence scoring..."
            ]

        # Calculate progress percentage
        current_stage = min(st.session_state.analysis_stage, len(stages) - 1)
        progress_percent = current_stage / (len(stages) - 1)

        with analysis_progress_container.container():
            st.subheader("🔄 Scientific Analysis in Progress")

            # Progress bar and current stage
            st.progress(progress_percent)

            # Current stage description
            st.info(f"**Current Stage:** {stages[current_stage]}")

            # Estimated time remaining based on thinking mode
            if st.session_state.use_debate:
                if st.session_state.thinking_mode == "high":
                    total_time = "15-25 minutes"
                elif st.session_state.thinking_mode == "low":
                    total_time = "10-15 minutes"
                else:  # none
                    total_time = "5-10 minutes"
            else:
                if st.session_state.thinking_mode == "high":
                    total_time = "10-15 minutes"
                elif st.session_state.thinking_mode == "low":
                    total_time = "5-10 minutes"
                else:  # none
                    total_time = "2-5 minutes"

            st.caption(f"Total estimated time: {total_time} (This is a complex scientific analysis involving multi-step reasoning)")

            # Display a message that explains what's happening
            if st.session_state.use_debate:
                debate_info = """
                ### Multi-Agent Scientific Debate in Progress

                The system is currently running a scientific debate between multiple specialized AI agents:
                - **Scientist Agent:** Generates core hypotheses and mechanisms
                - **Critic Agent:** Identifies limitations and challenges assumptions
                - **Expander Agent:** Refines and improves on initial ideas
                """

                if st.session_state.use_elo_evaluation:
                    debate_info += """

                    Hypotheses are being evaluated using an **Elo-based rating system**:
                    - Each hypothesis is assigned an Elo rating (like in chess)
                    - Hypotheses compete in head-to-head comparisons
                    - Winners gain rating points, losers lose points
                    - Final tournament determines the strongest scientific explanation
                    """

                debate_info += """
                Each agent contributes to improving the scientific analysis through multiple debate rounds.
                This process mimics scientific discourse and improves the quality of the final analysis.
                """

                st.markdown(debate_info)
            else:
                st.markdown("""
                ### Extended Scientific Analysis in Progress

                The system is currently performing a deep scientific analysis using:
                - Knowledge graph reasoning over biomedical literature
                - Molecular mechanism and pathway identification
                - Confidence-weighted evidence integration

                This analysis uses Claude's extended thinking capabilities to explore complex scientific relationships.
                """)

    # Handle the analysis process
    if analyze_clicked and query:
        st.session_state.current_query = query
        st.session_state.analysis_running = True
        st.session_state.analysis_stage = 0  # Reset progress
        st.session_state.live_debate_updates = []  # Reset updates

        # Initialize the progress display
        with analysis_progress_container.container():
            if st.session_state.use_debate:
                st.subheader("🔄 Orchestrating multi-agent scientific debate...")
            else:
                st.subheader("🔄 Performing deep scientific analysis...")
            st.info("Initializing analysis, please wait...")
            st.progress(0)

        try:
            # Register the callback to capture debate history but not for UI updates
            def update_debate_callback(entry):
                st.session_state.live_debate_updates.append(entry)

                # Update the stage counter based on agent activities
                if entry['action'] == 'initial_hypothesis':
                    st.session_state.analysis_stage = 2
                elif entry['action'] == 'critique' and len(st.session_state.live_debate_updates) <= 2:
                    st.session_state.analysis_stage = 3
                elif entry['action'] == 'refinement' and len(st.session_state.live_debate_updates) <= 4:
                    st.session_state.analysis_stage = 4
                elif entry['action'] == 'rebuttal' and len(st.session_state.live_debate_updates) <= 6:
                    st.session_state.analysis_stage = 5
                elif entry['action'] == 'critique' and len(st.session_state.live_debate_updates) <= 8:
                    st.session_state.analysis_stage = 7
                elif entry['action'] == 'refinement' and len(st.session_state.live_debate_updates) <= 10:
                    st.session_state.analysis_stage = 8
                elif entry['action'] == 'rebuttal' and len(st.session_state.live_debate_updates) <= 12:
                    st.session_state.analysis_stage = 9
                elif entry['action'] == 'critique' and len(st.session_state.live_debate_updates) <= 14:
                    st.session_state.analysis_stage = 11
                elif entry['action'] == 'refinement' and len(st.session_state.live_debate_updates) <= 16:
                    st.session_state.analysis_stage = 12
                elif entry['action'] == 'rebuttal':
                    st.session_state.analysis_stage = 13
                elif entry['action'] == 'final_evaluation':
                    st.session_state.analysis_stage = 14

            # Pass the callback to sci_agent
            sci_agent.set_debate_callback(update_debate_callback)

            # Update progress to concept extraction
            st.session_state.analysis_stage = 1

            if st.session_state.use_debate:
                # Run the debate-driven analysis
                analysis = sci_agent.analyze_mechanism_with_debate(
                    query,
                    novelty_score=novelty_score,
                    use_elo=st.session_state.use_elo_evaluation
                )

                # Final synthesis stage
                st.session_state.analysis_stage = 14

                # Store debate history if available
                if hasattr(sci_agent.debate_orchestrator, 'debate_history'):
                    st.session_state.debate_history = sci_agent.debate_orchestrator.debate_history
            else:
                # Update progress for standard analysis
                st.session_state.analysis_stage = 2

                # Run the standard analysis
                analysis = sci_agent.analyze_mechanism(
                    query,
                    novelty_score=novelty_score,
                    include_established=st.session_state.include_established
                )

                # Standard analysis completion
                st.session_state.analysis_stage = 6

                # Reset debate history
                st.session_state.debate_history = None

            # Store results and clear status displays
            st.session_state.analysis_results = analysis
            st.session_state.analysis_running = False
            st.session_state.analysis_stage = 0  # Reset progress for next time
            analysis_progress_container.empty()

        except Exception as e:
            # Show error and clear progress displays
            analysis_progress_container.empty()
            st.error(f"Error in analysis: {str(e)}")
            st.error("The extended thinking analysis encountered an error. Please try again with a different query or check the logs for details.")
            st.session_state.analysis_running = False
            st.session_state.analysis_stage = 0
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

        # Display Elo rating if available
        if "elo_evaluation" in analysis and st.session_state.use_elo_evaluation:
            st.subheader("Hypothesis Evaluation")

            elo_col1, elo_col2 = st.columns(2)
            with elo_col1:
                st.metric(
                    "Best Hypothesis Elo Rating", 
                    f"{analysis['elo_evaluation']['best_hypothesis_rating']:.0f}",
                    help="Higher Elo ratings indicate stronger scientific explanations"
                )
            with elo_col2:
                # Display number of hypotheses compared
                if "leaderboard" in analysis["elo_evaluation"]:
                    st.metric("Hypotheses Evaluated", f"{len(analysis['elo_evaluation']['leaderboard'])}")

            # Show Elo leaderboard
            with st.expander("View Hypothesis Leaderboard", expanded=False):
                st.markdown("### Hypothesis Elo Leaderboard")
                st.markdown("Hypotheses ranked by Elo rating (similar to chess ratings):")

                leaderboard_data = analysis["elo_evaluation"]["leaderboard"]
                for item in leaderboard_data:
                    st.markdown(f"**{item['rank']}.** Hypothesis #{item['hypothesis_id'][:8]} - **{item['rating']:.0f}** Elo")

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

                if st.session_state.use_elo_evaluation:
                    st.markdown("""
                    This analysis was refined through multiple rounds of scientific debate, with hypotheses evaluated using an Elo-based rating system similar to Google's Coscientist approach.
                    """)
                else:
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

                    elif entry['action'] == 'final_evaluation' and st.session_state.use_elo_evaluation:
                        if 'rankings' in entry['content']:
                            st.markdown("*Elo Tournament Results:*")
                            for rank in entry['content']['rankings'][:3]:  # Top 3
                                st.markdown(f"- Rank {rank['rank']}: Hypothesis #{rank['hypothesis_id'][:8]} (Rating: {rank['rating']:.0f})")

                    # Add timestamp
                    st.caption(f"Timestamp: {entry['timestamp']}")
                    st.markdown("---")

        # Add citation for extended thinking capabilities
        st.markdown("---")
        # Show the appropriate token information based on thinking mode
        if st.session_state.thinking_mode == "high":
            output_tokens = "80K"
            thinking_tokens = "64K"
        elif st.session_state.thinking_mode == "low":
            output_tokens = "64K"
            thinking_tokens = "32K"
        else:  # none
            output_tokens = "32K" 
            thinking_tokens = "0"

        thinking_mode_text = "extended thinking" if st.session_state.thinking_mode != "none" else "standard processing"

        # Add Elo evaluation information if used
        if st.session_state.use_elo_evaluation and st.session_state.use_debate:
            st.caption(f"Analysis powered by Claude 3.7 Sonnet's {thinking_mode_text} capabilities ({output_tokens} output tokens, {thinking_tokens} thinking tokens) with Elo-based hypothesis evaluation inspired by Google's Coscientist")
        else:
            st.caption(f"Analysis powered by Claude 3.7 Sonnet's {thinking_mode_text} capabilities ({output_tokens} output tokens, {thinking_tokens} thinking tokens)")