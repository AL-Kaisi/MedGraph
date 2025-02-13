import networkx as nx
import sys
import os

# Add the parent directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from pyvis.network import Network
import streamlit as st
from app.main import fetch_person_diseases  # assuming this function fetches the data

class GraphVisualizer:
    def __init__(self, person_name):
        self.person_name = person_name
        self.graph = nx.Graph()

    def fetch_data(self):
        """Fetch data related to the person from Neo4j."""
        self.diseases = fetch_person_diseases(self.person_name)

    def build_graph(self):
        """Build the graph based on the fetched data."""
        # Add the person as a node
        self.graph.add_node(self.person_name, label=self.person_name, color="blue")

        # Add disease nodes and relationships
        for disease in self.diseases:
            disease_name = disease['d.name']
            disease_description = disease['d.description']

            # Add disease node
            self.graph.add_node(disease_name, label=disease_name, title=disease_description, color="green")

            # Add an edge between the person and the disease
            self.graph.add_edge(self.person_name, disease_name)

    def visualize(self):
        """Visualize the graph using Pyvis."""
        # Create a Pyvis network for visualization
        net = Network(height="600px", width="100%", directed=False)
        net.from_nx(self.graph)

        # Display the graph
        net.show("graph.html")
        st.components.v1.html(open("graph.html", "r").read(), height=600)

# Streamlit UI code
st.title("Graph RAG - Neo4j Integration")

# Input to view diseases of a person
person_for_diseases = st.text_input("Enter person's name to view diseases")

if person_for_diseases:
    # Instantiate the GraphVisualizer class
    graph_visualizer = GraphVisualizer(person_for_diseases)

    # Fetch data and build the graph
    graph_visualizer.fetch_data()
    graph_visualizer.build_graph()

    # Visualize the graph
    graph_visualizer.visualize()
