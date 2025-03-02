import streamlit as st
import plotly.graph_objects as go
import networkx as nx

def render_header():
    st.title("SciDiscover")
    st.markdown("""
    A scientific discovery framework for hypothesis generation and concept connection.
    """)

def render_search_box():
    return st.text_input("Enter scientific concepts or keywords:", "")

def render_concept_network(graph):
    pos = nx.spring_layout(graph)
    edge_trace = go.Scatter(
        x=[],
        y=[],
        line=dict(width=0.5, color='#888'),
        hoverinfo='none',
        mode='lines')

    node_trace = go.Scatter(
        x=[],
        y=[],
        mode='markers+text',
        hoverinfo='text',
        marker=dict(
            showscale=True,
            colorscale='YlGnBu',
            size=10,
        ))

    for edge in graph.edges():
        x0, y0 = pos[edge[0]]
        x1, y1 = pos[edge[1]]
        edge_trace['x'] += (x0, x1, None)
        edge_trace['y'] += (y0, y1, None)

    for node in graph.nodes():
        x, y = pos[node]
        node_trace['x'] += (x,)
        node_trace['y'] += (y,)

    fig = go.Figure(data=[edge_trace, node_trace],
                   layout=go.Layout(
                       showlegend=False,
                       hovermode='closest',
                       margin=dict(b=0,l=0,r=0,t=0),
                   ))
    
    st.plotly_chart(fig)

def render_hypothesis_output(hypothesis):
    st.subheader("Generated Hypothesis")
    st.write(hypothesis)
    
def render_entity_table(entities):
    if entities:
        st.subheader("Identified Entities")
        st.table(entities)
