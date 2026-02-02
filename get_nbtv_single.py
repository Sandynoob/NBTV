import sys
import json
import time
import os
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains
from webdriver_manager.chrome import ChromeDriverManager

# Relative path for GitHub compatibility
SAVE_PATH = "nbtv_live.txt"

def run_capture(name, url):
    options = Options()
    options.add_argument('--headless=new') 
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--mute-audio')
    options.set_capability('goog:loggingPrefs', {'performance': 'ALL'})
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")

    driver = None
    try:
        # Automatically manages Linux ChromeDriver on GitHub
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=options)
        driver.get(url)
        
        # Wait for page elements
        time.sleep(5) 
        try:
            # Simulate interaction to trigger auth_key
            ActionChains(driver).move_by_offset(100, 100).click().perform()
        except:
            pass

        # Wait for network requests (GitHub network is slower)
        time.sleep(25) 

        logs = driver.get_log('performance')
        for entry in logs:
            log_data = json.loads(entry['message'])['message']
            if log_data['method'] == 'Network.requestWillBeSent':
                req_url = log_data['params']['request']['url']
                # Match m3u8 and ensure it's from the correct domain
                if '.m3u8' in req_url and 'nbtv.cn' in req_url:
                    with open(SAVE_PATH, "a", encoding="utf-8") as f:
                        f.write(f"{name},{req_url}\n")
                    print(f"✅ {name} SUCCESS")
                    return
        print(f"❌ {name} FAILED: No m3u8 found in logs")
    except Exception as e:
        print(f"⚠️ {name} ERROR: {e}")
    finally:
        if driver:
            driver.quit()

if __name__ == "__main__":
    # Fix: sys.argv[1] is Name, sys.argv[2] is URL
    if len(sys.argv) >= 3:
        run_capture(sys.argv[1], sys.argv[2])
    else:
        print("❌ Error: Missing arguments")
