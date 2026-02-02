import sys
import json
import time
import os
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains

# ❗ 请确保此路径与你本地匹配
DRIVER_PATH = r"D:\py\chromedriver.exe"
# 临时存放 TXT，主脚本会汇总它
SAVE_PATH = r"D:\py\nbtv_live.txt"

def run_capture(name, url):
    options = Options()
    options.add_argument('--headless=new') 
    options.set_capability('goog:loggingPrefs', {'performance': 'ALL'})
    
    options.add_argument('--autoplay-policy=no-user-gesture-required')
    options.add_argument('--mute-audio')
    options.add_argument('--disable-gpu')
    options.add_argument('--no-sandbox')
    options.add_argument('--blink-settings=imagesEnabled=false')
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")

    try:
        service = Service(executable_path=DRIVER_PATH)
        driver = webdriver.Chrome(service=service, options=options)
        driver.get(url)
        
        # 等待加载并模拟点击
        time.sleep(5) 
        try:
            ActionChains(driver).move_by_offset(300, 300).click().perform()
        except: pass

        # 给播放器足够的时间获取带 auth_key 的链接
        time.sleep(15) 

        logs = driver.get_log('performance')
        for entry in logs:
            log_data = json.loads(entry['message'])['message']
            if log_data['method'] == 'Network.requestWillBeSent':
                req_url = log_data['params']['request']['url']
                # 优先匹配带 auth_key 的链接
                if '.m3u8' in req_url and 'ncmc.nbtv.cn' in req_url:
                    with open(SAVE_PATH, "a", encoding="utf-8") as f:
                        f.write(f"{name},{req_url}\n")
                    print(f"✅ {name} 捕获成功")
                    return
        print(f"❌ {name} 未捕获到信号")
    finally:
        if 'driver' in locals(): driver.quit()

if __name__ == "__main__":
    if len(sys.argv) > 2:
        run_capture(sys.argv[1], sys.argv[2])
