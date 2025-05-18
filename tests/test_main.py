import sys
import os

# Add the parent directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../app')))

import pytest
from app.main import create_person, create_disease, create_relationship, fetch_person_diseases, GraphVisualizer
from app.main import driver  # Assuming 'driver' is defined for Neo4j session management


# Fixture to clear data before tests run (optional)
@pytest.fixture(scope="module")
def setup_neo4j():
    # Clear existing data before tests run
    with driver.session() as session:
        session.run("MATCH (n) DETACH DELETE n")  # Clear the database


def test_create_person(setup_neo4j):
    # Create a new person
    success, message = create_person("Bob", 25)
    assert success == True

    # Fetch diseases for Bob (Bob should not have any diseases yet)
    result = fetch_person_diseases("Bob")

    # Assert that there are no diseases for Bob
    assert len(result) == 0


def test_create_relationship(setup_neo4j):
    # Create a new person and disease
    success1, msg1 = create_person("Charlie", 40)
    success2, msg2 = create_disease("Tuberculosis", "Infectious bacterial disease")
    assert success1 == True
    assert success2 == True

    # Create a relationship between Charlie and Tuberculosis
    success3, msg3 = create_relationship("Charlie", "Tuberculosis")
    assert success3 == True

    # Fetch diseases for Charlie
    diseases = fetch_person_diseases("Charlie")

    # Debugging: Check the diseases fetched
    print(f"Test Fetch Diseases for Charlie: {diseases}")

    # Assert that Charlie has 1 disease, and that it is Tuberculosis
    assert len(diseases) == 1
    assert diseases[0]['d.name'] == "Tuberculosis"
    assert diseases[0]['d.description'] == "Infectious bacterial disease"


def test_graph_visualizer(setup_neo4j):
    # Create a person and diseases, and add relationships for graph visualisation
    success1, msg1 = create_person("Alice", 30)
    success2, msg2 = create_disease("HIV", "Human Immunodeficiency Virus")
    success3, msg3 = create_relationship("Alice", "HIV")
    assert success1 == True
    assert success2 == True
    assert success3 == True

    # Create an instance of GraphVisualizer for the person Alice
    graph_visualizer = GraphVisualizer("Alice")
    
    # Fetch data and build the graph
    graph_visualizer.fetch_data()
    graph_visualizer.build_graph()
    
    # Visualise the graph (this will generate an HTML file that is shown in Gradio)
    graph_visualizer.visualize()
    
    # You can also add additional assertions to ensure the graph is correct, e.g., 
    # checking that the graph contains the nodes and relationships you expect
    # (e.g., 'Alice' -> 'HIV' relationship)
    assert 'Alice' in graph_visualizer.graph.nodes
    assert 'HIV' in graph_visualizer.graph.nodes
    assert graph_visualizer.graph.has_edge('Alice', 'HIV')
