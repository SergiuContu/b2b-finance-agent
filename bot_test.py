import requests
import time

# Target the rate-limited endpoint
TARGET_URL = "http://127.0.0.1:8000/ask"
PAYLOAD = {"question": "What is the maximum advance limit for a B2B Merchant Cash Advance?"}

print("Initiating simulated bot attack...\n")

# Fire 8 rapid requests (Limit is 5 per minute)
for i in range(1, 9):
    print(f"Firing Request {i}...")
    response = requests.post(TARGET_URL, json=PAYLOAD)
    
    if response.status_code == 200:
        print(f" [VULNERABLE] Status {response.status_code}: Server processed the request and incurred AWS costs.")
    elif response.status_code == 429:
        print(f" [SECURE] Status {response.status_code}: Rate Limiter actively blocked the request.")
    elif response.status_code == 422:
        print(f" [BLOCKED] Status {response.status_code}: Pydantic validation rejected the payload size.")
    else:
        print(f" [ERROR] Status {response.status_code}: {response.text}")
        
    time.sleep(0.5) # Half-second delay between strikes