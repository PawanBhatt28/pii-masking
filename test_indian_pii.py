import requests
import json

BASE_URL = "http://localhost:8000/api/v1"
API_KEY = "demo-key"
HEADERS = {"X-API-Key": API_KEY, "Content-Type": "application/json"}

# Test comprehensive PII including Indian entities
text = """
Test Indian PII:
- Aadhaar: 1234 5678 9012
- PAN: ABCDE1234F
- Indian Passport: A1234567
- Phone: +91-9876543210

Test International:
- US SSN: 123-45-6789
- UK Passport: P1234567
- IBAN: GB33BUKB20201555555555
- Phone: +44 7700 900123
"""

payload = {
    "text": text,
    "session_id": "comprehensive_test",
    "context": {"user_id": "demo", "user_role": "admin"}
}

print("Testing Comprehensive PII Detection...")
print(f"Original Text: {text}\n")

resp = requests.post(f"{BASE_URL}/mask", json=payload, headers=HEADERS)

if resp.status_code == 200:
    data = resp.json()
    print(f"✅ Success! Detected {len(data['entities'])} PII entities\n")
    print("Detected Entities:")
    for entity in data['entities']:
        print(f"  - {entity['type']}: '{entity['text']}' (score: {entity['score']:.2f})")
    print(f"\nRisk Score: {data['risk_score']}")
else:
    print(f"❌ Error: {resp.status_code}")
    print(resp.text)
