#!/usr/bin/env python3
"""
Simple test script for HRSN FHIR Processing Server
"""

import requests
import json

def test_health(base_url="http://localhost:8001"):
    """Test server health endpoint"""
    print("Testing health endpoint...")
    response = requests.get(f"{base_url}/health")
    
    if response.status_code == 200:
        health_data = response.json()
        print(f"✓ Server is healthy")
        print(f"  Status: {health_data['status']}")
        print(f"  Version: {health_data['version']}")
        print(f"  Database: {health_data['database']}")
        return True
    else:
        print(f"✗ Health check failed: {response.status_code}")
        return False

def test_root(base_url="http://localhost:8001"):
    """Test root endpoint"""
    print("\nTesting root endpoint...")
    response = requests.get(f"{base_url}/")
    
    if response.status_code == 200:
        data = response.json()
        print(f"✓ Root endpoint working")
        print(f"  Message: {data['message']}")
        return True
    else:
        print(f"✗ Root endpoint failed: {response.status_code}")
        return False

def test_docs(base_url="http://localhost:8001"):
    """Test API docs endpoint"""
    print("\nTesting API docs...")
    response = requests.get(f"{base_url}/docs")
    
    if response.status_code == 200:
        print(f"✓ API docs available at {base_url}/docs")
        return True
    else:
        print(f"✗ API docs failed: {response.status_code}")
        return False

def main():
    """Run all tests"""
    print("HRSN FHIR Processing Server - Test Suite")
    print("=" * 50)
    
    tests = [
        test_health,
        test_root,
        test_docs
    ]
    
    passed = 0
    total = len(tests)
    
    for test_func in tests:
        try:
            if test_func():
                passed += 1
        except Exception as e:
            print(f"✗ Test {test_func.__name__} failed with error: {e}")
    
    print("\n" + "=" * 50)
    print(f"Test Results: {passed}/{total} passed")
    
    if passed == total:
        print("🎉 All tests passed! Server is working correctly.")
        return 0
    else:
        print("❌ Some tests failed. Check the output above.")
        return 1

if __name__ == "__main__":
    exit(main())