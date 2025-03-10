import networkx as nx
from pyvis.network import Network
from neo4j import GraphDatabase
import streamlit as st  # Import Streamlit
import os
from dotenv import load_dotenv

load_dotenv()

# Now you can access the environment variables
uri = os.getenv("NEO4J_URI")
username = os.getenv("NEO4J_USERNAME")
password = os.getenv("NEO4J_PASSWORD")

# Create a Neo4j driver
driver = GraphDatabase.driver(uri, auth=(username, password))

def create_person(name, age):
    """Creates a Person node in Neo4j."""
    with driver.session() as session:
        session.run("CREATE (a:Person {name: $name, age: $age})", name=name, age=age)

def create_disease(name, description):
    """Creates a Disease node in Neo4j."""
    with driver.session() as session:
        session.run("CREATE (d:Disease {name: $name, description: $description})", name=name, description=description)

def create_relationship(person_name, disease_name):
    """Creates a relationship between Person and Disease in Neo4j."""
    with driver.session() as session:
        # Check if the relationship already exists
        result = session.run("""
            MATCH (p:Person {name: $person_name})-[:HAS_DISEASE]->(d:Disease {name: $disease_name})
            RETURN COUNT(*) AS count
        """, person_name=person_name, disease_name=disease_name)

        # Debugging: Check if the relationship already exists
        count = result.single()['count']
        print(f"Checking existing relationship for {person_name} and {disease_name}. Found count: {count}")

        # If the relationship doesn't exist, create it
        if count == 0:
            session.run("""
                MATCH (p:Person {name: $person_name}), (d:Disease {name: $disease_name})
                CREATE (p)-[:HAS_DISEASE]->(d)
            """, person_name=person_name, disease_name=disease_name)
            print(f"Created relationship between {person_name} and {disease_name}")
        else:
            print(f"Relationship already exists between {person_name} and {disease_name}")

def fetch_person_diseases(name):
    """Fetch diseases related to a person."""
    with driver.session() as session:
        result = session.run("""
            MATCH (p:Person {name: $name})-[:HAS_DISEASE]->(d:Disease)
            RETURN d.name AS disease_name, d.description AS disease_description
        """, name=name)
        
        diseases = [{"d.name": record["disease_name"], "d.description": record["disease_description"]} for record in result]
        
        # Debugging output
        print(f"Fetched diseases for {name}: {diseases}")
        
        return diseases


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

        # Remove duplicate diseases by using a set for disease names
        seen_diseases = set()

        # Add disease nodes and relationships
        for disease in self.diseases:
            disease_name = disease['d.name']
            disease_description = disease['d.description']

            # Only add unique diseases
            if disease_name not in seen_diseases:
                seen_diseases.add(disease_name)
                # Add disease node
                self.graph.add_node(disease_name, label=disease_name, title=disease_description, color="green")
                # Add an edge between the person and the disease
                self.graph.add_edge(self.person_name, disease_name)

        # Debugging: Check the graph nodes and edges
        print(f"Graph nodes: {self.graph.nodes}")
        print(f"Graph edges: {self.graph.edges}")

        if len(self.graph.nodes) == 0 or len(self.graph.edges) == 0:
            print("Error: The graph has no nodes or edges.")
            st.error("No data to visualize.")

    def visualize(self):
        """Visualize the graph using Pyvis."""
        try:
            # Ensure the graph has nodes and edges before rendering
            if len(self.graph.nodes) == 0 or len(self.graph.edges) == 0:
                print("Error: The graph has no nodes or edges.")
                st.error("No data to visualize.")
                return

            # Create a Pyvis network for visualization
            net = Network(height="600px", width="100%", directed=False)
            net.from_nx(self.graph)

            # Define a path for saving the HTML file
            output_path = os.path.join(os.getcwd(), "graph_output.html")

            # Write the graph to an HTML file explicitly
            net.save_graph(output_path)

            # Check if the file exists
            if os.path.exists(output_path):
                # Read the generated HTML file and display it in Streamlit
                with open(output_path, "r") as file:
                    st.components.v1.html(file.read(), height=600)
            else:
                st.error("Error: Graph HTML file not found.")

        except Exception as e:
            print(f"Error while generating the graph: {e}")
            st.error("There was an issue generating the graph visualization.")
