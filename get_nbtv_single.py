import sys
import json
import time
import os
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

# Remove D:\py\ - Use current directory for GitHub
SAVE_PATH = "nbtv_live.txt"

def run_capture(name, url):
    options = Options()
    options.add_argument('--headless=new') 
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage') # Required for Docker/Linux
    options.set_capability('goog:loggingPrefs', {'performance': 'ALL'})
    options.add_argument('--autoplay-policy=no-user-gesture-required')
    options.add_argument('--mute-audio')
    options.add_argument('--blink-settings=imagesEnabled=false')
    options.add_argument("user-agent=Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")

    try:
        # Automatically installs the correct Linux driver
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
        driver.get(url)
        time.sleep(18) 

        logs = driver.get_log('performance')
        for entry in logs:
            log_data = json.loads(entry['message'])['message']
            if log_data['method'] == 'Network.requestWillBeSent':
                req_url = log_data['params']['request']['url']
                if '.m3u8' in req_url and 'ncmc.nbtv.cn' in req_url:
                    with open(SAVE_PATH, "a", encoding="utf-8") as f:
                        f.write(f"{name},{req_url}\n")
                    print(f"✅ Captured: {name}")
                    return
    finally:
        if 'driver' in locals(): driver.quit()

if __name__ == "__main__":
    if len(sys.argv) > 2:
        run_capture(sys.argv[1], sys.argv[2])
