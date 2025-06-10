#!/usr/bin/env python3
"""
Test script for HRSN FHIR Bundle Processor Web Interface
"""

import requests
import json
import sys

def test_web_interface(base_url="http://localhost:8001"):
    """Test the web interface functionality"""
    print("🧪 Testing HRSN FHIR Bundle Processor Web Interface")
    print("=" * 60)
    
    # Test health endpoint
    print("\n1. Testing health endpoint...")
    try:
        response = requests.get(f"{base_url}/health")
        if response.status_code == 200:
            health_data = response.json()
            print(f"✓ Health check passed")
            print(f"  Service: {health_data['service']}")
            print(f"  Status: {health_data['status']}")
        else:
            print(f"✗ Health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"✗ Health check error: {e}")
        return False
    
    # Test web interface
    print("\n2. Testing web interface...")
    try:
        response = requests.get(f"{base_url}/")
        if response.status_code == 200 and "HRSN FHIR Bundle Processor" in response.text:
            print("✓ Web interface accessible")
        else:
            print(f"✗ Web interface failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"✗ Web interface error: {e}")
        return False
    
    # Test FHIR bundle processing
    print("\n3. Testing FHIR bundle processing...")
    
    # Load test bundle
    try:
        with open("hrsn_bundle_1.json", "r") as f:
            test_bundle = json.load(f)
        print(f"✓ Loaded test bundle: {test_bundle.get('id', 'unknown')}")
    except Exception as e:
        print(f"✗ Failed to load test bundle: {e}")
        return False
    
    # Process bundle
    try:
        response = requests.post(
            f"{base_url}/api/process-bundle",
            json=test_bundle,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            result = response.json()
            print("✓ Bundle processed successfully")
            
            # Display results summary
            print(f"\n📊 Processing Results:")
            print(f"  Bundle ID: {result['bundle_info']['id']}")
            print(f"  Bundle Type: {result['bundle_info']['type']}")
            print(f"  Total Resources: {result['bundle_info']['total']}")
            
            print(f"\n📋 Extracted Data:")
            print(f"  Patients: {len(result['patients'])}")
            print(f"  Screenings: {len(result['screenings'])}")
            print(f"  Responses: {len(result['responses'])}")
            print(f"  Organizations: {len(result['organizations'])}")
            
            # Show patient details
            if result['patients']:
                patient = result['patients'][0]
                print(f"\n👤 Sample Patient:")
                print(f"  Name: {patient['name']}")
                print(f"  Gender: {patient['gender']}")
                print(f"  Birth Date: {patient['birth_date']}")
                print(f"  Address: {patient['address']}")
            
            # Show organization details
            if result['organizations']:
                org = result['organizations'][0]
                print(f"\n🏥 Sample Organization:")
                print(f"  Name: {org['name']}")
                print(f"  Type: {org['type']}")
                print(f"  Address: {org['address']}")
            
            return True
            
        else:
            print(f"✗ Bundle processing failed: {response.status_code}")
            print(f"  Error: {response.text}")
            return False
            
    except Exception as e:
        print(f"✗ Bundle processing error: {e}")
        return False

def test_second_bundle(base_url="http://localhost:8001"):
    """Test with the second bundle"""
    print("\n4. Testing with second FHIR bundle...")
    
    try:
        with open("hrsn_bundle_2.json", "r") as f:
            test_bundle = json.load(f)
        print(f"✓ Loaded second test bundle: {test_bundle.get('id', 'unknown')}")
        
        response = requests.post(
            f"{base_url}/api/process-bundle",
            json=test_bundle,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            result = response.json()
            print("✓ Second bundle processed successfully")
            
            print(f"\n📊 Second Bundle Results:")
            print(f"  Bundle ID: {result['bundle_info']['id']}")
            print(f"  Patients: {len(result['patients'])}")
            print(f"  Organizations: {len(result['organizations'])}")
            
            return True
        else:
            print(f"✗ Second bundle processing failed: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"✗ Second bundle processing error: {e}")
        return False

def main():
    """Run all tests"""
    print("Starting comprehensive test of HRSN FHIR Bundle Processor...")
    
    tests_passed = 0
    total_tests = 4
    
    # Run tests
    if test_web_interface():
        tests_passed += 3  # Health, web interface, and first bundle
    
    if test_second_bundle():
        tests_passed += 1
    
    # Final results
    print("\n" + "=" * 60)
    print(f"🎯 Test Results: {tests_passed}/{total_tests} tests passed")
    
    if tests_passed == total_tests:
        print("🎉 All tests passed! Web interface is fully functional.")
        print(f"\n🌐 Access the web interface at: http://localhost:8001")
        print("📚 API documentation at: http://localhost:8001/docs")
        return 0
    else:
        print("❌ Some tests failed. Check the output above.")
        return 1

if __name__ == "__main__":
    exit(main())