// Doctor's Portal JavaScript

const API_BASE_URL = '';
let currentPatient = null;
let allDiseases = [];
let doctorName = 'Dr. Smith'; // In a real app, this would come from authentication

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

// Format date for display
function formatDate(dateString) {
    const date = new Date(dateString);
    return date.toLocaleDateString() + ' ' + date.toLocaleTimeString();
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
        if (section === 'patient-list') {
            loadPatientList();
        } else if (section === 'prescriptions') {
            loadPrescriptions();
        }
    });
});

// Patient Search
const searchInput = document.getElementById('patientSearch');
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

// Select patient for consultation
async function selectPatient(name) {
    try {
        const response = await fetch(`${API_BASE_URL}/api/patients/${name}/medical-record`);
        const record = await response.json();
        
        currentPatient = record.patient;
        displayPatientConsultation(record);
        searchResults.classList.remove('show');
        searchInput.value = '';
        document.getElementById('consultationPanel').style.display = 'block';
    } catch (error) {
        showAlert('Error loading patient record', 'danger');
    }
}

// Display patient consultation panel
function displayPatientConsultation(record) {
    // Patient info
    document.getElementById('patientName').textContent = record.patient.name;
    document.getElementById('patientAge').textContent = record.patient.age;
    document.getElementById('patientId').textContent = 'MR-' + Math.random().toString(36).substr(2, 9).toUpperCase();
    
    // Current conditions
    const conditionsHtml = record.diagnoses
        .filter(d => d.status === 'active')
        .map(d => `
            <div class="condition-item ${d.severity}">
                <strong>${d.disease}</strong>
                <small class="d-block">Severity: ${d.severity}</small>
                <small class="text-muted">Diagnosed: ${formatDate(d.date)}</small>
            </div>
        `).join('');
    
    document.getElementById('currentConditions').innerHTML = conditionsHtml || '<p class="text-muted">No active conditions</p>';
    
    // Recent vitals
    const vitalsHtml = record.vitals.map(v => `
        <div class="vital-stat">
            <div class="value">${v.blood_pressure}</div>
            <div class="label">BP</div>
        </div>
        <div class="vital-stat">
            <div class="value">${v.heart_rate}</div>
            <div class="label">Heart Rate</div>
        </div>
        <div class="vital-stat">
            <div class="value">${v.temperature}°C</div>
            <div class="label">Temp</div>
        </div>
    `).join('');
    
    document.getElementById('recentVitals').innerHTML = vitalsHtml || '<p class="text-muted">No recent vitals</p>';
    
    // Active medications
    const medicationsHtml = record.prescriptions
        .filter(p => p.status === 'active')
        .map(p => `
            <div class="medication-item">
                <strong>${p.medication}</strong>
                <small class="d-block">${p.dosage} - ${p.frequency}</small>
                <small class="text-muted">Prescribed: ${formatDate(p.date)}</small>
            </div>
        `).join('');
    
    document.getElementById('activeMedications').innerHTML = medicationsHtml || '<p class="text-muted">No active medications</p>';
}

// Vitals form handling
document.getElementById('vitalsForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    
    if (!currentPatient) return;
    
    const vitalsData = {
        blood_pressure: document.getElementById('bloodPressure').value,
        heart_rate: document.getElementById('heartRate').value,
        temperature: document.getElementById('temperature').value,
        weight: document.getElementById('weight').value,
        height: document.getElementById('height').value,
        notes: ''
    };
    
    try {
        const response = await fetch(`${API_BASE_URL}/api/patients/${currentPatient.name}/vitals`, {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify(vitalsData)
        });
        
        const result = await response.json();
        
        if (result.success) {
            showAlert('Vital signs recorded successfully', 'success');
            document.getElementById('vitalsForm').reset();
            selectPatient(currentPatient.name); // Refresh patient data
        } else {
            showAlert(result.message, 'danger');
        }
    } catch (error) {
        showAlert('Error recording vital signs', 'danger');
    }
});

// Calculate BMI
document.getElementById('weight').addEventListener('input', calculateBMI);
document.getElementById('height').addEventListener('input', calculateBMI);

function calculateBMI() {
    const weight = parseFloat(document.getElementById('weight').value);
    const height = parseFloat(document.getElementById('height').value);
    
    if (weight && height) {
        const heightM = height / 100;
        const bmi = (weight / (heightM * heightM)).toFixed(1);
        document.getElementById('bmi').value = bmi;
    } else {
        document.getElementById('bmi').value = '';
    }
}

// Diagnosis form handling
document.getElementById('diagnosisForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    
    if (!currentPatient) return;
    
    const diagnosisData = {
        patient_name: currentPatient.name,
        disease_name: document.getElementById('diseaseSelect').value,
        doctor_name: doctorName,
        severity: document.getElementById('severity').value,
        notes: document.getElementById('diagnosisNotes').value
    };
    
    try {
        const response = await fetch(`${API_BASE_URL}/api/diagnosis`, {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify(diagnosisData)
        });
        
        const result = await response.json();
        
        if (result.success) {
            showAlert('Diagnosis added successfully', 'success');
            document.getElementById('diagnosisForm').reset();
            selectPatient(currentPatient.name); // Refresh patient data
        } else {
            showAlert(result.message, 'danger');
        }
    } catch (error) {
        showAlert('Error adding diagnosis', 'danger');
    }
});

