import streamlit as st
from ..reasoning.sci_agent import SciAgent
from ..knowledge.pubtator import PubTatorClient

def main_page():
    st.title("SciDiscover")
    st.markdown("""
    A scientific discovery framework for analyzing molecular mechanisms and pathways.
    Powered by advanced language models and scientific knowledge bases.
    """)

    sci_agent = SciAgent()
    pubtator = PubTatorClient()

    query = st.text_area(
        "Enter your scientific query:",
        height=100,
        help="Describe the molecular mechanism or pathway you want to analyze"
    )

    if st.button("Analyze", type="primary"):
        if not query:
            st.warning("Please enter a scientific query to analyze.")
            return

        with st.spinner("Performing deep scientific analysis..."):
            analysis = sci_agent.analyze_mechanism(query)

            if "error" in analysis:
                st.error("Error in analysis. Please try again.")
                return

            # Display Primary Analysis
            st.header("Molecular Mechanism Analysis")

            # Show confidence score
            confidence = analysis.get("confidence_score", 0)
            st.metric("Analysis Confidence Score", f"{confidence:.2f}")

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