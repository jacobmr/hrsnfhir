#!/usr/bin/env python3
"""
Comprehensive demo of the HRSN Chatbot functionality
"""

import requests
import json

def demo_chatbot():
    """Demonstrate the chatbot capabilities"""
    print("🎭 HRSN Chatbot Demonstration")
    print("=" * 50)
    print("🌟 Key Features:")
    print("  ✅ Real-time patient data analysis")
    print("  ✅ SDOH condition queries")
    print("  ✅ Safety risk assessment")
    print("  ✅ Patient identification with hyperlinks")
    print("  ✅ Statistical summaries")
    print("  ✅ Natural language processing")
    print()
    
    # Demo questions that showcase different capabilities
    demo_queries = [
        {
            "question": "How many patients do we have?",
            "feature": "📊 Database Overview"
        },
        {
            "question": "Who are the high risk patients?", 
            "feature": "⚠️ Safety Risk Assessment"
        },
        {
            "question": "Show me patient statistics",
            "feature": "📈 Comprehensive Analytics"
        },
        {
            "question": "Tell me about all patients",
            "feature": "👥 Patient Directory"
        },
        {
            "question": "Which patients have transportation issues?",
            "feature": "🚗 Transportation Analysis"
        }
    ]
    
    print("🎬 Live Demo Queries:")
    print("-" * 50)
    
    for i, demo in enumerate(demo_queries, 1):
        print(f"\n{i}. {demo['feature']}")
        print(f"   Q: \"{demo['question']}\"")
        
        try:
            response = requests.post(
                "http://localhost:8001/api/chatbot",
                json={"question": demo['question']},
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                result = response.json()
                answer = result['answer'].replace('\n', '\n   ')
                print(f"   A: {answer}")
                
                if result.get('data'):
                    print(f"   📋 Found {len(result['data'])} relevant patients")
                    
            else:
                print(f"   ❌ Error: {response.status_code}")
                
        except Exception as e:
            print(f"   ❌ Exception: {e}")
    
    print("\n" + "=" * 50)
    print("🎯 Chatbot Capabilities Summary:")
    print("  • Natural language query processing")
    print("  • Real-time data analysis from FHIR bundles")
    print("  • Statistical reporting with percentages")
    print("  • Patient identification and linking")
    print("  • SDOH category-specific analysis")
    print("  • Safety risk scoring (AHC HRSN standard)")
    print("  • Multi-condition correlation analysis")
    
    print("\n💡 Example Questions You Can Ask:")
    example_questions = [
        "How many patients have food insecurity?",
        "Who has housing problems?", 
        "Show me safety statistics",
        "Which patients need transportation help?",
        "Tell me about high risk patients",
        "What are the overall patient demographics?"
    ]
    
    for q in example_questions:
        print(f"  • \"{q}\"")
    
    print(f"\n🌐 Web Interface: http://localhost:8001")
    print("🤖 Try the chatbot in your browser!")

if __name__ == "__main__":
    demo_chatbot()