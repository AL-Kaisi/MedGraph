// MedGraph JavaScript Application

const API_BASE_URL = '';

// Utility function to show alerts
function showAlert(message, type = 'success') {
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type} alert-dismissible fade show`;
    alertDiv.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    document.body.appendChild(alertDiv);
    
    setTimeout(() => {
        alertDiv.remove();
    }, 5000);
}

// Fetch all persons
async function fetchPersons() {
    try {
        const response = await fetch(`${API_BASE_URL}/api/persons`);
        const persons = await response.json();
        return persons;
    } catch (error) {
        console.error('Error fetching persons:', error);
        return [];
    }
}

// Fetch all diseases
async function fetchDiseases() {
    try {
        const response = await fetch(`${API_BASE_URL}/api/diseases`);
        const diseases = await response.json();
        return diseases;
    } catch (error) {
        console.error('Error fetching diseases:', error);
        return [];
    }
}

// Update select dropdowns
async function updateSelects() {
    const persons = await fetchPersons();
    const diseases = await fetchDiseases();
    
    // Update person selects
    const personSelects = ['relationPerson', 'graphPerson'];
    personSelects.forEach(selectId => {
        const select = document.getElementById(selectId);
        select.innerHTML = '<option value="">Select a patient...</option>';
        persons.forEach(person => {
            const option = new Option(person.name, person.name);
            select.add(option);
        });
    });
    
    // Update disease select
    const diseaseSelect = document.getElementById('relationDisease');
    diseaseSelect.innerHTML = '<option value="">Select a disease...</option>';
    diseases.forEach(disease => {
        const option = new Option(disease.name, disease.name);
        diseaseSelect.add(option);
    });
}

// Create person
document.getElementById('createPersonForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const name = document.getElementById('personName').value;
    const age = document.getElementById('personAge').value;
    
    try {
        const response = await fetch(`${API_BASE_URL}/api/persons`, {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({name, age})
        });
        
        const result = await response.json();
        
        if (result.success) {
            showAlert(result.message, 'success');
            document.getElementById('createPersonForm').reset();
            updateSelects();
        } else {
            showAlert(result.message, 'danger');
        }
    } catch (error) {
        showAlert('Error creating patient', 'danger');
    }
});

// Create disease
document.getElementById('createDiseaseForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const name = document.getElementById('diseaseName').value;
    const description = document.getElementById('diseaseDescription').value;
    
    try {
        const response = await fetch(`${API_BASE_URL}/api/diseases`, {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({name, description})
        });
        
        const result = await response.json();
        
        if (result.success) {
            showAlert(result.message, 'success');
            document.getElementById('createDiseaseForm').reset();
            updateSelects();
        } else {
            showAlert(result.message, 'danger');
        }
    } catch (error) {
        showAlert('Error creating disease', 'danger');
    }
});

// Create relationship
document.getElementById('createRelationshipForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const person_name = document.getElementById('relationPerson').value;
    const disease_name = document.getElementById('relationDisease').value;
    
    try {
        const response = await fetch(`${API_BASE_URL}/api/relationships`, {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({person_name, disease_name})
        });
        
        const result = await response.json();
        
        if (result.success) {
            showAlert(result.message, 'success');
            document.getElementById('createRelationshipForm').reset();
            loadGraph();
        } else {
            showAlert(result.message, 'danger');
        }
    } catch (error) {
        showAlert('Error creating relationship', 'danger');
    }
});

// Load graph
let network = null;

async function loadGraph() {
    const personName = document.getElementById('graphPerson').value;
    
    if (!personName) {
        // Clear the graph
        if (network) {
            network.destroy();
            network = null;
        }
        document.getElementById('diseasesTableBody').innerHTML = 
            '<tr><td colspan="3" class="text-center">Select a patient to view diseases</td></tr>';
        return;
    }
    
    try {
        // Fetch graph data
        const response = await fetch(`${API_BASE_URL}/api/graph/${personName}`);
        const graphData = await response.json();
        
        // Fetch diseases for table
        const diseasesResponse = await fetch(`${API_BASE_URL}/api/persons/${personName}/diseases`);
        const diseases = await diseasesResponse.json();
        
        // Update diseases table
        const tableBody = document.getElementById('diseasesTableBody');
        if (diseases.length === 0) {
            tableBody.innerHTML = `<tr><td colspan="3" class="text-center">No diseases found for ${personName}</td></tr>`;
        } else {
            tableBody.innerHTML = diseases.map(disease => `
                <tr>
                    <td>${personName}</td>
                    <td>${disease['d.name']}</td>
                    <td>${disease['d.description']}</td>
                </tr>
            `).join('');
        }
        
        // Create network visualization
        const container = document.getElementById('networkGraph');
        const options = {
            nodes: {
                shape: 'dot',
                size: 20,
                font: {
                    size: 14
                },
                borderWidth: 2
            },
            edges: {
                width: 2,
                arrows: {
                    to: {enabled: true, scaleFactor: 0.5}
                }
            },
            physics: {
                enabled: true,
                barnesHut: {
                    gravitationalConstant: -8000,
                    springConstant: 0.001,
                    springLength: 200
                }
            },
            interaction: {
                hover: true,
                tooltipDelay: 200
            }
        };
        
        // Create or update network
        if (network) {
            network.setData(graphData);
        } else {
            network = new vis.Network(container, graphData, options);
        }
        
    } catch (error) {
        console.error('Error loading graph:', error);
        showAlert('Error loading graph', 'danger');
    }
}

// Event listeners
document.getElementById('graphPerson').addEventListener('change', loadGraph);
document.getElementById('refreshGraph').addEventListener('click', loadGraph);

// Initialize the application
document.addEventListener('DOMContentLoaded', () => {
    updateSelects();
});
