import requests
import json

BASE_URL = "http://localhost:8000/api/v1"
API_KEY = "demo-key"
HEADERS = {"X-API-Key": API_KEY, "Content-Type": "application/json"}

# User's Indian PII test
text = """Hello, my name is Ramesh Kumar and my email is ramesh.kumar@example.in. 
My Aadhaar number is 1234-5678-9012 and PAN is ABCDE1234F. 
I have a HDFC credit card 4111-1111-1111-1111. 
My IP address is 203.91.115.10 and I was born on 15-Aug-1990."""

payload = {
    "text": text,
    "session_id": "indian_test",
    "context": {"user_id": "demo", "user_role": "admin"}
}

print("=" * 80)
print("INDIAN PII TEST (After Fixes)")
print("=" * 80)
print(f"\nOriginal Text:\n{text}\n")

resp = requests.post(f"{BASE_URL}/mask", json=payload, headers=HEADERS)

if resp.status_code == 200:
    data = resp.json()
    
    print(f"✅ Detected {len(data['entities'])} PII entities")
    print(f"Risk Score: {data['risk_score']}/10\n")
    
    print("Detected Entities:")
    for entity in data['entities']:
        print(f"  • {entity['type']}: '{entity['text']}' (score: {entity['score']:.2f})")
    
    print("\n" + "=" * 80)
    print("MASKED TEXT:")
    print("=" * 80)
    print(data['masked_text'])
    
    # Check for issues
    print("\n" + "=" * 80)
    print("VALIDATION:")
    print("=" * 80)
    
    aadhaar_masked = "1234-5678-9012" not in data['masked_text']
    pan_masked = "ABCDE1234F" not in data['masked_text']
    no_keyword_masking = "PAN" not in [e['text'] for e in data['entities']]
    
    print(f"✅ Aadhaar masked: {aadhaar_masked}")
    print(f"✅ PAN masked: {pan_masked}")
    print(f"✅ No keyword masking: {no_keyword_masking}")
    
else:
    print(f"❌ Error: {resp.status_code}")
    print(resp.text)
