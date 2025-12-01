import logging
import sys

# Configure logging to stdout
logging.basicConfig(level=logging.INFO, stream=sys.stdout)

try:
    print("Importing PIIDetector...")
    from api.services.detection import PIIDetector
    
    print("Initializing PIIDetector...")
    detector = PIIDetector()
    
    text = """Hello, my name is Ramesh Kumar and my email is ramesh.kumar@example.in. 
    My Aadhaar number is 1234-5678-9012 and PAN is ABCDE1234F. 
    I have a HDFC credit card 4111-1111-1111-1111. 
    My IP address is 203.91.115.10 and I was born on 15-Aug-1990."""
    
    print("Running detection...")
    entities = detector.detect(text)
    
    print(f"Detected {len(entities)} entities:")
    for e in entities:
        print(f"- {e['type']}: {e['text']} ({e['score']})")
        
except Exception as e:
    print(f"CRASHED: {e}")
    import traceback
    traceback.print_exc()
