import sys
import json
import time
import os
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains
from webdriver_manager.chrome import ChromeDriverManager

SAVE_PATH = "nbtv_live.txt"

def run_capture(name, url):
    options = Options()
    options.add_argument('--headless=new') 
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage') # Linux 必须：防止内存崩溃
    options.add_argument('--mute-audio')
    options.set_capability('goog:loggingPrefs', {'performance': 'ALL'})
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")

    driver = None
    try:
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=options)
        # 设置页面加载超时，防止永久卡死
        driver.set_page_load_timeout(40)
        
        driver.get(url)
        time.sleep(5) 
        
        try:
            # 尝试点击页面激活播放器
            ActionChains(driver).move_by_offset(100, 100).click().perform()
        except:
            pass

        # 等待流量生成
        print(f"   [子进程] 正在分析 {name} 的网络包...")
        time.sleep(25) 

        logs = driver.get_log('performance')
        for entry in logs:
            log_data = json.loads(entry['message'])['message']
            if log_data['method'] == 'Network.requestWillBeSent':
                req_url = log_data['params']['request']['url']
                # 寻找带 auth_key 的完整 m3u8
                if '.m3u8' in req_url and 'nbtv.cn' in req_url:
                    with open(SAVE_PATH, "a", encoding="utf-8") as f:
                        f.write(f"{name},{req_url}\n")
                    print(f"✅ {name} 捕获成功")
                    return
        print(f"❌ {name} 捕获失败: 未发现链接")
    except Exception as e:
        print(f"⚠️ {name} 报错: {e}")
    finally:
        if driver:
            driver.quit()

if __name__ == "__main__":
    if len(sys.argv) >= 3:
        run_capture(sys.argv[1], sys.argv[2])
