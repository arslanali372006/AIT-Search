#!/usr/bin/env python3
"""
Test search performance for single-word and multi-word searches.
Target: single-word <500ms, multi-word <1.5s
"""
import requests
import time

BASE_URL = "http://localhost:8000/api"

def test_single_word_search(query):
    """Test single-word search performance"""
    print(f"\n{'='*60}")
    print(f"Testing single-word search: '{query}'")
    print(f"{'='*60}")
    
    start = time.time()
    response = requests.post(f"{BASE_URL}/search/single", json={"query": query, "top_k": 10})
    end = time.time()
    
    elapsed = (end - start) * 1000  # Convert to milliseconds
    results = response.json()
    
    print(f"⏱️  Time taken: {elapsed:.2f}ms")
    print(f"📊 Results count: {len(results)}")
    print(f"✅ Status: {'PASS' if elapsed < 500 else '❌ FAIL'} (target: <500ms)")
    
    if results:
        print(f"🔝 Top result: {results[0]['doc_id']} (score: {results[0]['score']:.4f})")
    
    return elapsed, len(results)

def test_multi_word_search(query):
    """Test multi-word search performance"""
    print(f"\n{'='*60}")
    print(f"Testing multi-word search: '{query}'")
    print(f"{'='*60}")
    
    start = time.time()
    response = requests.post(f"{BASE_URL}/search/multi", json={"query": query, "top_k": 10})
    end = time.time()
    
    elapsed = (end - start) * 1000  # Convert to milliseconds
    results = response.json()
    
    print(f"⏱️  Time taken: {elapsed:.2f}ms")
    print(f"📊 Results count: {len(results)}")
    print(f"✅ Status: {'PASS' if elapsed < 1500 else '❌ FAIL'} (target: <1500ms)")
    
    if results:
        print(f"🔝 Top result: {results[0]['doc_id']} (score: {results[0]['score']:.4f})")
    
    return elapsed, len(results)

def test_semantic_search(query):
    """Test semantic search (no strict time requirement)"""
    print(f"\n{'='*60}")
    print(f"Testing semantic search: '{query}'")
    print(f"{'='*60}")
    
    start = time.time()
    response = requests.post(f"{BASE_URL}/search/semantic", json={"query": query, "top_k": 10})
    end = time.time()
    
    elapsed = (end - start) * 1000  # Convert to milliseconds
    results = response.json()
    
    print(f"⏱️  Time taken: {elapsed:.2f}ms ({elapsed/1000:.2f}s)")
    print(f"📊 Results count: {len(results)}")
    print(f"ℹ️  Note: Semantic search can be slower (acceptable)")
    
    if results:
        print(f"🔝 Top result: {results[0]['doc_id']} (score: {results[0]['score']:.4f})")
    
    return elapsed, len(results)

if __name__ == "__main__":
    print("\n🚀 SEARCH ENGINE PERFORMANCE TEST")
    print(f"{'='*60}")
    
    # Test single-word searches
    single_tests = ["covid", "vaccine", "protein", "treatment", "symptoms"]
    single_times = []
    
    for query in single_tests:
        elapsed, _ = test_single_word_search(query)
        single_times.append(elapsed)
        time.sleep(0.5)  # Brief pause between requests
    
    # Test multi-word searches
    multi_tests = [
        "covid vaccine efficacy",
        "coronavirus treatment options",
        "immune system response"
    ]
    multi_times = []
    
    for query in multi_tests:
        elapsed, _ = test_multi_word_search(query)
        multi_times.append(elapsed)
        time.sleep(0.5)
    
    # Test semantic search (just one example)
    semantic_elapsed, _ = test_semantic_search("infection prevention methods")
    
    # Summary
    print(f"\n{'='*60}")
    print("📈 PERFORMANCE SUMMARY")
    print(f"{'='*60}")
    
    avg_single = sum(single_times) / len(single_times)
    avg_multi = sum(multi_times) / len(multi_times)
    
    print(f"\n📊 Single-Word Search:")
    print(f"   Average: {avg_single:.2f}ms")
    print(f"   Min: {min(single_times):.2f}ms")
    print(f"   Max: {max(single_times):.2f}ms")
    print(f"   Target: <500ms")
    print(f"   Status: {'✅ PASS' if avg_single < 500 else '❌ FAIL'}")
    
    print(f"\n📊 Multi-Word Search:")
    print(f"   Average: {avg_multi:.2f}ms")
    print(f"   Min: {min(multi_times):.2f}ms")
    print(f"   Max: {max(multi_times):.2f}ms")
    print(f"   Target: <1500ms")
    print(f"   Status: {'✅ PASS' if avg_multi < 1500 else '❌ FAIL'}")
    
    print(f"\n📊 Semantic Search:")
    print(f"   Time: {semantic_elapsed:.2f}ms ({semantic_elapsed/1000:.2f}s)")
    print(f"   Status: ℹ️  No strict requirement (acceptable)")
    
    print(f"\n{'='*60}")
    print("🎉 TEST COMPLETE!")
    print(f"{'='*60}\n")