// Prescription form handling
document.getElementById('prescriptionForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    
    if (!currentPatient) return;
    
    const prescriptionData = {
        medication: document.getElementById('medication').value,
        dosage: document.getElementById('dosage').value,
        frequency: document.getElementById('frequency').value,
        doctor_name: doctorName,
        duration: document.getElementById('duration').value,
        notes: document.getElementById('instructions').value
    };
    
    try {
        const response = await fetch(`${API_BASE_URL}/api/patients/${currentPatient.name}/prescription`, {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify(prescriptionData)
        });
        
        const result = await response.json();
        
        if (result.success) {
            showAlert('Prescription added successfully', 'success');
            document.getElementById('prescriptionForm').reset();
            selectPatient(currentPatient.name); // Refresh patient data
        } else {
            showAlert(result.message, 'danger');
        }
    } catch (error) {
        showAlert('Error adding prescription', 'danger');
    }
});

// New patient modal
function showNewPatientForm() {
    const modal = new bootstrap.Modal(document.getElementById('newPatientModal'));
    modal.show();
}

async function registerNewPatient() {
    const name = document.getElementById('newPatientName').value;
    const age = document.getElementById('newPatientAge').value;
    
    if (!name || !age) return;
    
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
            bootstrap.Modal.getInstance(document.getElementById('newPatientModal')).hide();
            selectPatient(name); // Select the newly created patient
        } else {
            showAlert(result.message, 'danger');
        }
    } catch (error) {
        showAlert('Error registering patient', 'danger');
    }
}

// Disease tracker
async function searchByDisease() {
    const diseaseName = document.getElementById('diseaseTracker').value;
    
    if (!diseaseName) return;
    
    try {
        const response = await fetch(`${API_BASE_URL}/api/diagnosis/search?disease=${encodeURIComponent(diseaseName)}`);
        const patients = await response.json();
        
        const html = patients.map(p => `
            <div class="patient-card" onclick="selectPatient('${p.patient_name}')">
                <h6>${p.patient_name} (Age: ${p.age})</h6>
                <p class="mb-1">Severity: <span class="badge bg-${p.severity === 'severe' ? 'danger' : 'warning'}">${p.severity}</span></p>
                <p class="mb-0"><small>Diagnosed: ${formatDate(p.diagnosed_date)}</small></p>
                <p class="mb-0"><small>Doctor: ${p.doctor}</small></p>
            </div>
        `).join('');
        
        document.getElementById('diseasePatientsList').innerHTML = html || '<p class="text-muted">No patients found with this disease</p>';
        
        // Update stats
        document.getElementById('diseaseStats').innerHTML = `
            <p><strong>Total Patients:</strong> ${patients.length}</p>
            <p><strong>Severity Distribution:</strong></p>
            <div class="progress">
                <div class="progress-bar bg-success" style="width: ${patients.filter(p => p.severity === 'mild').length / patients.length * 100}%">Mild</div>
                <div class="progress-bar bg-warning" style="width: ${patients.filter(p => p.severity === 'moderate').length / patients.length * 100}%">Moderate</div>
                <div class="progress-bar bg-danger" style="width: ${patients.filter(p => p.severity === 'severe').length / patients.length * 100}%">Severe</div>
            </div>
        `;
    } catch (error) {
        showAlert('Error searching patients', 'danger');
    }
}

// Load patient list
async function loadPatientList() {
    try {
        const response = await fetch(`${API_BASE_URL}/api/persons`);
        const patients = await response.json();
        
        const tbody = document.getElementById('patientTableBody');
        tbody.innerHTML = patients.map(p => `
            <tr>
                <td>${p.name}</td>
                <td>${p.age}</td>
                <td>-</td>
                <td>-</td>
                <td>
                    <button class="btn btn-sm btn-primary" onclick="selectPatient('${p.name}'); showSection('patient-consultation')">
                        View
                    </button>
                </td>
            </tr>
        `).join('');
    } catch (error) {
        console.error('Error loading patient list:', error);
    }
}

// Show specific section
function showSection(section) {
    document.querySelectorAll('.sidebar .list-group-item').forEach(item => {
        if (item.dataset.section === section) {
            item.click();
        }
    });
}

// Load diseases for dropdowns
async function loadDiseases() {
    try {
        const response = await fetch(`${API_BASE_URL}/api/diseases`);
        allDiseases = await response.json();
        
        // Populate disease selects
        const diseaseSelect = document.getElementById('diseaseSelect');
        const diseaseTracker = document.getElementById('diseaseTracker');
        
        allDiseases.forEach(disease => {
            const option1 = new Option(disease.name, disease.name);
            const option2 = new Option(disease.name, disease.name);
            diseaseSelect.add(option1);
            diseaseTracker.add(option2);
        });
    } catch (error) {
        console.error('Error loading diseases:', error);
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