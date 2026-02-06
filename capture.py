import sys, json, time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options

def run_capture(name, url):
    options = Options()
    options.add_argument('--headless=new')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--disable-gpu')
    options.set_capability('goog:loggingPrefs', {'performance': 'ALL'})

    driver = None
    try:
        driver = webdriver.Chrome(options=options)
        driver.set_page_load_timeout(20)
        driver.get(url)

        found_url = None
        for _ in range(15):
            time.sleep(1)
            logs = driver.get_log('performance')
            for entry in logs:
                log_data = json.loads(entry['message'])['message']
                if log_data['method'] == 'Network.requestWillBeSent':
                    req_url = log_data['params']['request']['url']
                    if '.m3u8' in req_url and 'nbtv.cn' in req_url:
                        found_url = req_url
                        break
            if found_url: break
        
        if found_url:
            print(f"RESULT:{name}|{found_url}")
            
    except Exception as e:
        sys.stderr.write(f"Error on {name}: {str(e)}\n")
    finally:
        if driver: driver.quit()

if __name__ == "__main__":
    if len(sys.argv) > 2:
        run_capture(sys.argv[1], sys.argv[2])
