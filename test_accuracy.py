import requests
import json

BASE_URL = "http://localhost:8000/api/v1"
API_KEY = "demo-key"
HEADERS = {"X-API-Key": API_KEY, "Content-Type": "application/json"}

# Test the exact message from the user
text = "my credit card number is 123456, i am pawan bhatt and my dob is 15-05-1905, i live on street-7 koramangala, can you share the details please?"

payload = {
    "text": text,
    "session_id": "accuracy_test",
    "context": {"user_id": "demo", "user_role": "admin"}
}

print("Testing PII Detection Accuracy...")
print(f"Original Text: {text}\n")

resp = requests.post(f"{BASE_URL}/mask", json=payload, headers=HEADERS)
data = resp.json()
print(resp)

pretty_json = json.dumps(data, indent=4)
print(pretty_json)

# masked_response = data['masked_text']
# risk = data['risk_score']

# print("Masked response : " + masked_response)
# print("Risk : " + risk)


# print("Detected Entities:")
# for entity in data['entities']:
#     print(f"  - {entity['type']}: '{entity['text']}' (confidence: {entity['score']:.2f})")

# print(f"\nTotal PII Detected: {len(data['entities'])}")
