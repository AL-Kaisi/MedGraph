#!/usr/bin/env python
"""Additional medical features for the hospital system."""

import os
from datetime import datetime
from app.main import driver

def create_diagnosis(patient_name, disease_name, doctor_name, notes="", severity="moderate"):
    """Create a diagnosis record with additional medical information."""
    try:
        with driver.session() as session:
            # First, create the basic relationship
            check_query = """
                MATCH (p:Person {name: $patient_name}), (d:Disease {name: $disease_name})
                RETURN p, d
            """
            result = session.run(check_query, patient_name=patient_name, disease_name=disease_name)
            
            if not result.single():
                return False, "Patient or disease not found"
            
            # Create diagnosis with metadata
            diagnosis_query = """
                MATCH (p:Person {name: $patient_name}), (d:Disease {name: $disease_name})
                CREATE (p)-[r:DIAGNOSED_WITH {
                    doctor: $doctor_name,
                    date: $date,
                    notes: $notes,
                    severity: $severity,
                    status: 'active'
                }]->(d)
                RETURN r
            """
            
            session.run(diagnosis_query, 
                       patient_name=patient_name,
                       disease_name=disease_name,
                       doctor_name=doctor_name,
                       date=datetime.now().isoformat(),
                       notes=notes,
                       severity=severity)
            
            return True, "Diagnosis created successfully"
    except Exception as e:
        return False, f"Error creating diagnosis: {str(e)}"

def add_medical_history(patient_name, condition, date_diagnosed, resolved=False, notes=""):
    """Add medical history entry for a patient."""
    try:
        with driver.session() as session:
            query = """
                MATCH (p:Person {name: $patient_name})
                CREATE (h:MedicalHistory {
                    condition: $condition,
                    date_diagnosed: $date_diagnosed,
                    resolved: $resolved,
                    notes: $notes,
                    created_at: $created_at
                })
                CREATE (p)-[:HAS_HISTORY]->(h)
                RETURN h
            """
            
            session.run(query,
                       patient_name=patient_name,
                       condition=condition,
                       date_diagnosed=date_diagnosed,
                       resolved=resolved,
                       notes=notes,
                       created_at=datetime.now().isoformat())
            
            return True, "Medical history added successfully"
    except Exception as e:
        return False, f"Error adding medical history: {str(e)}"

def add_prescription(patient_name, medication, dosage, frequency, doctor_name, duration="", notes=""):
    """Add prescription for a patient."""
    try:
        with driver.session() as session:
            query = """
                MATCH (p:Person {name: $patient_name})
                CREATE (rx:Prescription {
                    medication: $medication,
                    dosage: $dosage,
                    frequency: $frequency,
                    doctor: $doctor_name,
                    duration: $duration,
                    notes: $notes,
                    prescribed_date: $prescribed_date,
                    status: 'active'
                })
                CREATE (p)-[:HAS_PRESCRIPTION]->(rx)
                RETURN rx
            """
            
            session.run(query,
                       patient_name=patient_name,
                       medication=medication,
                       dosage=dosage,
                       frequency=frequency,
                       doctor_name=doctor_name,
                       duration=duration,
                       notes=notes,
                       prescribed_date=datetime.now().isoformat())
            
            return True, "Prescription added successfully"
    except Exception as e:
        return False, f"Error adding prescription: {str(e)}"

def add_vitals(patient_name, blood_pressure, heart_rate, temperature, weight, height, notes=""):
    """Record patient vital signs."""
    try:
        with driver.session() as session:
            query = """
                MATCH (p:Person {name: $patient_name})
                CREATE (v:VitalSigns {
                    blood_pressure: $blood_pressure,
                    heart_rate: $heart_rate,
                    temperature: $temperature,
                    weight: $weight,
                    height: $height,
                    bmi: $bmi,
                    notes: $notes,
                    recorded_at: $recorded_at
                })
                CREATE (p)-[:HAS_VITALS]->(v)
                RETURN v
            """
            
            # Calculate BMI if height and weight provided
            bmi = None
            if height and weight:
                height_m = float(height) / 100  # Convert cm to m
                bmi = float(weight) / (height_m * height_m)
            
            session.run(query,
                       patient_name=patient_name,
                       blood_pressure=blood_pressure,
                       heart_rate=heart_rate,
                       temperature=temperature,
                       weight=weight,
                       height=height,
                       bmi=bmi,
                       notes=notes,
                       recorded_at=datetime.now().isoformat())
            
            return True, "Vital signs recorded successfully"
    except Exception as e:
        return False, f"Error recording vital signs: {str(e)}"

