import sys
import json
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains

DRIVER_PATH = r"D:\py\chromedriver.exe"
SAVE_PATH = r"D:\py\nbtv_live.txt"

def run_capture(name, url):
    options = Options()
    options.add_argument('--headless=new') 
    options.set_capability('goog:loggingPrefs', {'performance': 'ALL'})
    
    # --- Speed & Docker Optimizations ---
    options.add_argument('--autoplay-policy=no-user-gesture-required')
    options.add_argument('--mute-audio')
    options.add_argument('--disable-gpu')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage') # Crucial for Docker stability
    options.add_argument('--blink-settings=imagesEnabled=false') # Don't load images (Faster)
    options.add_argument('--window-size=1280,720')
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36")

    try:
        service = Service(executable_path=DRIVER_PATH)
        driver = webdriver.Chrome(service=service, options=options)
        driver.get(url)
        
        # Reduced initial wait to 3s (page starts loading immediately)
        time.sleep(3) 
        
        # Simulate click
        try:
            actions = ActionChains(driver)
            actions.move_by_offset(300, 300).click().perform()
        except: pass

        # Reduced capture wait from 20s to 12s (Parallel allows more aggression)
        time.sleep(12) 

        logs = driver.get_log('performance')
        for entry in logs:
            log_data = json.loads(entry['message'])['message']
            if log_data['method'] == 'Network.requestWillBeSent':
                req_url = log_data['params']['request']['url']
                if '.m3u8' in req_url and 'nbtv.cn' in req_url:
                    with open(SAVE_PATH, "a", encoding="utf-8") as f:
                        f.write(f"{name},{req_url}\n")
                    return # Exit as soon as found
    finally:
        if 'driver' in locals():
            driver.quit()

if __name__ == "__main__":
    if len(sys.argv) > 2:
        run_capture(sys.argv[1], sys.argv[2])
