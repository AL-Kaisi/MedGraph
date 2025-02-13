import sys
import os

# Add the parent directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import streamlit as st
from app.main import create_person, create_disease, create_relationship, fetch_person_diseases, GraphVisualizer

# Set up the title of the app
st.title("Graph RAG - Neo4j Integration")

# Sidebar for navigation
st.sidebar.title("Navigation")
option = st.sidebar.radio("Select an option", ("Create Person", "Create Disease", "Create Relationship", "View Diseases", "View Disease Graph"))

# Create Person section
if option == "Create Person":
    st.subheader("Create a Person")
    name = st.text_input("Enter person's name")
    age = st.number_input("Enter person's age", min_value=1)

    if st.button("Create Person"):
        if name and age:
            create_person(name, age)
            st.success(f"Person '{name}' created successfully!")
        else:
            st.error("Please provide valid inputs.")

# Create Disease section
elif option == "Create Disease":
    st.subheader("Create a Disease")
    disease_name = st.text_input("Enter disease name")
    description = st.text_area("Enter disease description")

    if st.button("Create Disease"):
        if disease_name and description:
            create_disease(disease_name, description)
            st.success(f"Disease '{disease_name}' created successfully!")
        else:
            st.error("Please provide valid inputs.")

# Create Relationship section
elif option == "Create Relationship":
    st.subheader("Create a Relationship between Person and Disease")
    person_name = st.text_input("Enter person's name")
    
    # Disease selection dropdown
    disease_options = ["diabetes", "HIV", "Cancer", "Hypertension"]  # Add more diseases
    disease_name = st.selectbox("Select disease", disease_options)

    if st.button("Create Relationship"):
        if person_name and disease_name:
            create_relationship(person_name, disease_name)
            st.success(f"Relationship between '{person_name}' and '{disease_name}' created successfully!")
        else:
            st.error("Please provide valid inputs.")

# View Diseases section
elif option == "View Diseases":
    st.subheader("View Diseases of a Person")
    person_for_diseases = st.text_input("Enter person's name to view diseases")

    if st.button("View Diseases"):
        if person_for_diseases:
            diseases = fetch_person_diseases(person_for_diseases)
            if diseases:
                for disease in diseases:
                    st.write(f"Disease: {disease['d.name']} - Description: {disease['d.description']}")
            else:
                st.write(f"No diseases found for {person_for_diseases}.")
        else:
            st.error("Please provide a person's name.")

# View Disease Graph section
elif option == "View Disease Graph":
    st.subheader("View Disease Relationships as a Graph")
    person_for_graph = st.text_input("Enter person's name to view disease graph")

    if person_for_graph:
        # Visualize the graph for the diseases of the person
        graph_visualizer = GraphVisualizer(person_for_graph)
        graph_visualizer.fetch_data()
        graph_visualizer.build_graph()
        graph_visualizer.visualize()
    else:
        st.error("Please provide a person's name to visualize the graph.")
