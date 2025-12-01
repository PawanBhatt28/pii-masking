import requests
import json
import time

BASE_URL = "http://localhost:8000/api/v1"
API_KEY = "demo-key"  # Any key works for MVP
HEADERS = {"X-API-Key": API_KEY}

def print_step(step, message):
    print(f"\n{'='*50}")
    print(f"STEP {step}: {message}")
    print(f"{'='*50}")

def demo():
    print("🚀 Starting PII Shield Demo...")
    
    # 1. Health Check
    print_step(1, "Checking System Health")
    try:
        resp = requests.get(f"{BASE_URL}/health")
        print(json.dumps(resp.json(), indent=2))
    except Exception as e:
        print(f"❌ System not running: {e}")
        print("Please run 'docker-compose up -d' first!")
        return

    # 2. Masking
    print_step(2, "Masking Sensitive Data")
    text = "My name is John Doe, email is john.doe@example.com, and my SSN is 123-45-6789."
    session_id = f"demo_session_{int(time.time())}"
    
    payload = {
        "text": text,
        "session_id": session_id,
        "context": {
            "user_id": "demo_user",
            "purpose": "demo",
            "user_role": "customer_service"
        }
    }
    
    resp = requests.post(f"{BASE_URL}/mask", json=payload, headers=HEADERS)
    if resp.status_code != 200:
        print(f"❌ Error: {resp.text}")
        return
        
    mask_data = resp.json()
    print(f"Original: {text}")
    print(f"Masked:   {mask_data['masked_text']}")
    print(f"Risk Score: {mask_data['risk_score']}")
    
    masked_text = mask_data['masked_text']

    # 3. Unmasking (Authorized)
    print_step(3, "Unmasking (Authorized Agent)")
    
    unmask_payload = {
        "text": masked_text,
        "session_id": session_id,
        "context": {
            "user_id": "agent_007",
            "user_role": "customer_service", # Allowed to unmask (except SSN maybe)
            "purpose": "customer_support"
        }
    }
    
    resp = requests.post(f"{BASE_URL}/unmask", json=unmask_payload, headers=HEADERS)
    unmask_data = resp.json()
    print(f"Unmasked Text: {unmask_data['unmasked_text']}")
    
    # 4. Unmasking (Unauthorized/Restricted)
    # Let's try to unmask SSN specifically if logic forbids it (our logic forbids SSN for customer_service)
    # The previous unmask might have kept SSN masked if logic works!
    
    # 5. Audit Logs
    print_step(4, "Checking Audit Logs")
    resp = requests.get(f"{BASE_URL}/audit?session_id={session_id}", headers=HEADERS)
    logs = resp.json()
    print(f"Found {len(logs)} audit events:")
    for log in logs:
        print(f"- [{log['timestamp']}] {log['operation']} by {log['user_role']}")

if __name__ == "__main__":
    demo()
