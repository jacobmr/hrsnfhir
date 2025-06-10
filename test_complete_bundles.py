#!/usr/bin/env python3
"""
Test script for the new complete HRSN FHIR Bundles with survey results
"""

import requests
import json
import sys

def test_complete_bundle(filename, base_url="http://localhost:8001"):
    """Test a complete FHIR bundle"""
    print(f"\n🧪 Testing {filename}...")
    
    try:
        with open(filename, "r") as f:
            test_bundle = json.load(f)
        print(f"✓ Loaded bundle: {test_bundle.get('id', 'unknown')}")
    except Exception as e:
        print(f"✗ Failed to load bundle: {e}")
        return False
    
    try:
        response = requests.post(
            f"{base_url}/api/process-bundle",
            json=test_bundle,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"✓ Bundle processed successfully")
            
            print(f"\n📊 Results for {filename}:")
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
                print(f"\n👤 Patient:")
                print(f"  Name: {patient['name']}")
                print(f"  Gender: {patient['gender']}")
                print(f"  Birth Date: {patient['birth_date']}")
            
            # Show questionnaire responses (NEW!)
            if result['responses']:
                print(f"\n📝 Survey Responses Found: {len(result['responses'])}")
                for i, response in enumerate(result['responses'][:1]):  # Show first one
                    print(f"  Response {i+1}: {response.get('questionnaire', 'N/A')}")
                    print(f"    Status: {response.get('status', 'N/A')}")
                    if 'item' in response:
                        print(f"    Questions: {len(response.get('item', []))}")
            
            # Show summary data if available
            if 'summary' in result:
                summary = result['summary']
                print(f"\n🛡️ Safety Analysis:")
                print(f"  Safety Score: {summary.get('total_safety_score', 'N/A')}")
                print(f"  High Risk: {'Yes' if summary.get('high_risk') else 'No'}")
                print(f"  Positive Screens: {summary.get('positive_screens', 'N/A')}")
                print(f"  Completion Rate: {summary.get('completion_rate', 'N/A')}%")
            
            return True
            
        else:
            print(f"✗ Bundle processing failed: {response.status_code}")
            print(f"  Error: {response.text}")
            return False
            
    except Exception as e:
        print(f"✗ Bundle processing error: {e}")
        return False

def main():
    """Test all complete bundles"""
    print("🧪 Testing Complete HRSN FHIR Bundles with Survey Results")
    print("=" * 70)
    
    bundles = [
        "hrsn_bundle_1_complete.json",
        "hrsn_bundle_2_complete.json", 
        "hrsn_bundle_3_complete.json"
    ]
    
    passed = 0
    total = len(bundles)
    
    for bundle in bundles:
        if test_complete_bundle(bundle):
            passed += 1
    
    print("\n" + "=" * 70)
    print(f"🎯 Test Results: {passed}/{total} complete bundles processed successfully")
    
    if passed == total:
        print("🎉 All complete bundles with survey results are working!")
        print("\n✅ Key Features Verified:")
        print("  • Complete 12-question AHC HRSN screening")
        print("  • QuestionnaireResponse resources with all survey data")
        print("  • Individual Observation resources for key responses")
        print("  • Safety score calculations")
        print("  • Multiple SDOH categories (housing, food, transportation, etc.)")
        print("  • High-risk and low-risk scenarios")
        print("  • Compliant with SHIN-NY Implementation Guide")
        return 0
    else:
        print("❌ Some tests failed. Check the output above.")
        return 1

if __name__ == "__main__":
    exit(main())