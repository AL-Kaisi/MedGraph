#!/usr/bin/env python
"""Sample data loader for MedGraph demonstration."""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.main import create_person, create_disease, create_relationship

def load_sample_data():
    """Load sample data into the database."""
    print("Loading sample data...")
    
    # Create sample persons
    persons = [
        ("John Doe", 45),
        ("Jane Smith", 32),
        ("Bob Johnson", 67),
        ("Alice Williams", 28),
        ("Charlie Brown", 55)
    ]
    
    # Create sample diseases
    diseases = [
        ("Type 2 Diabetes", "A chronic condition affecting glucose metabolism"),
        ("Hypertension", "High blood pressure condition"),
        ("COVID-19", "Respiratory illness caused by SARS-CoV-2"),
        ("Asthma", "Chronic respiratory condition causing breathing difficulties"),
        ("Arthritis", "Inflammation of joints causing pain and stiffness")
    ]
    
    # Create persons
    for name, age in persons:
        success, message = create_person(name, age)
        print(f"Person: {message}")
    
    # Create diseases
    for name, description in diseases:
        success, message = create_disease(name, description)
        print(f"Disease: {message}")
    
    # Create relationships
    relationships = [
        ("John Doe", "Type 2 Diabetes"),
        ("John Doe", "Hypertension"),
        ("Jane Smith", "Asthma"),
        ("Bob Johnson", "Arthritis"),
        ("Bob Johnson", "Hypertension"),
        ("Alice Williams", "COVID-19"),
        ("Charlie Brown", "Type 2 Diabetes"),
        ("Charlie Brown", "Arthritis")
    ]
    
    for person, disease in relationships:
        success, message = create_relationship(person, disease)
        print(f"Relationship: {message}")
    
    print("\nSample data loaded successfully!")
    print("You can now run the Gradio app to visualise the data.")

if __name__ == "__main__":
    load_sample_data()