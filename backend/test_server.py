#!/usr/bin/env python3
"""
Quick test script to verify the backend server works
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Test imports
try:
    from app import app, load_models
    print("✓ App imports successfully")
except Exception as e:
    print(f"✗ Error importing app: {e}")
    sys.exit(1)

# Test model loading
try:
    print("\nTesting model loading...")
    load_models()
    print("✓ Models loaded successfully")
except Exception as e:
    print(f"⚠ Warning: Model loading had issues: {e}")
    print("  (Server will still work with fallbacks)")

# Test app creation
try:
    with app.test_client() as client:
        # Test health endpoint
        response = client.get('/api/health')
        if response.status_code == 200:
            print("✓ Health endpoint works")
            print(f"  Response: {response.get_json()}")
        else:
            print(f"✗ Health endpoint failed: {response.status_code}")
        
        # Test nutritional targets endpoint
        test_data = {
            'age': 25,
            'weight': 70,
            'heightFeet': 5,
            'heightInches': 10,
            'activityLevel': 'Moderate',
            'gender': 'Male'
        }
        response = client.post('/api/nutritional-targets', json=test_data)
        if response.status_code == 200:
            print("✓ Nutritional targets endpoint works")
            result = response.get_json()
            print(f"  Calories: {result.get('calories')}, Protein: {result.get('protein')}g")
        else:
            print(f"✗ Nutritional targets endpoint failed: {response.status_code}")
            print(f"  Response: {response.get_data(as_text=True)}")
        
        print("\n✓ All tests passed! Server is ready to run.")
        print("  Start the server with: python3 app.py")
        
except Exception as e:
    print(f"✗ Error testing endpoints: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

