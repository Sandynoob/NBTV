import sys
import json
import time
import os
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
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36")
    options.set_capability('goog:loggingPrefs', {'performance': 'ALL'})

    try:
        # 直接使用系统路径中的驱动，避免并发下载冲突
        driver = webdriver.Chrome(options=options)
        driver.set_page_load_timeout(40)
        
        driver.get(url)
        time.sleep(25) # 给 GitHub 环境留出足够的缓冲时间

        logs = driver.get_log('performance')
        for entry in logs:
            log_data = json.loads(entry['message'])['message']
            if log_data['method'] == 'Network.requestWillBeSent':
                req_url = log_data['params']['request']['url']
                if '.m3u8' in req_url and 'auth_key=' in req_url:
                    with open(temp_file, "w", encoding="utf-8") as f:
                        f.write(f"{name},{req_url}")
                    print(f"✅ {name} 捕获成功")
                    return
        print(f"❌ {name} 未捕获到有效信号")
    except Exception as e:
        print(f"⚠️ {name} 运行报错: {e}")
    finally:
        if 'driver' in locals(): driver.quit()

if __name__ == "__main__":
    # 增加参数检查，防止 tuple index 错误
    if len(sys.argv) >= 3:
        target_name = sys.argv[1]
        target_url = sys.argv[2]
        run_capture(target_name, target_url)
    else:
        print("❌ 参数不足")
