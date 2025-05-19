import networkx as nx
from pyvis.network import Network
from neo4j import GraphDatabase
# Removed Streamlit import - using Flask instead
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
    try:
        with driver.session() as session:
            # Check if person already exists
            result = session.run("MATCH (p:Person {name: $name}) RETURN p", name=name)
            if result.single():
                return False, f"Person '{name}' already exists"

            session.run("CREATE (a:Person {name: $name, age: $age})", name=name, age=age)
            return True, f"Successfully created person '{name}'"
    except Exception as e:
        return False, f"Error creating person: {str(e)}"

def create_disease(name, description):
    """Creates a Disease node in Neo4j."""
    try:
        with driver.session() as session:
            # Check if disease already exists
            result = session.run("MATCH (d:Disease {name: $name}) RETURN d", name=name)
            if result.single():
                return False, f"Disease '{name}' already exists"

            session.run("CREATE (d:Disease {name: $name, description: $description})", name=name, description=description)
            return True, f"Successfully created disease '{name}'"
    except Exception as e:
        return False, f"Error creating disease: {str(e)}"

def create_relationship(person_name, disease_name):
    """Creates a relationship between Person and Disease in Neo4j."""
    try:
        with driver.session() as session:
            # Check if person exists
            person_result = session.run("MATCH (p:Person {name: $name}) RETURN p", name=person_name)
            if not person_result.single():
                return False, f"Person '{person_name}' does not exist"

            # Check if disease exists
            disease_result = session.run("MATCH (d:Disease {name: $name}) RETURN d", name=disease_name)
            if not disease_result.single():
                return False, f"Disease '{disease_name}' does not exist"

            # Check if the relationship already exists
            result = session.run("""
                MATCH (p:Person {name: $person_name})-[:HAS_DISEASE]->(d:Disease {name: $disease_name})
                RETURN COUNT(*) AS count
            """, person_name=person_name, disease_name=disease_name)

            count = result.single()['count']

            # If the relationship doesn't exist, create it
            if count == 0:
                session.run("""
                    MATCH (p:Person {name: $person_name}), (d:Disease {name: $disease_name})
                    CREATE (p)-[:HAS_DISEASE]->(d)
                """, person_name=person_name, disease_name=disease_name)
                return True, f"Successfully created relationship between '{person_name}' and '{disease_name}'"
            else:
                return False, f"Relationship already exists between '{person_name}' and '{disease_name}'"
    except Exception as e:
        return False, f"Error creating relationship: {str(e)}"

def fetch_person_diseases(name):
    """Fetch diseases related to a person."""
    try:
        with driver.session() as session:
            result = session.run("""
                MATCH (p:Person {name: $name})-[:HAS_DISEASE]->(d:Disease)
                RETURN d.name AS disease_name, d.description AS disease_description
            """, name=name)

            diseases = [{"d.name": record["disease_name"], "d.description": record["disease_description"]} for record in result]
            return diseases
    except Exception as e:
        print(f"Error fetching diseases: {str(e)}")
        return []

def get_all_persons():
    """Get all persons in the database."""
    try:
        with driver.session() as session:
            result = session.run("MATCH (p:Person) RETURN p.name AS name, p.age AS age ORDER BY p.name")
            return [{"name": record["name"], "age": record["age"]} for record in result]
    except Exception as e:
        print(f"Error fetching persons: {str(e)}")
        return []

def get_all_diseases():
    """Get all diseases in the database."""
    try:
        with driver.session() as session:
            result = session.run("MATCH (d:Disease) RETURN d.name AS name, d.description AS description ORDER BY d.name")
            return [{"name": record["name"], "description": record["description"]} for record in result]
    except Exception as e:
        print(f"Error fetching diseases: {str(e)}")
        return []

def search_patients(search_term):
    """Search patients by name."""
    try:
        with driver.session() as session:
            query = """
                MATCH (p:Person)
                WHERE toLower(p.name) CONTAINS toLower($search_term)
                RETURN p.name AS name, p.age AS age
                ORDER BY p.name
                LIMIT 20
            """
            result = session.run(query, search_term=search_term)
            return [{"name": record["name"], "age": record["age"]} for record in result]
    except Exception as e:
        print(f"Error searching patients: {str(e)}")
        return []

def get_patient_details(name):
    """Get detailed patient information including all diseases."""
    try:
        with driver.session() as session:
            # Get patient basic info
            patient_query = """
                MATCH (p:Person {name: $name})
                RETURN p.name AS name, p.age AS age
            """
            patient_result = session.run(patient_query, name=name).single()

            if not patient_result:
                return None

            patient_info = {
                "name": patient_result["name"],
                "age": patient_result["age"],
                "diseases": []
            }

            # Get all diseases for this patient
            diseases_query = """
                MATCH (p:Person {name: $name})-[:HAS_DISEASE]->(d:Disease)
                RETURN d.name AS name, d.description AS description
                ORDER BY d.name
            """
            diseases_result = session.run(diseases_query, name=name)

            for record in diseases_result:
                patient_info["diseases"].append({
                    "name": record["name"],
                    "description": record["description"]
                })

            return patient_info
    except Exception as e:
        print(f"Error fetching patient details: {str(e)}")
        return None

def delete_relationship(person_name, disease_name):
    """Delete a relationship between person and disease."""
    try:
        with driver.session() as session:
            # Check if the relationship exists
            check_query = """
                MATCH (p:Person {name: $person_name})-[r:HAS_DISEASE]->(d:Disease {name: $disease_name})
                RETURN COUNT(r) AS count
            """
            result = session.run(check_query, person_name=person_name, disease_name=disease_name)

            if result.single()['count'] == 0:
                return False, f"No relationship exists between '{person_name}' and '{disease_name}'"

            # Delete the relationship
            delete_query = """
                MATCH (p:Person {name: $person_name})-[r:HAS_DISEASE]->(d:Disease {name: $disease_name})
                DELETE r
            """
            session.run(delete_query, person_name=person_name, disease_name=disease_name)

            return True, f"Successfully removed relationship between '{person_name}' and '{disease_name}'"
    except Exception as e:
        return False, f"Error deleting relationship: {str(e)}"


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
            raise ValueError("No data to visualize.")

    def visualize(self):
        """Visualize the graph using Pyvis."""
        try:
            # Ensure the graph has nodes and edges before rendering
            if len(self.graph.nodes) == 0 or len(self.graph.edges) == 0:
                print("Error: The graph has no nodes or edges.")
                raise ValueError("No data to visualize.")

            # Create a Pyvis network for visualization
            net = Network(height="600px", width="100%", directed=False)
            net.from_nx(self.graph)

            # Define a path for saving the HTML file
            output_path = os.path.join(os.getcwd(), "graph_output.html")

            # Write the graph to an HTML file explicitly
            net.save_graph(output_path)

            # Check if the file exists
            if os.path.exists(output_path):
                # Return the path to the generated HTML file
                return output_path
            else:
                raise FileNotFoundError("Error: Graph HTML file not found.")

        except Exception as e:
            print(f"Error while generating the graph: {e}")
            raise Exception(f"There was an issue generating the graph visualization: {e}")
