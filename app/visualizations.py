#!/usr/bin/env python
"""Medical data visualization functions."""

import networkx as nx
from pyvis.network import Network
from collections import Counter
import json
from app.main import driver

def get_hospital_overview_graph():
    """Generate hospital-wide visualization of all patients and diseases."""
    try:
        with driver.session() as session:
            # Get all relationships
            query = """
                MATCH (p:Person)-[r:DIAGNOSED_WITH]->(d:Disease)
                RETURN p.name AS patient, p.age AS age, d.name AS disease, 
                       r.severity AS severity, r.status AS status
            """
            result = session.run(query)
            
            # Create network
            net = Network(height="600px", width="100%", directed=True,
                         bgcolor="#ffffff", font_color="#000000")
            
            # Track nodes to avoid duplicates
            patients = set()
            diseases = set()
            
            for record in result:
                patient = record["patient"]
                disease = record["disease"]
                severity = record["severity"]
                status = record["status"]
                
                # Add patient node
                if patient not in patients:
                    net.add_node(patient, label=patient, color="#3498db", 
                                title=f"Patient: {patient}\nAge: {record['age']}",
                                shape="circle", size=20)
                    patients.add(patient)
                
                # Add disease node
                if disease not in diseases:
                    net.add_node(disease, label=disease, color="#e74c3c",
                                title=f"Disease: {disease}", shape="square", size=15)
                    diseases.add(disease)
                
                # Add edge with severity color
                edge_color = {
                    "mild": "#2ecc71",
                    "moderate": "#f39c12",
                    "severe": "#e74c3c",
                    "critical": "#9b59b6"
                }.get(severity, "#95a5a6")
                
                if status == "active":
                    net.add_edge(patient, disease, color=edge_color, 
                               title=f"Severity: {severity}\nStatus: {status}")
            
            # Set physics
            net.set_options("""
                var options = {
                    "physics": {
                        "barnesHut": {
                            "gravitationalConstant": -10000,
                            "springConstant": 0.001,
                            "springLength": 200
                        },
                        "minVelocity": 0.75
                    },
                    "edges": {
                        "smooth": {
                            "type": "continuous"
                        }
                    },
                    "nodes": {
                        "font": {
                            "size": 12
                        }
                    }
                }
            """)
            
            return net.get_graph()
    except Exception as e:
        print(f"Error creating hospital overview graph: {str(e)}")
        return None

def get_disease_distribution():
    """Get disease distribution statistics."""
    try:
        with driver.session() as session:
            query = """
                MATCH (p:Person)-[r:DIAGNOSED_WITH]->(d:Disease)
                WHERE r.status = 'active'
                RETURN d.name AS disease, COUNT(p) AS patient_count
                ORDER BY patient_count DESC
                LIMIT 10
            """
            result = session.run(query)
            
            data = {
                "labels": [],
                "values": [],
                "colors": []
            }
            
            colors = ["#3498db", "#e74c3c", "#2ecc71", "#f39c12", "#9b59b6",
                     "#1abc9c", "#34495e", "#e67e22", "#95a5a6", "#d35400"]
            
            for i, record in enumerate(result):
                data["labels"].append(record["disease"])
                data["values"].append(record["patient_count"])
                data["colors"].append(colors[i % len(colors)])
            
            return data
    except Exception as e:
        print(f"Error getting disease distribution: {str(e)}")
        return {"labels": [], "values": [], "colors": []}

def get_severity_distribution():
    """Get severity distribution of active diagnoses."""
    try:
        with driver.session() as session:
            query = """
                MATCH (p:Person)-[r:DIAGNOSED_WITH]->(d:Disease)
                WHERE r.status = 'active'
                RETURN r.severity AS severity, COUNT(*) AS count
            """
            result = session.run(query)
            
            severities = {"mild": 0, "moderate": 0, "severe": 0, "critical": 0}
            
            for record in result:
                severity = record["severity"]
                if severity in severities:
                    severities[severity] = record["count"]
            
            return {
                "labels": list(severities.keys()),
                "values": list(severities.values()),
                "colors": ["#2ecc71", "#f39c12", "#e74c3c", "#9b59b6"]
            }
    except Exception as e:
        print(f"Error getting severity distribution: {str(e)}")
        return {"labels": [], "values": [], "colors": []}

