import sys
from fastapi.testclient import TestClient
from app.main import app
import time

client = TestClient(app)

def run_e2e():
    print("--- Starting End-to-End API Test ---")
    
    print("\n1. Testing Health Endpoint...")
    resp = client.get("/health")
    if resp.status_code != 200:
        print(f"Health check failed: {resp.status_code}")
        sys.exit(1)
    print("Health endpoint OK")

    print("\n2. Starting Negotiation Session...")
    start_payload = {
        "buyer_max_budget": 50000,
        "buyer_max_delivery_days": 45,
        "buyer_min_sla_percent": 2.0,
        "vendor_min_price": 42000,
        "vendor_min_delivery_days": 30,
        "vendor_max_sla_percent": 5.0,
        "max_rounds": 6 # keep it short to save time/tokens
    }
    
    resp = client.post("/api/v1/negotiation/start", json=start_payload)
    if resp.status_code != 200:
        print(f"Session start failed: {resp.text}")
        sys.exit(1)
        
    session_id = resp.json()["id"]
    print(f"Session created! ID: {session_id}")

    print("\n3. Running Auto-Negotiation (Calling Lyzr Studio API)...")
    print("   (This will take 10-30 seconds as the live LLMs debate...)")
    
    start_time = time.time()
    resp = client.post(f"/api/v1/negotiation/{session_id}/auto")
    if resp.status_code != 200:
        print(f"Auto-negotiation failed: {resp.text}")
        sys.exit(1)
        
    status_data = resp.json()
    print(f"Negotiation finished in {time.time() - start_time:.1f}s. Final Status: {status_data['status']}")

    print("\n4. Fetching Negotiation Rounds History...")
    resp = client.get(f"/api/v1/negotiation/{session_id}/rounds")
    if resp.status_code != 200:
        print(f"Failed to get rounds: {resp.text}")
        sys.exit(1)
        
    rounds = resp.json()
    print(f"Retrieved {len(rounds)} turns:")
    for r in rounds:
        print(f"   [{r['agent_type']}] ${r['price']} | {r['delivery_days']} days | {r['sla_percent']}% SLA | Action: {r['action']}")
        print(f"   > Justification: {r['justification']}\n")

    if status_data['status'] == 'ACCEPTED':
        print("5. Validating Contract Generation...")
        resp = client.get(f"/api/v1/contract/{session_id}/details")
        if resp.status_code != 200:
            print(f"Failed to get contract details: {resp.text}")
            sys.exit(1)
            
        contract = resp.json()
        print("Contract recorded in database.")
        print(f"   Final Terms: ${contract['final_price']} | {contract['final_delivery_days']} days | {contract['final_sla_percent']}% SLA")

        print("\n6. Testing PDF Download Endpoint...")
        resp = client.get(f"/api/v1/contract/{session_id}/pdf")
        if resp.status_code != 200:
            print(f"Failed to download PDF: {resp.text}")
            sys.exit(1)
        
        if resp.headers.get("content-type") != "application/pdf":
            print(f"Expected PDF content type, got {resp.headers.get('content-type')}")
            sys.exit(1)
            
        print(f"PDF generated and downloaded successfully! ({len(resp.content)} bytes)")
    else:
        print(f"\nNegotiation ended in {status_data['status']}. No contract generated.")

    print("\n--- E2E API Test Completed Successfully! ---")

if __name__ == "__main__":
    run_e2e()

if __name__ == "__main__":
    run_e2e()