def get_patient_medical_record(patient_name):
    """Get complete medical record for a patient."""
    try:
        with driver.session() as session:
            # Get patient info
            patient_query = """
                MATCH (p:Person {name: $name})
                RETURN p.name AS name, p.age AS age
            """
            patient_result = session.run(patient_query, name=patient_name).single()
            
            if not patient_result:
                return None
            
            record = {
                "patient": {
                    "name": patient_result["name"],
                    "age": patient_result["age"]
                },
                "diagnoses": [],
                "prescriptions": [],
                "vitals": [],
                "medical_history": []
            }
            
            # Get current diagnoses
            diagnoses_query = """
                MATCH (p:Person {name: $name})-[r:DIAGNOSED_WITH]->(d:Disease)
                RETURN d.name AS disease, r.doctor AS doctor, r.date AS date, 
                       r.notes AS notes, r.severity AS severity, r.status AS status
                ORDER BY r.date DESC
            """
            diagnoses_result = session.run(diagnoses_query, name=patient_name)
            for diag in diagnoses_result:
                record["diagnoses"].append(dict(diag))
            
            # Get prescriptions
            rx_query = """
                MATCH (p:Person {name: $name})-[:HAS_PRESCRIPTION]->(rx:Prescription)
                RETURN rx.medication AS medication, rx.dosage AS dosage, 
                       rx.frequency AS frequency, rx.doctor AS doctor,
                       rx.duration AS duration, rx.prescribed_date AS date,
                       rx.status AS status, rx.notes AS notes
                ORDER BY rx.prescribed_date DESC
            """
            rx_result = session.run(rx_query, name=patient_name)
            for rx in rx_result:
                record["prescriptions"].append(dict(rx))
            
            # Get vital signs (last 5 records)
            vitals_query = """
                MATCH (p:Person {name: $name})-[:HAS_VITALS]->(v:VitalSigns)
                RETURN v.blood_pressure AS blood_pressure, v.heart_rate AS heart_rate,
                       v.temperature AS temperature, v.weight AS weight,
                       v.height AS height, v.bmi AS bmi, v.recorded_at AS date
                ORDER BY v.recorded_at DESC
                LIMIT 5
            """
            vitals_result = session.run(vitals_query, name=patient_name)
            for vitals in vitals_result:
                record["vitals"].append(dict(vitals))
            
            # Get medical history
            history_query = """
                MATCH (p:Person {name: $name})-[:HAS_HISTORY]->(h:MedicalHistory)
                RETURN h.condition AS condition, h.date_diagnosed AS date_diagnosed,
                       h.resolved AS resolved, h.notes AS notes
                ORDER BY h.date_diagnosed DESC
            """
            history_result = session.run(history_query, name=patient_name)
            for hist in history_result:
                record["medical_history"].append(dict(hist))
            
            return record
    except Exception as e:
        print(f"Error fetching medical record: {str(e)}")
        return None

def search_by_diagnosis(disease_name):
    """Find all patients diagnosed with a specific disease."""
    try:
        with driver.session() as session:
            query = """
                MATCH (p:Person)-[r:DIAGNOSED_WITH]->(d:Disease {name: $disease_name})
                WHERE r.status = 'active'
                RETURN p.name AS patient_name, p.age AS age, 
                       r.doctor AS doctor, r.date AS diagnosed_date,
                       r.severity AS severity
                ORDER BY r.date DESC
            """
            result = session.run(query, disease_name=disease_name)
            return [dict(record) for record in result]
    except Exception as e:
        print(f"Error searching by diagnosis: {str(e)}")
        return []

def update_diagnosis_status(patient_name, disease_name, status, notes=""):
    """Update the status of a diagnosis (active, resolved, chronic)."""
    try:
        with driver.session() as session:
            query = """
                MATCH (p:Person {name: $patient_name})-[r:DIAGNOSED_WITH]->(d:Disease {name: $disease_name})
                SET r.status = $status, r.updated_at = $updated_at
                WITH r
                WHERE $notes <> ''
                SET r.resolution_notes = $notes
                RETURN r
            """
            
            result = session.run(query,
                               patient_name=patient_name,
                               disease_name=disease_name,
                               status=status,
                               notes=notes,
                               updated_at=datetime.now().isoformat())
            
            if result.single():
                return True, f"Diagnosis status updated to {status}"
            else:
                return False, "Diagnosis not found"
    except Exception as e:
        return False, f"Error updating diagnosis: {str(e)}"
