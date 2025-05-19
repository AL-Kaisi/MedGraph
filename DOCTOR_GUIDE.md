# MedGraph Doctor's Portal Guide

## Overview

The MedGraph Doctor's Portal provides comprehensive tools for medical professionals to manage patient care, diagnoses, prescriptions, and medical records.

## Access Points

- **Hospital Interface**: http://localhost:8502/
- **Doctor's Portal**: http://localhost:8502/doctor
- **Simple Interface**: http://localhost:8502/simple

## Key Features for Doctors

### 1. Patient Consultation

The main interface for patient care, including:

#### a. Patient Search
- Real-time search by patient name
- Quick access to patient medical records
- Create new patient records

#### b. Vital Signs Recording
- Blood pressure
- Heart rate
- Temperature
- Weight & Height
- Automatic BMI calculation

#### c. Diagnosis Management
- Select from 100+ pre-loaded diseases
- Specify severity levels (mild, moderate, severe, critical)
- Add clinical notes
- Track diagnosis status (active, resolved, chronic)

#### d. Prescription Management
- Create prescriptions with:
  - Medication name
  - Dosage
  - Frequency (once daily, twice daily, etc.)
  - Duration
  - Special instructions

### 2. Medical Records

Complete patient medical history including:
- All diagnoses
- Prescription history
- Vital signs history
- Medical conditions timeline

### 3. Disease Tracker

- Search patients by disease
- View disease prevalence
- Track severity distribution
- Monitor disease patterns

### 4. Patient List

- View all patients
- Quick access to patient records
- Last visit tracking

## How to Assign a Patient to a Disease

### Method 1: During Consultation

1. Navigate to **Patient Consultation**
2. Search for the patient
3. In the **Diagnosis** section:
   - Select the disease from the dropdown
   - Choose severity level
   - Add clinical notes
   - Click "Add Diagnosis"

### Method 2: Quick Assignment

1. From the hospital interface
2. Select patient
3. Choose disease from dropdown
4. Click "Create Relationship"

## Clinical Workflow

### New Patient Visit

1. **Register Patient**
   - Go to Patient Consultation
   - Click "New Patient"
   - Enter name and age

2. **Record Vital Signs**
   - Enter BP, heart rate, temperature
   - Add weight and height
   - BMI calculates automatically

3. **Make Diagnosis**
   - Select disease from dropdown
   - Set severity level
   - Add clinical notes
   - Save diagnosis

4. **Create Prescription**
   - Enter medication details
   - Set dosage and frequency
   - Add duration and instructions
   - Save prescription

### Follow-up Visit

1. **Search Patient**
   - Type patient name in search
   - Select from results

2. **Review Medical History**
   - View current conditions
   - Check recent vitals
   - Review active medications

3. **Update Status**
   - Change diagnosis status if needed
   - Add new prescriptions
   - Record new vital signs

## Disease Management

### Available Disease Categories

- Infectious Diseases
- Cardiovascular
- Respiratory
- Endocrine
- Neurological
- Musculoskeletal
- Gastrointestinal
- Mental Health
- Cancer
- Renal

### Disease Information

Each disease includes:
- Name
- Description
- ICD-10 code

## Data Relationships

```
Patient → DIAGNOSED_WITH → Disease
  ↓
  → HAS_PRESCRIPTION → Prescription
  → HAS_VITALS → VitalSigns
  → HAS_HISTORY → MedicalHistory
```

## Best Practices

1. **Always record vital signs** during consultations
2. **Use appropriate severity levels** for diagnoses
3. **Add detailed clinical notes** for complex cases
4. **Update diagnosis status** when conditions resolve
5. **Review medical history** before new diagnoses
6. **Check for drug interactions** before prescribing

## API Endpoints for Advanced Users

- `POST /api/diagnosis` - Create diagnosis
- `POST /api/patients/{name}/vitals` - Record vitals
- `POST /api/patients/{name}/prescription` - Create prescription
- `GET /api/patients/{name}/medical-record` - Get full record
- `GET /api/diagnosis/search?disease={name}` - Find patients by disease
- `PUT /api/diagnosis/status` - Update diagnosis status

## Tips for Efficient Use

1. Use keyboard shortcuts to navigate between sections
2. Leverage the search function for quick patient access
3. Review the disease graph for visual understanding
4. Export data for reports and analysis
5. Use the disease tracker for epidemiological insights