import requests
import json
import time

BASE_URL = "http://localhost:8000/api/v1"
API_KEY = "test_api_key_12345"  # Ensure this matches .env or is valid
HEADERS = {
    "X-API-Key": API_KEY,
    "Content-Type": "application/json"
}

def test_masking_and_detection():
    print("\n--- Testing Masking & Detection (Phases 1-3) ---")
    # Valid Aadhaar (Verhoeff compliant) and PAN
    text = "My name is John Doe, born on 12/05/1990. My PAN is ABCDE1234F and Aadhaar is 3675 9834 6015."
    
    payload = {
        "session_id": "test_session_123",
        "text": text,
        "pii_types": ["PERSON", "DATE_TIME", "IN_PAN", "IN_AADHAAR"],
        "purpose": "Test Automation"
    }

    try:
        response = requests.post(f"{BASE_URL}/mask", headers=HEADERS, json=payload)
        if response.status_code == 200:
            data = response.json()
            print("✅ Masking Success")
            print(f"Original: {text}")
            print(f"Masked:   {data['masked_text']}")
            print(f"Entities: {[e['type'] for e in data['entities']]}")
            return data
        else:
            print(f"❌ Masking Failed: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        print(f"❌ Error: {e}")
        return None

def test_unmasking(masked_data):
    if not masked_data: return
    print("\n--- Testing Unmasking ---")
    
    payload = {
        "session_id": masked_data['session_id'],
        "text": masked_data['masked_text'],
        "reason": "Verification",
        "context": {"user_role": "admin"}
    }
    
    try:
        response = requests.post(f"{BASE_URL}/unmask", headers=HEADERS, json=payload)
        if response.status_code == 200:
            data = response.json()
            print("✅ Unmasking Success")
            print(f"Unmasked: {data['unmasked_text']}")
        else:
            print(f"❌ Unmasking Failed: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"❌ Error: {e}")

def test_admin_apis():
    print("\n--- Testing Admin APIs ---")
    
    # 1. Audit Logs
    try:
        response = requests.get(f"{BASE_URL}/audit?limit=5", headers=HEADERS)
        if response.status_code == 200:
            logs = response.json()
            print(f"✅ Audit Logs: Retrieved {len(logs)} events")
            if logs:
                print(f"Latest Event: {logs[0]['operation']} - {logs[0]['timestamp']}")
        else:
            print(f"❌ Audit Logs Failed: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"❌ Audit Error: {e}")

    # 2. Vault Inspection
    try:
        response = requests.get(f"{BASE_URL}/admin/vault?limit=5", headers=HEADERS)
        if response.status_code == 200:
            entries = response.json()
            print(f"✅ Vault Entries: Retrieved {len(entries)} entries")
            if entries:
                print(f"Sample Key: {entries[0]['key']}")
        else:
            print(f"❌ Vault Inspection Failed: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"❌ Vault Error: {e}")

if __name__ == "__main__":
    # Wait for service to be ready
    print("Waiting for API to be ready...")
    time.sleep(5)
    
    masked_data = test_masking_and_detection()
    if masked_data:
        test_unmasking(masked_data)
        test_admin_apis()
