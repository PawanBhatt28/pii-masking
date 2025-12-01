import requests
import json
import time

BASE_URL = "http://localhost:8000/api/v1"
API_KEY = "test_api_key_12345"  # Ensure this matches .env or is valid
HEADERS = {
    "X-API-Key": API_KEY,
    "Content-Type": "application/json"
}

def test_bert_detection():
    print("\n--- Testing BERT (Deberta v3) Detection ---")
    # Text with names and locations that Presidio might miss without BERT
    text = "My name is Ananya Sharma and I live in Bangalore."
    
    payload = {
        "session_id": "test_bert_session",
        "text": text,
        "purpose": "Test BERT"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/mask", headers=HEADERS, json=payload)
        if response.status_code == 200:
            data = response.json()
            print("✅ Masking Success")
            print(f"Original: {text}")
            print(f"Masked:   {data['masked_text']}")
            
            # Check metadata
            meta = data.get('metadata', {})
            print(f"BERT Enabled: {meta.get('bert_enabled')}")
            print(f"BERT Entities Found: {meta.get('bert_entities_found')}")
            
            # Check entities
            entities = data.get('entities', [])
            entity_list = [f"{e['type']} ({e.get('source', '?')})" for e in entities]
            print(f"Entities: {entity_list}")
            
            if meta.get('bert_entities_found') > 0:
                print("✅ BERT is working!")
            else:
                print("⚠️ BERT found 0 entities. Check API key or model status.")
                
            return data
        else:
            print(f"❌ Masking Failed: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        print(f"❌ Error: {e}")
        return None

if __name__ == "__main__":
    # Wait for service to be ready
    print("Waiting for API to be ready...")
    time.sleep(5)
    
    test_bert_detection()
