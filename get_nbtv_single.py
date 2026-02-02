import sys
import json
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options

def run_capture(name, url):
    temp_file = f"{name}.tmp"
    options = Options()
    options.add_argument('--headless=new')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--mute-audio')
    # Use a more realistic browser fingerprint
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36")
    options.set_capability('goog:loggingPrefs', {'performance': 'ALL'})

    try:
        # We assume Chrome is already in the PATH on Ubuntu
        driver = webdriver.Chrome(options=options)
        driver.set_page_load_timeout(60) # Increase timeout for slow international connection
        
        driver.get(url)
        # Some players need a physical interaction; simulate a scroll
        driver.execute_script("window.scrollBy(0, 100);")
        
        # INCREASE wait time to 40s to allow for slow CDN handshake
        print(f"Waiting 40s for {name} to resolve...")
        time.sleep(40) 

        logs = driver.get_log('performance')
        for entry in logs:
            log_data = json.loads(entry['message'])['message']
            if log_data['method'] == 'Network.requestWillBeSent':
                req_url = log_data['params']['request']['url']
                # Search specifically for auth_key which is required for NBTV playback
                if '.m3u8' in req_url and 'auth_key=' in req_url:
                    with open(temp_file, "w", encoding="utf-8") as f:
                        f.write(f"{name},{req_url}")
                    print(f"✅ {name} SUCCESS")
                    return
        print(f"❌ {name} NO SIGNAL FOUND")
    except Exception as e:
        print(f"⚠️ {name} ERROR: {e}")
    finally:
        if 'driver' in locals(): driver.quit()

if __name__ == "__main__":
    if len(sys.argv) >= 3:
        run_capture(sys.argv[1], sys.argv[2])
