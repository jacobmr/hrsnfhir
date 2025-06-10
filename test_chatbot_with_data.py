#!/usr/bin/env python3
"""
Test chatbot after loading data through the web API
"""

import requests
import json

def load_test_data(base_url="http://localhost:8001"):
    """Load test bundles through the API to populate chatbot database"""
    print("📁 Loading test data into chatbot database...")
    
    bundles = [
        "hrsn_bundle_1_complete.json",
        "hrsn_bundle_2_complete.json", 
        "hrsn_bundle_3_complete.json"
    ]
    
    loaded_count = 0
    
    for bundle_file in bundles:
        try:
            with open(bundle_file, "r") as f:
                bundle_data = json.load(f)
            
            response = requests.post(
                f"{base_url}/api/process-bundle",
                json=bundle_data,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                result = response.json()
                print(f"✓ Loaded {bundle_file}: {len(result['patients'])} patients")
                loaded_count += 1
            else:
                print(f"✗ Failed to load {bundle_file}: {response.status_code}")
                
        except Exception as e:
            print(f"✗ Error loading {bundle_file}: {e}")
    
    print(f"📊 Successfully loaded {loaded_count}/{len(bundles)} bundles")
    return loaded_count == len(bundles)

def test_chatbot_query(question, base_url="http://localhost:8001"):
    """Test a chatbot query"""
    print(f"\n🤖 Question: {question}")
    print("-" * 60)
    
    try:
        response = requests.post(
            f"{base_url}/api/chatbot",
            json={"question": question},
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"✓ Answer: {result['answer']}")
            
            if result.get('data'):
                print(f"\n📋 Patient Data ({len(result['data'])} patients):")
                for patient in result['data']:
                    print(f"  • {patient.get('name', 'Unknown')} (ID: {patient.get('patient_id', 'N/A')})")
                    if patient.get('safety_score'):
                        print(f"    Safety Score: {patient['safety_score']}")
            
            if result.get('summary'):
                summary = result['summary']
                print(f"\n📊 Summary:")
                for key, value in summary.items():
                    if key != 'condition':
                        print(f"  {key.replace('_', ' ').title()}: {value}")
            
            return True
            
        else:
            print(f"✗ Error: {response.status_code} - {response.text}")
            return False
            
    except Exception as e:
        print(f"✗ Exception: {e}")
        return False

def main():
    """Test chatbot with loaded data"""
    print("🧪 Testing HRSN Chatbot with Loaded Data")
    print("=" * 70)
    
    # First load test data
    if not load_test_data():
        print("❌ Failed to load test data. Exiting.")
        return 1
    
    print("\n" + "=" * 70)
    print("🤖 Now testing chatbot queries...")
    
    # Test questions that should now work with data
    test_questions = [
        "How many patients have food insecurity?",
        "Who are the high risk patients?", 
        "Which patients have housing problems?",
        "Show me patient statistics",
        "Who has safety concerns?"
    ]
    
    passed = 0
    total = len(test_questions)
    
    for question in test_questions:
        if test_chatbot_query(question):
            passed += 1
        print("\n" + "=" * 70)
    
    print(f"\n🎯 Final Results: {passed}/{total} queries successful")
    
    if passed == total:
        print("🎉 Chatbot is working perfectly with patient data!")
        print("\n🌐 Visit http://localhost:8001 to try the web interface")
        print("💬 The chatbot is ready for queries!")
        return 0
    else:
        print("❌ Some queries failed. Check the output above.")
        return 1

if __name__ == "__main__":
    exit(main())