"""
Test script for RAG Chatbot API
Tests the /ask endpoint with sample questions
"""
import requests
import json
import time
from typing import Dict, Any

# Configuration
API_BASE_URL = "http://localhost:8000"
TIMEOUT = 30


def test_health_check() -> bool:
    """Test the health check endpoint"""
    print("Testing health check...")
    try:
        response = requests.get(f"{API_BASE_URL}/health", timeout=5)
        if response.status_code == 200:
            print("✓ Health check passed")
            return True
        else:
            print(f"✗ Health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"✗ Health check error: {e}")
        return False


def test_stats() -> Dict[str, Any]:
    """Get collection statistics"""
    print("\nGetting collection stats...")
    try:
        response = requests.get(f"{API_BASE_URL}/stats", timeout=5)
        if response.status_code == 200:
            stats = response.json()
            print(f"✓ Collection: {stats.get('collection_name')}")
            print(f"  Vectors: {stats.get('vectors_count', 'N/A')}")
            print(f"  Points: {stats.get('points_count', 'N/A')}")
            return stats
        else:
            print(f"✗ Stats request failed: {response.status_code}")
            return {}
    except Exception as e:
        print(f"✗ Stats error: {e}")
        return {}


def ask_question(question: str) -> Dict[str, Any]:
    """Ask a question to the RAG chatbot"""
    print(f"\nQuestion: {question}")
    print("Querying...")
    
    try:
        start_time = time.time()
        response = requests.post(
            f"{API_BASE_URL}/ask",
            json={"question": question},
            timeout=TIMEOUT
        )
        elapsed_time = time.time() - start_time
        
        if response.status_code == 200:
            result = response.json()
            answer = result.get("answer", "No answer")
            sources = result.get("sources", [])
            
            print(f"\n✓ Answer (in {elapsed_time:.2f}s):")
            print(f"  {answer}")
            
            if sources:
                print(f"\n  Sources ({len(sources)} found):")
                for i, source in enumerate(sources[:3], 1):  # Show top 3
                    print(f"    {i}. Score: {source.get('score', 'N/A'):.3f}")
                    text_preview = source.get('text', '')[:100]
                    print(f"       Preview: {text_preview}...")
            
            return result
        else:
            print(f"✗ Query failed: {response.status_code}")
            print(f"  Error: {response.text}")
            return {}
            
    except requests.Timeout:
        print(f"✗ Query timed out after {TIMEOUT}s")
        return {}
    except Exception as e:
        print(f"✗ Query error: {e}")
        return {}


def main():
    """Main test function"""
    print("=" * 60)
    print("RAG Chatbot API Test")
    print("=" * 60)
    
    # Test health
    if not test_health_check():
        print("\n⚠️  Backend is not healthy. Make sure services are running:")
        print("   docker-compose up -d")
        return
    
    # Get stats
    stats = test_stats()
    if stats.get('vectors_count', 0) == 0:
        print("\n⚠️  No documents indexed. Run the loader:")
        print("   docker exec openwebui-backend-1 python loader.py")
        print("\nContinuing with test questions anyway...\n")
    
    # Test questions
    questions = [
        "What is RAG and how does it work?",
        "What are the benefits of this system?",
        "How do I add more documents?",
        "What models can I use with Ollama?",
        "What are the use cases for this chatbot?",
    ]
    
    print("\n" + "=" * 60)
    print("Testing Sample Questions")
    print("=" * 60)
    
    for question in questions:
        ask_question(question)
        time.sleep(1)  # Brief pause between questions
    
    print("\n" + "=" * 60)
    print("Test Complete!")
    print("=" * 60)


if __name__ == "__main__":
    main()
