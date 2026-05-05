import requests as req
import json

# --- CONFIGURATION ---
# Use a valid Dev Firebase ID Token
header = "" # Add your Firebase ID Token here
API_BASE_URL = "http://127.0.0.1:8000"

# --- CORE FUNCTIONAL HELPERS ---

def post(link:str, payload:dict={}):
    r = req.post(
        url=f"{API_BASE_URL}{link}",
        headers={"Authorization": header, "Content-Type": "application/json"},
        data=json.dumps(payload)
    )
    print(f"POST {link} | Status: {r.status_code}")
    try:
        print(r.json())
    except:
        print(r.text)
    return r

def get(link:str):
    r = req.get(url=f"{API_BASE_URL}{link}")
    print(f"GET {link} | Status: {r.status_code}")
    try:
        print(r.json())
    except:
        print(r.text)
    return r

def put(link:str, payload:dict={}):
    r = req.put(
        url=f"{API_BASE_URL}{link}",
        headers={"Authorization": header, "Content-Type": "application/json"},
        data=json.dumps(payload)
    )
    return r

# --- BUSINESS LOGIC TASKS ---

def loop_add_timings(name:str , file:str):
    print(f"--- Processing timing file: {file} ---")
    with open(file, 'r') as f:
        times = f.readlines()
        i = 1
        for time_str in times:
            time_str = time_str.strip()
            res = put("/v1/timings/update", {
                "route_name": name,
                "timing": time_str,
                "stop": "Thane Station"
            })
            
            print(f"Entry {i}: {time_str} | Status: {res.status_code}")
            
            if res.status_code == 429:
                print(f"!! Global Rate Limit Hit at entry {i} !!")
                return # Stop processing if limited

            if i % 10 == 0:
                print(f"\nCompleted {i} entries\n")
            i += 1
    
    get(f"/v1/timings/{name}")
    print("--- Timing Sync Done ---")

# --- RATE LIMIT VERIFICATION TESTS ---

def run_rate_limit_stress_test(endpoint: str, method: str, iterations: int):
    print(f"\n>>> Stress Testing Rate Limit: {endpoint} ({iterations} iterations)")
    for i in range(1, iterations + 1):
        res = None
        if method == "POST":
            # Using empty dict for sync/test endpoints
            res = req.post(f"{API_BASE_URL}{endpoint}", headers={"Authorization": header}, json={})
        elif method == "GET":
            res = req.get(f"{API_BASE_URL}{endpoint}")
        
        if res is None:
            raise ValueError("Unsupported HTTP method for stress test.")
        
        print(f"Request {i}: {res.status_code}")
        
        if res.status_code == 429:
            print(f"SUCCESS: Rate limit (429) triggered correctly at request {i}")
            return True
    
    print("FAILURE: Rate limit was not triggered.")
    return False

# --- MAIN EXECUTION ---

if __name__ == "__main__":
    # 1. Test Strict Limit (5/minute) on User Sync
    # This proves Layer 1 (Infrastructure) protection is working
    run_rate_limit_stress_test("/v1/user/sync", "POST", iterations=10)

    # 2. Functional: Add a Route 
    # (Note: If you run this 6 times, it will hit the 429 strict limit)
    post("/v1/route/add", {
        "route_name": "156",
        "stops": ["Thane Station", "Tiku-jini-wadi"],
        "start": "Thane Station",
        "end": "Tiku-jini-wadi",
        "timing": "04:38 PM"
    })

    # 3. Functional: Bulk Add Timings
    # This tests the Global Limit (100/minute)
    loop_add_timings("156", "156.txt")