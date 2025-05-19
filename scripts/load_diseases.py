#!/usr/bin/env python
"""Script to load all diseases into Neo4j database."""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.main import create_disease
from data.diseases_data import DISEASE_CATEGORIES

def load_all_diseases():
    """Load all diseases from the disease data into Neo4j."""
    total_diseases = 0
    successful = 0
    failed = 0
    
    print("Loading diseases into Neo4j database...")
    print("=" * 50)
    
    for category, diseases in DISEASE_CATEGORIES.items():
        print(f"\nLoading {category} diseases...")
        
        for disease in diseases:
            total_diseases += 1
            disease_full_desc = f"{disease['description']} (ICD-10: {disease['icd10']})"
            
            success, message = create_disease(disease['name'], disease_full_desc)
            
            if success:
                successful += 1
                print(f"  ✓ {disease['name']}")
            else:
                failed += 1
                print(f"  ✗ {disease['name']}: {message}")
    
    print("\n" + "=" * 50)
    print(f"Disease loading complete!")
    print(f"Total: {total_diseases}")
    print(f"Successful: {successful}")
    print(f"Failed: {failed}")
    
    return successful, failed

if __name__ == "__main__":
    load_all_diseases()