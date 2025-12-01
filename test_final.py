import requests
import json

BASE_URL = "http://localhost:8000/api/v1"
API_KEY = "demo-key"
HEADERS = {"X-API-Key": API_KEY, "Content-Type": "application/json"}

# Test the FULL message from user's earlier example
text = """Hello, my name is John Doe and my email is john.doe@example.com. You can reach me at +1-202-555-0173. My SSN is 123-45-6789, and my passport number is X1234567. I have a credit card 4111-1111-1111-1111 linked to IBAN GB33BUKB20201555555555. My IP address is 192.168.0.1 and I was born on 2025-11-30. My address is 123 Main St, New York, NY.

Alice Smith just signed up with email alice.smith@mail.com, phone +44 7700 900123. Her SSN is 987-65-4321 and passport P9876543. She also owns credit card 5500-0000-0000-0004 with IBAN DE89370400440532013000. Current IP: 10.0.0.5. Date of joining: 12/31/2024. Address: 221B Baker Street, London.

Mohammed Khan contacted support. Email: user123@gmail.com, Phone: +91-9876543210, SSN: 111-22-3333, Passport: M8765432, Credit Card: 3400-0000-0000-009, IBAN: GB33BUKB20201555555555, IP: 172.16.5.4, Date of registration: 01-Jan-2023, Address: No. 5, MG Road, Mumbai."""

payload = {
    "text": text,
    "session_id": "final_test",
    "context": {"user_id": "demo", "user_role": "admin"}
}

print("=" * 80)
print("FINAL PRODUCTION-GRADE TEST")
print("=" * 80)
print(f"\nOriginal Text Length: {len(text)} characters\n")

resp = requests.post(f"{BASE_URL}/mask", json=payload, headers=HEADERS)

if resp.status_code == 200:
    data = resp.json()
    
    print(f"✅ SUCCESS! Detected {len(data['entities'])} PII entities")
    print(f"Risk Score: {data['risk_score']}/10\n")
    
    # Group by type
    by_type = {}
    for entity in data['entities']:
        etype = entity['type']
        if etype not in by_type:
            by_type[etype] = []
        by_type[etype].append(entity)
    
    print("Detected Entities by Type:")
    print("-" * 80)
    for etype, entities in sorted(by_type.items()):
        print(f"\n{etype} ({len(entities)} found):")
        for e in entities:
            print(f"  • '{e['text']}' (confidence: {e['score']:.2f})")
    
    print("\n" + "=" * 80)
    print("MASKED OUTPUT (First 500 chars):")
    print("=" * 80)
    print(data['masked_text'][:500] + "...")
    
else:
    print(f"❌ Error: {resp.status_code}")
    print(resp.text)
