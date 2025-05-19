// Hospital System JavaScript

const API_BASE_URL = '';
let currentPatient = null;
let allDiseases = [];

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

// Navigation handling
document.querySelectorAll('.sidebar .list-group-item').forEach(item => {
    item.addEventListener('click', (e) => {
        e.preventDefault();
        
        // Update active state
        document.querySelectorAll('.sidebar .list-group-item').forEach(i => i.classList.remove('active'));
        item.classList.add('active');
        
        // Show corresponding section
        const section = item.dataset.section;
        document.querySelectorAll('.content-section').forEach(s => s.style.display = 'none');
        document.getElementById(section).style.display = 'block';
        
        // Load section-specific data
        if (section === 'statistics') {
            loadStatistics();
        }
    });
});

// Patient Search
const searchInput = document.getElementById('patientSearchInput');
const searchResults = document.getElementById('searchResults');
let searchTimeout;

searchInput.addEventListener('input', (e) => {
    clearTimeout(searchTimeout);
    const query = e.target.value.trim();
    
    if (query.length < 2) {
        searchResults.classList.remove('show');
        return;
    }
    
    searchTimeout = setTimeout(async () => {
        try {
            const response = await fetch(`${API_BASE_URL}/api/persons/search?q=${encodeURIComponent(query)}`);
            const patients = await response.json();
            
            searchResults.innerHTML = '';
            if (patients.length > 0) {
                patients.forEach(patient => {
                    const item = document.createElement('div');
                    item.className = 'search-result-item';
                    item.innerHTML = `<strong>${patient.name}</strong> (Age: ${patient.age})`;
                    item.addEventListener('click', () => selectPatient(patient.name));
                    searchResults.appendChild(item);
                });
                searchResults.classList.add('show');
            } else {
                searchResults.innerHTML = '<div class="search-result-item">No patients found</div>';
                searchResults.classList.add('show');
            }
        } catch (error) {
            console.error('Search error:', error);
        }
    }, 300);
});

// Select patient
async function selectPatient(name) {
    try {
        const response = await fetch(`${API_BASE_URL}/api/persons/${name}/details`);
        const patient = await response.json();
        
        currentPatient = patient;
        displayPatientDetails(patient);
        searchResults.classList.remove('show');
        searchInput.value = '';
    } catch (error) {
        showAlert('Error loading patient details', 'danger');
    }
}

// Display patient details
function displayPatientDetails(patient) {
    document.getElementById('patientDetails').style.display = 'block';
    document.getElementById('detailName').textContent = patient.name;
    document.getElementById('detailAge').textContent = patient.age;
    
    // Display diseases
    const diseaseList = document.getElementById('diseaseList');
    diseaseList.innerHTML = '';
    
    if (patient.diseases.length > 0) {
        patient.diseases.forEach(disease => {
            const item = document.createElement('div');
            item.className = 'disease-item';
            item.innerHTML = `
                <div>
                    <strong>${disease.name}</strong>
                    <small class="text-muted d-block">${disease.description}</small>
                </div>
                <button class="btn btn-danger btn-sm" onclick="removeDisease('${disease.name}')">
                    <i class="bi bi-trash"></i>
                </button>
            `;
            diseaseList.appendChild(item);
        });
    } else {
        diseaseList.innerHTML = '<p class="text-muted">No medical conditions recorded</p>';
    }
    
    // Load disease graph
    loadPatientGraph(patient.name);
}

