#!/usr/bin/env python3
"""
Test script for the HRSN Chatbot functionality
"""

import requests
import json

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
                for patient in result['data'][:5]:  # Show first 5
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
    """Test various chatbot queries"""
    print("🧪 Testing HRSN Chatbot Functionality")
    print("=" * 70)
    
    # Test questions
    test_questions = [
        "How many patients have food insecurity?",
        "Who are the high risk patients?", 
        "Which patients have housing problems?",
        "Tell me about transportation issues",
        "Show me patient statistics",
        "How many patients do we have?",
        "Who has safety concerns?",
        "What can you tell me about the patients?"
    ]
    
    passed = 0
    total = len(test_questions)
    
    for question in test_questions:
        if test_chatbot_query(question):
            passed += 1
        print("\n" + "=" * 70)
    
    print(f"\n🎯 Chatbot Test Results: {passed}/{total} queries successful")
    
    if passed == total:
        print("🎉 All chatbot queries working perfectly!")
        print("\n🌐 Try the web interface at: http://localhost:8001")
        print("💬 Ask questions like:")
        for q in test_questions[:4]:
            print(f"   • \"{q}\"")
        return 0
    else:
        print("❌ Some queries failed. Check the output above.")
        return 1

if __name__ == "__main__":
    exit(main())