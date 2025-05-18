import sys
import os

# Add the parent directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import gradio as gr
import pandas as pd
from app.main import (create_person, create_disease, create_relationship, 
                     fetch_person_diseases, GraphVisualizer, get_all_persons, 
                     get_all_diseases)

# Custom CSS for a modern look
custom_css = """
.gradio-container {
    font-family: 'Arial', sans-serif;
    background-color: #f5f7fa;
}
.gr-button-primary {
    background-color: #3498db;
    border-color: #3498db;
}
.gr-button-primary:hover {
    background-color: #2980b9;
    border-color: #2980b9;
}
.output-message {
    padding: 10px;
    border-radius: 5px;
    margin: 10px 0;
}
.success {
    background-color: #d4edda;
    border: 1px solid #c3e6cb;
    color: #155724;
}
.error {
    background-color: #f8d7da;
    border: 1px solid #f5c6cb;
    color: #721c24;
}
"""

# Title and description
title = "MedGraph - Medical Knowledge Graph"
description = "Manage patient-disease relationships with graph database technology"

# Helper functions
def create_person_handler(name, age):
    if not name or not age:
        return "Error: Please provide valid inputs."
    success, message = create_person(name, int(age))
    return f"Success: {message}" if success else f"Error: {message}"

def create_disease_handler(disease_name, description):
    if not disease_name or not description:
        return "Error: Please provide valid inputs."
    success, message = create_disease(disease_name, description)
    return f"Success: {message}" if success else f"Error: {message}"

def create_relationship_handler(person_name, disease_name):
    if not person_name or not disease_name:
        return "Error: Please provide valid inputs."
    success, message = create_relationship(person_name, disease_name)
    return f"Success: {message}" if success else f"Error: {message}"

def view_diseases_handler(person_name):
    if not person_name:
        return pd.DataFrame({"Error": ["Please provide a person's name."]})

    diseases = fetch_person_diseases(person_name)
    if not diseases:
        return pd.DataFrame({"Result": [f"No diseases found for {person_name}."]})

    # Create a pandas DataFrame for better display
    df = pd.DataFrame(diseases)
    if 'd.name' in df.columns and 'd.description' in df.columns:
        df = df.rename(columns={'d.name': 'Disease', 'd.description': 'Description'})
    return df

def view_graph_handler(person_name):
    if not person_name:
        return "<p style='color: red;'>Error: Please provide a person's name to visualise the graph.</p>"

    # Create visualisation
    graph_visualizer = GraphVisualizer(person_name)
    graph_visualizer.fetch_data()
    graph_visualizer.build_graph()
    graph_visualizer.visualize()

    # Read the generated HTML file
    output_path = os.path.join(os.getcwd(), "graph_output.html")
    if os.path.exists(output_path):
        with open(output_path, "r") as file:
            return file.read()
    else:
        return "<p style='color: red;'>Error: Graph HTML file not found.</p>"

def get_persons_list():
    persons = get_all_persons()
    return [p['name'] for p in persons]

def get_diseases_list():
    diseases = get_all_diseases()
    return [d['name'] for d in diseases]

# Create the Gradio interface
with gr.Blocks(title=title, theme=gr.themes.Soft(), css=custom_css) as app:
    gr.Markdown(f"# {title}")
    gr.Markdown(f"*{description}*")
    
    with gr.Tabs():
        # Create Person tab
        with gr.TabItem("Create Person", id=1):
            gr.Markdown("### Add a New Patient")
            with gr.Row():
                with gr.Column():
                    person_name = gr.Textbox(label="Name", placeholder="Enter patient's name")
                    person_age = gr.Number(label="Age", minimum=1, maximum=150, step=1)
                    create_person_btn = gr.Button("Create Person", variant="primary")
                with gr.Column():
                    person_output = gr.Textbox(label="Result", lines=2)
            
            create_person_btn.click(
                create_person_handler,
                inputs=[person_name, person_age],
                outputs=person_output
            )
        
        # Create Disease tab
        with gr.TabItem("Create Disease", id=2):
            gr.Markdown("### Add a New Disease")
            with gr.Row():
                with gr.Column():
                    disease_name = gr.Textbox(label="Disease Name", placeholder="Enter disease name")
                    disease_desc = gr.Textbox(label="Description", placeholder="Enter disease description", lines=3)
                    create_disease_btn = gr.Button("Create Disease", variant="primary")
                with gr.Column():
                    disease_output = gr.Textbox(label="Result", lines=2)
            
            create_disease_btn.click(
                create_disease_handler,
                inputs=[disease_name, disease_desc],
                outputs=disease_output
            )
        
        # Create Relationship tab
        with gr.TabItem("Create Relationship", id=3):
            gr.Markdown("### Link Patient to Disease")
            with gr.Row():
                with gr.Column():
                    rel_person = gr.Dropdown(label="Select Patient", choices=get_persons_list)
                    rel_disease = gr.Dropdown(label="Select Disease", choices=get_diseases_list)
                    gr.Markdown("*Refresh the page to see newly added patients and diseases*")
                    create_rel_btn = gr.Button("Create Relationship", variant="primary")
                with gr.Column():
                    rel_output = gr.Textbox(label="Result", lines=2)
            
            create_rel_btn.click(
                create_relationship_handler,
                inputs=[rel_person, rel_disease],
                outputs=rel_output
            )
        
        # View Diseases tab
        with gr.TabItem("View Diseases", id=4):
            gr.Markdown("### View Patient's Diseases")
            with gr.Row():
                with gr.Column():
                    view_person = gr.Dropdown(label="Select Patient", choices=get_persons_list)
                    view_diseases_btn = gr.Button("View Diseases", variant="primary")
                with gr.Column():
                    diseases_output = gr.Dataframe(label="Diseases", headers=['Disease', 'Description'])
            
            view_diseases_btn.click(
                view_diseases_handler,
                inputs=view_person,
                outputs=diseases_output
            )
        
        # View Graph tab
        with gr.TabItem("View Graph", id=5):
            gr.Markdown("### Visualise Patient-Disease Relationships")
            with gr.Row():
                with gr.Column():
                    graph_person = gr.Dropdown(label="Select Patient", choices=get_persons_list)
                    view_graph_btn = gr.Button("Generate Graph", variant="primary")
            
            graph_output = gr.HTML(label="Graph Visualisation")
            
            view_graph_btn.click(
                view_graph_handler,
                inputs=graph_person,
                outputs=graph_output
            )
    
    gr.Markdown("---")
    gr.Markdown("Developed by the MedGraph Team")

if __name__ == "__main__":
    app.launch(server_name="0.0.0.0", server_port=8501, share=False)