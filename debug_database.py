#!/usr/bin/env python3
"""
Debug script to see what's actually in the chatbot database
"""

import requests
import json

def load_test_data():
    """Load test bundles to populate database"""
    bundles = [
        "hrsn_bundle_1_complete.json",
        "hrsn_bundle_2_complete.json", 
        "hrsn_bundle_3_complete.json"
    ]
    
    print("📁 Loading test bundles...")
    for bundle_file in bundles:
        try:
            with open(bundle_file, "r") as f:
                bundle_data = json.load(f)
            
            response = requests.post(
                "http://localhost:8001/api/process-bundle",
                json=bundle_data,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                result = response.json()
                print(f"✓ {bundle_file}: {len(result['patients'])} patients, {len(result['responses'])} responses")
            else:
                print(f"✗ {bundle_file}: Error {response.status_code}")
                
        except Exception as e:
            print(f"✗ {bundle_file}: {e}")

def debug_chatbot():
    """Test specific chatbot queries for debugging"""
    
    test_queries = [
        "Tell me about all patients",
        "How many patients do we have?",
        "Show me patient statistics",
        "Who are the patients?",
        "List all patients"
    ]
    
    print("\n🔍 Testing patient listing queries...")
    
    for question in test_queries:
        print(f"\n❓ Question: {question}")
        
        try:
            response = requests.post(
                "http://localhost:8001/api/chatbot",
                json={"question": question},
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                result = response.json()
                print(f"📝 Answer: {result['answer']}")
                
                if result.get('data'):
                    print(f"👥 Patients returned: {len(result['data'])}")
                    for i, patient in enumerate(result['data'], 1):
                        print(f"  {i}. {patient.get('name', 'Unknown')}")
                        print(f"     ID: {patient.get('patient_id', 'N/A')}")
                        print(f"     Gender: {patient.get('gender', 'N/A')}")
                        print(f"     Birth Date: {patient.get('birth_date', 'N/A')}")
                else:
                    print("👥 No patient data returned")
                    
                if result.get('summary'):
                    print(f"📊 Summary: {result['summary']}")
                    
            else:
                print(f"❌ Error: {response.status_code}")
                
        except Exception as e:
            print(f"❌ Exception: {e}")

def main():
    print("🔍 HRSN Database Debug Tool")
    print("=" * 50)
    
    # Load test data first
    load_test_data()
    
    # Test chatbot queries
    debug_chatbot()
    
    print("\n" + "=" * 50)
    print("🎯 If you see all 3 patients listed above, the database is working correctly!")
    print("🎯 If not, there might be an issue with data storage or retrieval.")

if __name__ == "__main__":
    main()