// Load patient graph
async function loadPatientGraph(patientName) {
    try {
        const response = await fetch(`${API_BASE_URL}/api/graph/${patientName}`);
        const graphData = await response.json();
        
        const container = document.getElementById('patientGraph');
        const options = {
            nodes: {
                shape: 'dot',
                size: 25,
                font: {
                    size: 16,
                    color: '#333'
                },
                borderWidth: 2
            },
            edges: {
                width: 2,
                arrows: {
                    to: {enabled: true, scaleFactor: 0.8}
                },
                color: {
                    color: '#848484',
                    highlight: '#0d6efd'
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
                tooltipDelay: 200,
                navigationButtons: true,
                keyboard: true
            }
        };
        
        new vis.Network(container, graphData, options);
    } catch (error) {
        console.error('Error loading graph:', error);
    }
}

// Add disease to patient
document.getElementById('addDiseaseBtn').addEventListener('click', async () => {
    const diseaseSelect = document.getElementById('diseaseSelect');
    const diseaseName = diseaseSelect.value;
    
    if (!currentPatient || !diseaseName) return;
    
    try {
        const response = await fetch(`${API_BASE_URL}/api/relationships`, {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({
                person_name: currentPatient.name,
                disease_name: diseaseName
            })
        });
        
        const result = await response.json();
        
        if (result.success) {
            showAlert('Disease added successfully', 'success');
            selectPatient(currentPatient.name); // Reload patient details
        } else {
            showAlert(result.message, 'danger');
        }
    } catch (error) {
        showAlert('Error adding disease', 'danger');
    }
});

// Remove disease from patient
async function removeDisease(diseaseName) {
    if (!currentPatient || !confirm('Remove this condition?')) return;
    
    try {
        const response = await fetch(`${API_BASE_URL}/api/relationships`, {
            method: 'DELETE',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({
                person_name: currentPatient.name,
                disease_name: diseaseName
            })
        });
        
        const result = await response.json();
        
        if (result.success) {
            showAlert('Disease removed successfully', 'success');
            selectPatient(currentPatient.name); // Reload patient details
        } else {
            showAlert(result.message, 'danger');
        }
    } catch (error) {
        showAlert('Error removing disease', 'danger');
    }
}

// New patient form
document.getElementById('newPatientForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const name = document.getElementById('newPatientName').value;
    const age = document.getElementById('newPatientAge').value;
    
    try {
        const response = await fetch(`${API_BASE_URL}/api/persons`, {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({name, age})
        });
        
        const result = await response.json();
        
        if (result.success) {
            showAlert('Patient registered successfully', 'success');
            document.getElementById('newPatientForm').reset();
        } else {
            showAlert(result.message, 'danger');
        }
    } catch (error) {
        showAlert('Error registering patient', 'danger');
    }
});

// Load diseases for select dropdown
async function loadDiseases() {
    try {
        const response = await fetch(`${API_BASE_URL}/api/diseases`);
        allDiseases = await response.json();
        
        const diseaseSelect = document.getElementById('diseaseSelect');
        diseaseSelect.innerHTML = '<option value="">Select a disease...</option>';
        
        allDiseases.forEach(disease => {
            const option = new Option(disease.name, disease.name);
            diseaseSelect.add(option);
        });
    } catch (error) {
        console.error('Error loading diseases:', error);
    }
}

// Disease browser
document.querySelectorAll('#diseaseCategories .list-group-item').forEach(item => {
    item.addEventListener('click', (e) => {
        e.preventDefault();
        
        // Update active state
        document.querySelectorAll('#diseaseCategories .list-group-item').forEach(i => i.classList.remove('active'));
        item.classList.add('active');
        
        const category = item.dataset.category;
        filterDiseases(category);
    });
});

function filterDiseases(category) {
    const tbody = document.getElementById('diseaseTableBody');
    tbody.innerHTML = '';
    
    let filteredDiseases = allDiseases;
    
    allDiseases.forEach(disease => {
        const row = tbody.insertRow();
        row.innerHTML = `
            <td>${disease.name}</td>
            <td>${disease.description}</td>
            <td>${extractICD10(disease.description)}</td>
        `;
    });
}

function extractICD10(description) {
    const match = description.match(/\(ICD-10: ([A-Z]\d{2}\.?\d*)\)/);
    return match ? match[1] : 'N/A';
}

// Load statistics
async function loadStatistics() {
    try {
        // Fetch all data
        const [personsResponse, diseasesResponse] = await Promise.all([
            fetch(`${API_BASE_URL}/api/persons`),
            fetch(`${API_BASE_URL}/api/diseases`)
        ]);
        
        const persons = await personsResponse.json();
        const diseases = await diseasesResponse.json();
        
        // Update statistics
        document.getElementById('totalPatients').textContent = persons.length;
        document.getElementById('totalDiseases').textContent = diseases.length;
        
        // Calculate more statistics (this would need additional API endpoints in a real app)
        // For now, we'll show placeholder data
        document.getElementById('totalRelationships').textContent = '0';
        document.getElementById('avgConditions').textContent = '0.0';
        
    } catch (error) {
        console.error('Error loading statistics:', error);
    }
}

// Initialize the application
document.addEventListener('DOMContentLoaded', () => {
    loadDiseases();
    
    // Click outside to close search results
    document.addEventListener('click', (e) => {
        if (!searchInput.contains(e.target) && !searchResults.contains(e.target)) {
            searchResults.classList.remove('show');
        }
    });
});