def get_patient_timeline(patient_name):
    """Get patient's medical timeline."""
    try:
        with driver.session() as session:
            # Get diagnoses timeline
            diagnoses_query = """
                MATCH (p:Person {name: $name})-[r:DIAGNOSED_WITH]->(d:Disease)
                RETURN d.name AS disease, r.date AS date, r.severity AS severity,
                       r.status AS status, 'diagnosis' AS type
                ORDER BY r.date DESC
            """
            
            # Get prescriptions timeline
            rx_query = """
                MATCH (p:Person {name: $name})-[:HAS_PRESCRIPTION]->(rx:Prescription)
                RETURN rx.medication AS item, rx.prescribed_date AS date,
                       rx.status AS status, 'prescription' AS type
                ORDER BY rx.prescribed_date DESC
            """
            
            # Get vitals timeline
            vitals_query = """
                MATCH (p:Person {name: $name})-[:HAS_VITALS]->(v:VitalSigns)
                RETURN 'Vitals Recorded' AS item, v.recorded_at AS date,
                       'active' AS status, 'vitals' AS type
                ORDER BY v.recorded_at DESC
                LIMIT 10
            """
            
            timeline = []
            
            # Execute queries
            for query, params in [(diagnoses_query, {"name": patient_name}),
                                 (rx_query, {"name": patient_name}),
                                 (vitals_query, {"name": patient_name})]:
                result = session.run(query, params)
                for record in result:
                    timeline.append(dict(record))
            
            # Sort by date
            timeline.sort(key=lambda x: x["date"], reverse=True)
            
            return timeline
    except Exception as e:
        print(f"Error getting patient timeline: {str(e)}")
        return []

def get_doctor_performance_stats(doctor_name):
    """Get performance statistics for a doctor."""
    try:
        with driver.session() as session:
            # Total patients treated
            patients_query = """
                MATCH (p:Person)-[r:DIAGNOSED_WITH]->(d:Disease)
                WHERE r.doctor = $doctor
                RETURN COUNT(DISTINCT p) AS total_patients
            """
            
            # Diagnoses by severity
            severity_query = """
                MATCH (p:Person)-[r:DIAGNOSED_WITH]->(d:Disease)
                WHERE r.doctor = $doctor
                RETURN r.severity AS severity, COUNT(*) AS count
            """
            
            # Most common diseases treated
            diseases_query = """
                MATCH (p:Person)-[r:DIAGNOSED_WITH]->(d:Disease)
                WHERE r.doctor = $doctor
                RETURN d.name AS disease, COUNT(*) AS count
                ORDER BY count DESC
                LIMIT 5
            """
            
            # Prescriptions written
            rx_query = """
                MATCH (p:Person)-[:HAS_PRESCRIPTION]->(rx:Prescription)
                WHERE rx.doctor = $doctor
                RETURN COUNT(*) AS total_prescriptions
            """
            
            stats = {
                "total_patients": 0,
                "severity_distribution": {},
                "common_diseases": [],
                "total_prescriptions": 0
            }
            
            # Execute queries
            result = session.run(patients_query, doctor=doctor_name)
            stats["total_patients"] = result.single()["total_patients"]
            
            result = session.run(severity_query, doctor=doctor_name)
            for record in result:
                stats["severity_distribution"][record["severity"]] = record["count"]
            
            result = session.run(diseases_query, doctor=doctor_name)
            for record in result:
                stats["common_diseases"].append({
                    "disease": record["disease"],
                    "count": record["count"]
                })
            
            result = session.run(rx_query, doctor=doctor_name)
            stats["total_prescriptions"] = result.single()["total_prescriptions"]
            
            return stats
    except Exception as e:
        print(f"Error getting doctor stats: {str(e)}")
        return {}

def get_disease_network(disease_name):
    """Get network visualization for a specific disease."""
    try:
        with driver.session() as session:
            # Get all patients with this disease and their other conditions
            query = """
                MATCH (p:Person)-[r1:DIAGNOSED_WITH]->(d1:Disease {name: $disease})
                OPTIONAL MATCH (p)-[r2:DIAGNOSED_WITH]->(d2:Disease)
                WHERE d2.name <> $disease AND r2.status = 'active'
                RETURN p.name AS patient, p.age AS age, 
                       d2.name AS other_disease, r2.severity AS severity
            """
            result = session.run(query, disease=disease_name)
            
            # Create network
            net = Network(height="500px", width="100%", directed=False,
                         bgcolor="#ffffff", font_color="#000000")
            
            # Add the main disease node
            net.add_node(disease_name, label=disease_name, color="#e74c3c",
                        size=30, shape="star")
            
            patients = set()
            diseases = set()
            
            for record in result:
                patient = record["patient"]
                other_disease = record["other_disease"]
                
                # Add patient node
                if patient not in patients:
                    net.add_node(patient, label=patient, color="#3498db",
                                title=f"Patient: {patient}\nAge: {record['age']}")
                    patients.add(patient)
                    net.add_edge(disease_name, patient, color="#e74c3c")
                
                # Add other disease nodes
                if other_disease and other_disease not in diseases:
                    net.add_node(other_disease, label=other_disease, 
                                color="#95a5a6", shape="square")
                    diseases.add(other_disease)
                    net.add_edge(patient, other_disease, color="#95a5a6")
            
            return net.get_graph()
    except Exception as e:
        print(f"Error creating disease network: {str(e)}")
        return None
