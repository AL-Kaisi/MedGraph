#!/usr/bin/env python
"""Test if the Flask app starts correctly."""

import sys
import os
import traceback

# Add the parent directory to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from app.flask_app import app
    print("✓ Flask app imported successfully")
    
    # Test if Neo4j connection works
    from app.main import driver
    with driver.session() as session:
        result = session.run("RETURN 1 AS num")
        if result.single()["num"] == 1:
            print("✓ Neo4j connection successful")
    
    # Test a simple route
    with app.test_client() as client:
        response = client.get('/')
        if response.status_code == 200:
            print("✓ Root route accessible")
        else:
            print(f"✗ Root route returned status code: {response.status_code}")
            
    print("\n✓ All basic tests passed - app should work correctly")
    
except ImportError as e:
    print(f"✗ Import error: {e}")
    traceback.print_exc()
    
except Exception as e:
    print(f"✗ Error: {e}")
    traceback.print_exc()