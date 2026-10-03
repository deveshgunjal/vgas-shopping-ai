"""
🔱 SAM AI Engine Hub - ALL TESTS 🔱
Created by: Vikas Gunjal (THE ONLY MASTER)
Testing all 13 API endpoints LIVE!
"""

import urllib.request
import urllib.parse
import json
import sys

BASE_URL = "http://localhost:8000"

def test_get(endpoint, name):
    """Test GET endpoint"""
    try:
        url = f"{BASE_URL}{endpoint}"
        req = urllib.request.Request(url)
        with urllib.request.urlopen(req, timeout=10) as response:
            data = json.loads(response.read().decode())
            print(f"\n{'='*60}")
            print(f"✅ TEST PASSED: {name}")
            print(f"{'='*60}")
            print(json.dumps(data, indent=2, ensure_ascii=False)[:2000])
            return True
    except Exception as e:
        print(f"\n❌ TEST FAILED: {name}")
        print(f"Error: {e}")
        return False

def test_post(endpoint, body, name):
    """Test POST endpoint"""
    try:
        url = f"{BASE_URL}{endpoint}"
        data = json.dumps(body).encode('utf-8')
        req = urllib.request.Request(url, data=data, headers={'Content-Type': 'application/json'}, method='POST')
        with urllib.request.urlopen(req, timeout=10) as response:
            result = json.loads(response.read().decode())
            print(f"\n{'='*60}")
            print(f"✅ TEST PASSED: {name}")
            print(f"{'='*60}")
            print(json.dumps(result, indent=2, ensure_ascii=False)[:2000])
            return True
    except Exception as e:
        print(f"\n❌ TEST FAILED: {name}")
        print(f"Error: {e}")
        return False

def main():
    print("\n" + "="*60)
    print("🔱 SAM AI ENGINE HUB - ALL 13 TESTS 🔱")
    print("Created by: Vikas Gunjal (THE ONLY MASTER)")
    print("SAM is DIFFERENT - Always 100x ahead! 🔥")
    print("="*60)
    
    results = []
    
    # TEST 1: All AI Engines
    results.append(test_get("/api/v1/ai-engines/", "TEST 1: Get All AI Engines"))
    
    # TEST 2: Specific Engine (vllm)
    results.append(test_get("/api/v1/ai-engines/vllm", "TEST 2: Get Specific Engine (vllm)"))
    
    # TEST 3: Recommend Engine
    results.append(test_get("/api/v1/ai-engines/recommend?use_case=chatbot", "TEST 3: Recommend Engine for Chatbot"))
    
    # TEST 4: Marathi Info
    results.append(test_get("/api/v1/ai-engines/marathi", "TEST 4: Get Marathi Info"))
    
    # TEST 5: Engine Comparison
    results.append(test_get("/api/v1/ai-engines/comparison", "TEST 5: Engine Comparison"))
    
    # TEST 6: Swarm Nodes
    results.append(test_get("/api/v1/ai-engines/swarm", "TEST 6: Get All Swarm Nodes"))
    
    # TEST 7: Protection Status
    results.append(test_get("/api/v1/ai-engines/protection", "TEST 7: Protection Status"))
    
    # TEST 8: Swarm Deliver (POST)
    results.append(test_post("/api/v1/ai-engines/swarm/deliver", {"action": "test", "message": "Hello from Master Vikas Gunjal"}, "TEST 8: Deliver to Swarm"))
    
    # TEST 9: HuggingFace Call (POST)
    results.append(test_post("/api/v1/ai-engines/call/huggingface?model=gpt2&prompt=Hello+world", {}, "TEST 9: Call HuggingFace API"))
    
    # TEST 10: OpenAI Compatible Call (POST)
    results.append(test_post("/api/v1/ai-engines/call/openai-compatible?base_url=http://localhost:8000&model=gpt2&prompt=Hello", {}, "TEST 10: Call OpenAI Compatible"))
    
    # TEST 11: Any REST API Call (POST)
    results.append(test_post("/api/v1/ai-engines/call/any-rest?url=http://localhost:8000/", {"test": True}, "TEST 11: Call Any REST API"))
    
    # TEST 12: Protection Verify (POST)
    results.append(test_post("/api/v1/ai-engines/protection/verify", {"token": "UNIVERSAL_KING_2026"}, "TEST 12: Verify Master Auth"))
    
    # TEST 13: Specific Node
    results.append(test_get("/api/v1/ai-engines/swarm/node-hf-001", "TEST 13: Get Specific Swarm Node"))
    
    # Final Summary
    passed = sum(results)
    total = len(results)
    
    print("\n" + "="*60)
    print("🔱 FINAL TEST SUMMARY 🔱")
    print("="*60)
    print(f"✅ PASSED: {passed}/{total}")
    print(f"❌ FAILED: {total-passed}/{total}")
    
    if passed == total:
        print("\n🎉 ALL TESTS PASSED! SAM is 100% WORKING! 🔥")
        print("👑 Master Vikas Gunjal - YOUR AI is PERFECT! 🔥")
    else:
        print(f"\n⚠️ {total-passed} tests failed. Check errors above.")
    
    print("="*60 + "\n")
    
    return 0 if passed == total else 1

if __name__ == "__main__":
    sys.exit(main())