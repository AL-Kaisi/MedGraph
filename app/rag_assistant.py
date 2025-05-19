#!/usr/bin/env python
"""RAG-based medical assistant for MedGraph."""

import os
from typing import List, Dict
import openai
from neo4j import GraphDatabase
from app.main import driver
import json

# Configure OpenAI (you'll need to set your API key)
openai.api_key = os.getenv("OPENAI_API_KEY", "")

class MedicalRAGAssistant:
    def __init__(self):
        self.driver = driver
        self.context_limit = 3000  # Characters to stay within token limits
        
    def get_relevant_medical_context(self, query: str) -> str:
        """Retrieve relevant medical context from Neo4j based on the query."""
        try:
            with self.driver.session() as session:
                # Extract potential disease names from query
                diseases_query = """
                    MATCH (d:Disease)
                    WHERE toLower(d.name) CONTAINS toLower($query)
                       OR toLower(d.description) CONTAINS toLower($query)
                    RETURN d.name AS name, d.description AS description
                    LIMIT 5
                """
                
                # Get patient information if mentioned
                patients_query = """
                    MATCH (p:Person)-[r:DIAGNOSED_WITH]->(d:Disease)
                    WHERE toLower(p.name) CONTAINS toLower($query)
                    RETURN p.name AS patient, p.age AS age, 
                           collect({disease: d.name, severity: r.severity}) AS conditions
                    LIMIT 3
                """
                
                # Get treatment patterns
                treatment_query = """
                    MATCH (p:Person)-[r:DIAGNOSED_WITH]->(d:Disease)
                    WHERE toLower(d.name) CONTAINS toLower($query)
                    MATCH (p)-[:HAS_PRESCRIPTION]->(rx:Prescription)
                    RETURN d.name AS disease, 
                           collect(DISTINCT rx.medication) AS medications
                    LIMIT 5
                """
                
                context_parts = []
                
                # Execute queries
                diseases_result = session.run(diseases_query, query=query)
                for record in diseases_result:
                    context_parts.append(
                        f"Disease: {record['name']}\n"
                        f"Description: {record['description']}\n"
                    )
                
                patients_result = session.run(patients_query, query=query)
                for record in patients_result:
                    conditions = ", ".join([f"{c['disease']} ({c['severity']})" 
                                          for c in record['conditions']])
                    context_parts.append(
                        f"Patient: {record['patient']}, Age: {record['age']}\n"
                        f"Conditions: {conditions}\n"
                    )
                
                treatment_result = session.run(treatment_query, query=query)
                for record in treatment_result:
                    medications = ", ".join(record['medications'])
                    context_parts.append(
                        f"Disease: {record['disease']}\n"
                        f"Common Medications: {medications}\n"
                    )
                
                return "\n".join(context_parts)[:self.context_limit]
        except Exception as e:
            print(f"Error getting medical context: {str(e)}")
            return ""
    
    def get_diagnostic_suggestions(self, symptoms: List[str]) -> Dict:
        """Get AI-powered diagnostic suggestions based on symptoms."""
        try:
            # Get disease patterns from database
            with self.driver.session() as session:
                diseases_query = """
                    MATCH (d:Disease)
                    RETURN d.name AS name, d.description AS description
                """
                result = session.run(diseases_query)
                diseases = [dict(record) for record in result]
            
            # Create context with disease information
            context = "Available diseases in system:\n"
            for disease in diseases[:20]:  # Limit to avoid token limits
                context += f"- {disease['name']}: {disease['description']}\n"
            
            # Construct prompt
            symptoms_text = ", ".join(symptoms)
            prompt = f"""
            Based on the following symptoms: {symptoms_text}
            
            And the available diseases in our system:
            {context}
            
            Please suggest:
            1. The most likely diagnoses (from the available diseases)
            2. Recommended severity level for each diagnosis
            3. Additional symptoms to check
            4. Recommended tests or examinations
            
            Format the response as JSON.
            """
            
            response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are a medical assistant AI. Provide helpful diagnostic suggestions based on symptoms."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=500
            )
            
            # Parse response
            content = response.choices[0].message.content
            try:
                return json.loads(content)
            except:
                return {"suggestions": content}
                
        except Exception as e:
            print(f"Error getting diagnostic suggestions: {str(e)}")
            return {"error": str(e)}
    
    def get_treatment_recommendations(self, disease_name: str, patient_info: Dict) -> Dict:
        """Get AI-powered treatment recommendations."""
        try:
            # Get current treatment patterns from database
            with self.driver.session() as session:
                treatment_query = """
                    MATCH (p:Person)-[r:DIAGNOSED_WITH]->(d:Disease {name: $disease})
                    MATCH (p)-[:HAS_PRESCRIPTION]->(rx:Prescription)
                    RETURN rx.medication AS medication, rx.dosage AS dosage, 
                           rx.frequency AS frequency, count(*) AS usage_count
                    ORDER BY usage_count DESC
                    LIMIT 10
                """
                result = session.run(treatment_query, disease=disease_name)
                common_treatments = [dict(record) for record in result]
            
            # Construct context
            context = f"Common treatments for {disease_name}:\n"
            for treatment in common_treatments:
                context += f"- {treatment['medication']} ({treatment['dosage']}, {treatment['frequency']}) - Used {treatment['usage_count']} times\n"
            
            prompt = f"""
            Patient Information:
            - Name: {patient_info.get('name', 'Unknown')}
            - Age: {patient_info.get('age', 'Unknown')}
            - Current Conditions: {', '.join(patient_info.get('conditions', []))}
            
            Disease: {disease_name}
            
            {context}
            
            Please recommend:
            1. Appropriate medications with dosage
            2. Treatment duration
            3. Special precautions
            4. Follow-up recommendations
            
            Format the response as JSON.
            """
            
            response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are a medical AI assistant. Provide treatment recommendations based on patient information and common practices."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=500
            )
            
            content = response.choices[0].message.content
            try:
                return json.loads(content)
            except:
                return {"recommendations": content}
                
        except Exception as e:
            print(f"Error getting treatment recommendations: {str(e)}")
            return {"error": str(e)}
    
    def answer_medical_question(self, question: str) -> str:
        """Answer medical questions using RAG."""
        try:
            # Get relevant context from database
            context = self.get_relevant_medical_context(question)
            
            prompt = f"""
            Context from medical database:
            {context}
            
            Question: {question}
            
            Please provide a comprehensive answer based on the context provided.
            If the context doesn't contain relevant information, provide general medical guidance.
            """
            
            response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are a medical AI assistant. Answer questions based on the provided context from a medical database."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=400
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            print(f"Error answering medical question: {str(e)}")
            return f"I apologize, but I'm unable to answer that question at the moment. Error: {str(e)}"
    
    def generate_clinical_notes(self, consultation_data: Dict) -> str:
        """Generate professional clinical notes from consultation data."""
        try:
            prompt = f"""
            Generate professional clinical notes based on the following consultation data:
            
            Patient: {consultation_data.get('patient_name', 'Unknown')}
            Age: {consultation_data.get('age', 'Unknown')}
            
            Chief Complaint: {consultation_data.get('chief_complaint', 'Not specified')}
            
            Vital Signs:
            {json.dumps(consultation_data.get('vitals', {}), indent=2)}
            
            Diagnosis: {consultation_data.get('diagnosis', 'Not specified')}
            Severity: {consultation_data.get('severity', 'Not specified')}
            
            Prescription:
            {json.dumps(consultation_data.get('prescription', {}), indent=2)}
            
            Doctor's Notes: {consultation_data.get('notes', '')}
            
            Please generate professional clinical notes in SOAP format.
            """
            
            response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are a medical documentation AI. Generate professional clinical notes in SOAP format."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=600
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            print(f"Error generating clinical notes: {str(e)}")
            return f"Error generating notes: {str(e)}"

# Singleton instance
rag_assistant = MedicalRAGAssistant()
