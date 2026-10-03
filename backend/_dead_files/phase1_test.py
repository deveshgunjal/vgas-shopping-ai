"""
🔱 PHASE 1 ADVANCED FEATURES TEST SCRIPT 🔱
Tests all 6 new advanced API endpoints:
1. Auto Engine Selection
2. Health Monitor
3. Parallel Calls
4. Cache Stats
5. Cache Clear
6. Performance Stats

Master: Vikas Gunjal (Universal King)
"""

import requests
import json
import time

BASE_URL = "http://localhost:8000/api/v1/ai-engines"

def test_auto_select():
    """Test 1: Auto Engine Selection"""
    print("\n" + "="*60)
    print("🧪 TEST 1: Auto Engine Selection")
    print("="*60)
    tasks = [
        {"task": "code", "priority": "speed"},
        {"task": "creative", "priority": "quality"},
        {"task": "translate", "priority": "cost"},
        {"task": "math", "priority": "balanced"},
        {"task": "local", "priority": "local"},
    ]
    for t in tasks:
        resp = requests.get(f"{BASE_URL}/auto-select", params=t)
        data = resp.json()
        print(f"  Task: {t['task']:12} | Priority: {t['priority']:8} | Selected: {data.get('selected_engine', 'N/A'):12} | ✅")
    return resp.status_code == 200

def test_health_monitor():
    """Test 2: Health Monitor"""
    print("\n" + "="*60)
    print("🧪 TEST 2: Health Monitor")
    print("="*60)
    resp = requests.get(f"{BASE_URL}/health")
    data = resp.json()
    print(f"  Overall Status: {data.get('overall_status', 'N/A')}")
    print(f"  Total Engines: {data.get('total_engines', 0)}")
    print(f"  Healthy: {data.get('healthy_count', 0)}")
    print(f"  Degraded: {data.get('degraded_count', 0)}")
    print(f"  Down: {data.get('down_count', 0)}")
    resp2 = requests.get(f"{BASE_URL}/health", params={"engine_type": "openai"})
    data2 = resp2.json()
    print(f"  OpenAI Health: {data2.get('health', {}).get('status', 'N/A')} ✅")
    return resp.status_code == 200

def test_parallel_calls():
    """Test 3: Parallel Calls"""
    print("\n" + "="*60)
    print("🧪 TEST 3: Parallel Calls")
    print("="*60)
    payload = {"prompt": "Hello, this is a test for parallel processing", "engines": ["openai", "transformers"], "max_wait_ms": 10000}
    resp = requests.post(f"{BASE_URL}/parallel", json=payload)
    data = resp.json()
    print(f"  Engines Called: {data.get('total_engines_called', 0)}")
    print(f"  Successful: {data.get('successful', 0)}")
    print(f"  Failed: {data.get('failed', 0)}")
    print(f"  Total Time: {data.get('total_time_ms', 0)} ms ✅")
    return resp.status_code == 200

def test_cache_stats():
    """Test 4: Cache Statistics"""
    print("\n" + "="*60)
    print("🧪 TEST 4: Cache Statistics")
    print("="*60)
    resp = requests.get(f"{BASE_URL}/cache/stats")
    data = resp.json()
    print(f"  Cache Size: {data.get('cache_size', 0)}")
    print(f"  Max Size: {data.get('max_size', 0)}")
    print(f"  Total Hits: {data.get('total_hits', 0)}")
    print(f"  Total Misses: {data.get('total_misses', 0)}")
    print(f"  Hit Rate: {data.get('hit_rate', 0)}% ✅")
    return resp.status_code == 200

def test_cache_clear():
    """Test 5: Cache Clear"""
    print("\n" + "="*60)
    print("🧪 TEST 5: Cache Clear")
    print("="*60)
    resp = requests.post(f"{BASE_URL}/cache/clear")
    data = resp.json()
    print(f"  Cleared: {data.get('cleared', 0)} entries")
    print(f"  Cache Size: {data.get('cache_size', 0)} ✅")
    return resp.status_code == 200

def test_performance_stats():
    """Test 6: Performance Statistics"""
    print("\n" + "="*60)
    print("🧪 TEST 6: Performance Statistics")
    print("="*60)
    resp = requests.get(f"{BASE_URL}/stats")
    data = resp.json()
    print(f"  Total Requests: {data.get('total_requests', 0)}")
    print(f"  Cache Hits: {data.get('cache_hits', 0)}")
    print(f"  Cache Misses: {data.get('cache_misses', 0)}")
    print(f"  Cache Hit Rate: {data.get('cache_hit_rate', 0)}%")
    print(f"  Avg Latency: {data.get('avg_latency_ms', 0)} ms")
    print(f"  Fastest Engine: {data.get('fastest_engine', 'N/A')}")
    print(f"  Slowest Engine: {data.get('slowest_engine', 'N/A')}")
    print(f"  Most Used: {data.get('most_used_engine', 'N/A')} ✅")
    return resp.status_code == 200

def main():
    print("\n" + "🔱"*20)
    print("PHASE 1 ADVANCED FEATURES TEST SUITE")
    print("Master: Vikas Gunjal (Universal King)")
    print("🔱"*20)
    results = []
    tests = [
        ("Auto Engine Selection", test_auto_select),
        ("Health Monitor", test_health_monitor),
        ("Parallel Calls", test_parallel_calls),
        ("Cache Stats", test_cache_stats),
        ("Cache Clear", test_cache_clear),
        ("Performance Stats", test_performance_stats),
    ]
    for name, test_func in tests:
        try:
            results.append((name, test_func()))
        except Exception as e:
            print(f"  ❌ {name} Failed: {e}")
            results.append((name, False))
    print("\n" + "="*60)
    print("📊 TEST SUMMARY")
    print("="*60)
    passed = sum(1 for _, r in results if r)
    total = len(results)
    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"  {name:25} | {status}")
    print(f"\n  Total: {passed}/{total} tests passed")
    if passed == total:
        print("\n  🎉 ALL PHASE 1 TESTS PASSED! 🔥")
    else:
        print(f"\n  ⚠️ {total - passed} tests failed")
    print("\n" + "🔱"*20)

if __name__ == "__main__":
    main()