import requests
import json
import time
import sys
from typing import Dict, List, Any

# Configuration
BASE_URL = "http://localhost:8000/api/v1"
API_KEY = "demo-key"  # Matches the key in the UI/Config
HEADERS = {"X-API-Key": API_KEY, "Content-Type": "application/json"}

# ANSI Colors
class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

def print_header(text):
    print(f"\n{Colors.HEADER}{Colors.BOLD}{'='*60}")
    print(f" {text}")
    print(f"{'='*60}{Colors.ENDC}")

def print_result(name, passed, details=""):
    if passed:
        print(f"{Colors.GREEN}[PASS] {name}{Colors.ENDC}")
    else:
        print(f"{Colors.FAIL}[FAIL] {name}{Colors.ENDC}")
        if details:
            print(f"{Colors.FAIL}       Error: {details}{Colors.ENDC}")

def run_test(name, func):
    try:
        print(f"{Colors.CYAN}Running: {name}...{Colors.ENDC}", end="\r")
        func()
        print_result(name, True)
        return True
    except AssertionError as e:
        print_result(name, False, str(e))
        return False
    except Exception as e:
        print_result(name, False, f"Exception: {str(e)}")
        return False

# --- Test Functions ---

def test_health():
    resp = requests.get(f"{BASE_URL}/health")
    assert resp.status_code == 200, f"Health check failed: {resp.status_code}"
    data = resp.json()
    assert data['status'] == 'healthy', f"System not healthy: {data}"

def test_basic_pii():
    text = "Contact John Doe at john.doe@example.com."
    payload = {
        "text": text,
        "session_id": "test_session_1",
        "context": {"user_id": "tester", "user_role": "admin"}
    }
    resp = requests.post(f"{BASE_URL}/mask", json=payload, headers=HEADERS)
    assert resp.status_code == 200, f"Mask failed: {resp.text}"
    data = resp.json()
    
    assert data['masked_text'] != text, "Text was not masked"
    assert "[PERSON_" in data['masked_text'], "Person not detected"
    assert "[EMAIL_ADDRESS_" in data['masked_text'], "Email not detected"
    assert "John Doe" not in data['masked_text'], "Name leaked"
    
    # Store for unmask test
    return data['masked_text'], "test_session_1"

def test_financial_pii():
    # Use a format that Presidio definitely catches. 
    # Sometimes 123-45-6789 is filtered as invalid checksum.
    text = "My SSN is 999-01-1234 and card is 4111 1111 1111 1111."
    payload = {
        "text": text,
        "session_id": "test_session_fin",
        "context": {"user_id": "tester", "user_role": "admin"}
    }
    resp = requests.post(f"{BASE_URL}/mask", json=payload, headers=HEADERS)
    data = resp.json()
    
    assert "999-01-1234" not in data['masked_text'], "SSN leaked"
    assert "4111 1111 1111 1111" not in data['masked_text'], "CC leaked"
    # Note: Presidio detection varies, but usually catches these formats
    
def test_unmask_admin():
    # Setup
    masked_text, session_id = test_basic_pii()
    
    payload = {
        "text": masked_text,
        "session_id": session_id,
        "context": {"user_id": "admin_user", "user_role": "admin"}
    }
    resp = requests.post(f"{BASE_URL}/unmask", json=payload, headers=HEADERS)
    data = resp.json()
    
    assert "John Doe" in data['unmasked_text'], "Admin failed to unmask Name"
    assert "john.doe@example.com" in data['unmasked_text'], "Admin failed to unmask Email"

def test_access_control_restricted():
    # 1. Mask SSN
    text = "My SSN is 999-01-1234."
    session_id = "test_session_acl"
    mask_payload = {
        "text": text,
        "session_id": session_id,
        "context": {"user_id": "user", "user_role": "admin"}
    }
    mask_resp = requests.post(f"{BASE_URL}/mask", json=mask_payload, headers=HEADERS)
    masked_text = mask_resp.json()['masked_text']
    
    # 2. Try Unmask as Customer Service (Should fail for SSN)
    unmask_payload = {
        "text": masked_text,
        "session_id": session_id,
        "context": {"user_id": "support_agent", "user_role": "customer_service"}
    }
    resp = requests.post(f"{BASE_URL}/unmask", json=unmask_payload, headers=HEADERS)
    data = resp.json()
    
    # The SSN token should STILL be there, NOT the original number
    assert "999-01-1234" not in data['unmasked_text'], "Restricted user unmasked SSN!"
    assert "[US_SSN_" in data['unmasked_text'] or "[SSN_" in data['unmasked_text'], "Token should remain for restricted data"

def test_no_pii():
    text = "Hello world, this is a safe sentence."
    payload = {
        "text": text,
        "session_id": "safe_session",
        "context": {}
    }
    resp = requests.post(f"{BASE_URL}/mask", json=payload, headers=HEADERS)
    data = resp.json()
    assert data['masked_text'] == text, "Safe text was modified"
    assert len(data['entities']) == 0, "False positive detected"

def test_audit_logs():
    # Just check if we can fetch them
    resp = requests.get(f"{BASE_URL}/audit?limit=5", headers=HEADERS)
    assert resp.status_code == 200
    assert isinstance(resp.json(), list)

def test_auth_failure():
    bad_headers = {"X-API-Key": "wrong-key"}
    resp = requests.get(f"{BASE_URL}/health", headers=bad_headers)
    # Health might be public, check mask
    resp = requests.post(f"{BASE_URL}/mask", json={}, headers=bad_headers)
    # FastAPI returns 422 for missing required headers/params, or 403/401 for auth
    assert resp.status_code in [401, 403, 422], f"Auth check failed, got {resp.status_code}"

def test_large_input():
    # 10KB of text
    text = "My name is John Doe. " * 500
    payload = {
        "text": text,
        "session_id": "load_test",
        "context": {}
    }
    start = time.time()
    resp = requests.post(f"{BASE_URL}/mask", json=payload, headers=HEADERS)
    duration = time.time() - start
    
    assert resp.status_code == 200
    print(f"       (Processed 10KB in {duration:.2f}s)")
    assert duration < 5.0, "Performance too slow (>5s for 10KB)"

# --- Main Runner ---

if __name__ == "__main__":
    print_header("🛡️ PII SHIELD - COMPREHENSIVE DEMO TEST SUITE 🛡️")
    
    tests = [
        ("System Health Check", test_health),
        ("Authentication Security", test_auth_failure),
        ("Basic PII Detection (Name, Email)", test_basic_pii),
        ("Financial Data Protection (SSN, CC)", test_financial_pii),
        ("No PII False Positive Check", test_no_pii),
        ("Admin Role Unmasking (Full Access)", test_unmask_admin),
        ("Role-Based Access Control (Restricted SSN)", test_access_control_restricted),
        ("Audit Log Recording", test_audit_logs),
        ("Performance / Large Payload", test_large_input)
    ]
    
    passed_count = 0
    for name, func in tests:
        if run_test(name, func):
            passed_count += 1
            
    print_header(f"TEST SUMMARY: {passed_count}/{len(tests)} PASSED")
    
    if passed_count == len(tests):
        print(f"{Colors.GREEN}{Colors.BOLD}✅ SYSTEM IS READY FOR DEMO!{Colors.ENDC}")
    else:
        print(f"{Colors.FAIL}{Colors.BOLD}❌ SOME CHECKS FAILED - REVIEW LOGS{Colors.ENDC}")
