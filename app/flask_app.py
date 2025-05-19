#!/usr/bin/env python
"""Flask backend for MedGraph application."""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import json
from app.main import (create_person, create_disease, create_relationship,
                     fetch_person_diseases, GraphVisualizer, get_all_persons,
                     get_all_diseases, search_patients, get_patient_details,
                     delete_relationship)
from app.medical_features import (create_diagnosis, add_medical_history,
                                add_prescription, add_vitals,
                                get_patient_medical_record,
                                search_by_diagnosis,
                                update_diagnosis_status)

app = Flask(__name__, static_folder='../frontend/static', template_folder='../frontend')
CORS(app)

@app.route('/')
def index():
    return render_template('hospital.html')

@app.route('/simple')
def simple_interface():
    return render_template('index.html')

@app.route('/doctor')
def doctor_portal():
    return render_template('doctor.html')

@app.route('/api/persons', methods=['GET', 'POST'])
def handle_persons():
    if request.method == 'GET':
        persons = get_all_persons()
        return jsonify(persons)
    
    elif request.method == 'POST':
        data = request.json
        name = data.get('name')
        age = data.get('age')
        
        if not name or not age:
            return jsonify({'success': False, 'message': 'Name and age are required'}), 400
        
        success, message = create_person(name, int(age))
        return jsonify({'success': success, 'message': message})

@app.route('/api/diseases', methods=['GET', 'POST'])
def handle_diseases():
    if request.method == 'GET':
        diseases = get_all_diseases()
        return jsonify(diseases)
    
    elif request.method == 'POST':
        data = request.json
        name = data.get('name')
        description = data.get('description')
        
        if not name or not description:
            return jsonify({'success': False, 'message': 'Name and description are required'}), 400
        
        success, message = create_disease(name, description)
        return jsonify({'success': success, 'message': message})

@app.route('/api/relationships', methods=['POST'])
def create_relationship_endpoint():
    data = request.json
    person_name = data.get('person_name')
    disease_name = data.get('disease_name')
    
    if not person_name or not disease_name:
        return jsonify({'success': False, 'message': 'Person name and disease name are required'}), 400
    
    success, message = create_relationship(person_name, disease_name)
    return jsonify({'success': success, 'message': message})

@app.route('/api/persons/<name>/diseases', methods=['GET'])
def get_person_diseases(name):
    diseases = fetch_person_diseases(name)
    return jsonify(diseases)

@app.route('/api/persons/search', methods=['GET'])
def search_patients_endpoint():
    search_term = request.args.get('q', '')
    if len(search_term) < 2:
        return jsonify([])

    patients = search_patients(search_term)
    return jsonify(patients)

@app.route('/api/persons/<name>/details', methods=['GET'])
def get_patient_details_endpoint(name):
    details = get_patient_details(name)
    if details is None:
        return jsonify({'error': 'Patient not found'}), 404
    return jsonify(details)

@app.route('/api/relationships', methods=['DELETE'])
def delete_relationship_endpoint():
    data = request.json
    person_name = data.get('person_name')
    disease_name = data.get('disease_name')

    if not person_name or not disease_name:
        return jsonify({'success': False, 'message': 'Person name and disease name are required'}), 400

    success, message = delete_relationship(person_name, disease_name)
    return jsonify({'success': success, 'message': message})

@app.route('/api/diagnosis', methods=['POST'])
def create_diagnosis_endpoint():
    data = request.json
    patient_name = data.get('patient_name')
    disease_name = data.get('disease_name')
    doctor_name = data.get('doctor_name')
    notes = data.get('notes', '')
    severity = data.get('severity', 'moderate')

    if not all([patient_name, disease_name, doctor_name]):
        return jsonify({'success': False, 'message': 'Patient name, disease name, and doctor name are required'}), 400

    success, message = create_diagnosis(patient_name, disease_name, doctor_name, notes, severity)
    return jsonify({'success': success, 'message': message})

@app.route('/api/patients/<name>/vitals', methods=['POST'])
def add_vitals_endpoint(name):
    data = request.json

    success, message = add_vitals(
        name,
        data.get('blood_pressure'),
        data.get('heart_rate'),
        data.get('temperature'),
        data.get('weight'),
        data.get('height'),
        data.get('notes', '')
    )

    return jsonify({'success': success, 'message': message})

@app.route('/api/patients/<name>/prescription', methods=['POST'])
def add_prescription_endpoint(name):
    data = request.json

    success, message = add_prescription(
        name,
        data.get('medication'),
        data.get('dosage'),
        data.get('frequency'),
        data.get('doctor_name'),
        data.get('duration', ''),
        data.get('notes', '')
    )

    return jsonify({'success': success, 'message': message})

@app.route('/api/patients/<name>/medical-record', methods=['GET'])
def get_medical_record_endpoint(name):
    record = get_patient_medical_record(name)
    if record is None:
        return jsonify({'error': 'Patient not found'}), 404
    return jsonify(record)

@app.route('/api/diagnosis/search', methods=['GET'])
def search_by_diagnosis_endpoint():
    disease_name = request.args.get('disease')
    if not disease_name:
        return jsonify([])

    patients = search_by_diagnosis(disease_name)
    return jsonify(patients)

@app.route('/api/diagnosis/status', methods=['PUT'])
def update_diagnosis_status_endpoint():
    data = request.json
    patient_name = data.get('patient_name')
    disease_name = data.get('disease_name')
    status = data.get('status')
    notes = data.get('notes', '')

    if not all([patient_name, disease_name, status]):
        return jsonify({'success': False, 'message': 'Missing required fields'}), 400

    success, message = update_diagnosis_status(patient_name, disease_name, status, notes)
    return jsonify({'success': success, 'message': message})

@app.route('/api/graph/<name>', methods=['GET'])
def get_graph_data(name):
    graph_visualizer = GraphVisualizer(name)
    graph_visualizer.fetch_data()
    graph_visualizer.build_graph()

    # Convert networkx graph to JSON format for vis.js
    nodes = []
    edges = []

    for node, data in graph_visualizer.graph.nodes(data=True):
        node_data = {
            'id': node,
            'label': node
        }
        if 'color' in data:
            node_data['color'] = data['color']
        if 'title' in data:
            node_data['title'] = data['title']
        nodes.append(node_data)

    for source, target in graph_visualizer.graph.edges():
        edges.append({
            'from': source,
            'to': target
        })

    return jsonify({
        'nodes': nodes,
        'edges': edges
    })

if __name__ == '__main__':
    app.run(debug=os.getenv('DEBUG', 'False') == 'True',
            host=os.getenv('APP_HOST', '0.0.0.0'),
            port=int(os.getenv('APP_PORT', '8502')))
