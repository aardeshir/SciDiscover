import streamlit as st
from .components import (
    render_header,
    render_search_box,
    render_concept_network,
    render_hypothesis_output,
    render_entity_table
)
from ..orchestrator.workflow import ScientificWorkflow
from ..knowledge.pubtator import PubTatorClient
from ..reasoning.hypothesis import HypothesisGenerator

def main_page():
    render_header()
    
    workflow = ScientificWorkflow()
    pubtator = PubTatorClient()
    hypothesis_gen = HypothesisGenerator()

    with st.sidebar:
        st.subheader("Analysis Options")
        analysis_type = st.selectbox(
            "Select Analysis Type",
            ["Concept Connection", "Hypothesis Generation", "Entity Identification"]
        )

    search_query = render_search_box()
    
    if st.button("Analyze"):
        with st.spinner("Processing..."):
            if analysis_type == "Concept Connection":
                graph = workflow.connect_concepts(search_query)
                render_concept_network(graph)
                
            elif analysis_type == "Hypothesis Generation":
                hypothesis = hypothesis_gen.generate(search_query)
                render_hypothesis_output(hypothesis)
                
            elif analysis_type == "Entity Identification":
                entities = pubtator.identify_entities(search_query)
                render_entity_table(entities)
