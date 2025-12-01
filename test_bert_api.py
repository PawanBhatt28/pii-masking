import requests
import json

BASE_URL = "http://localhost:8000/api/v1"
API_KEY = "demo-key"
HEADERS = {"X-API-Key": API_KEY, "Content-Type": "application/json"}

# Test WITHOUT BERT (baseline)
text = """My SSN is 123-45-6789 and my passport is X1234567. 
Credit Card: 4111-1111-1111-1111, IBAN: GB33BUKB20201555555555.
Contact: john.doe@example.com, +1-202-555-0173"""

payload = {
    "text": text,
    "session_id": "bert_test",
    "context": {"user_id": "demo", "user_role": "admin"}
}

print("=" * 80)
print("BERT API INTEGRATION TEST")
print("=" * 80)
print(f"\nTest Text:\n{text}\n")

resp = requests.post(f"{BASE_URL}/mask", json=payload, headers=HEADERS)

if resp.status_code == 200:
    data = resp.json()
    
    print(f"✅ API Response: SUCCESS")
    print(f"Detected Entities: {len(data['entities'])}")
    print(f"Risk Score: {data['risk_score']}/10\n")
    
    print("Entities Found:")
    for entity in data['entities']:
        print(f"  • {entity['type']}: '{entity['text']}' (score: {entity['score']:.2f})")
    
    print("\n" + "=" * 80)
    print("MASKED TEXT:")
    print("=" * 80)
    print(data['masked_text'])
    
    print("\n" + "=" * 80)
    print("BERT FALLBACK STATUS:")
    print("=" * 80)
    print("Check Docker logs for: 'HuggingFace BERT fallback enabled/disabled'")
    print("\nTo enable BERT:")
    print("1. Get free API key: https://huggingface.co/settings/tokens")
    print("2. Add to .env: HUGGINGFACE_API_KEY=your_key_here")
    print("3. Restart: docker-compose restart api")
    
else:
    print(f"❌ Error: {resp.status_code}")
    print(resp.text)
