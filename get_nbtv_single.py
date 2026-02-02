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
    # 预创建文件防止报错
    if not os.path.exists(SAVE_PATH):
        open(SAVE_PATH, 'a').close()

    options = Options()
    options.add_argument('--headless=new')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--disable-gpu')
    options.add_argument('--mute-audio')
    # 核心：伪装成 Windows 用户，防止被识别为 Linux 爬虫
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
    options.set_capability('goog:loggingPrefs', {'performance': 'ALL'})

    try:
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=options)
        # 设置页面加载超时
        driver.set_page_load_timeout(30)
        
        print(f"🚀 正在访问: {url}")
        driver.get(url)
        
        # 1. 模拟滚动，让懒加载元素生效
        driver.execute_script("window.scrollTo(0, 500);")
        time.sleep(5)
        
        # 2. 模拟点击播放器位置 (强制激活播放器)
        print("🖱️ 正在模拟点击播放器...")
        try:
            actions = ActionChains(driver)
            actions.move_by_offset(640, 360).click().perform()
        except:
            pass
        
        # 3. 增加等待时间，GitHub 的海外网络访问国内站较慢
        print("⏳ 正在监控网络流量 (30秒)...")
        time.sleep(30) 

        logs = driver.get_log('performance')
        m3u8_url = None
        
        for entry in logs:
            log_data = json.loads(entry['message'])['message']
            if log_data['method'] == 'Network.requestWillBeSent':
                req_url = log_data['params']['request']['url']
                # 精确匹配，排除广告干扰
                if '.m3u8' in req_url and ('ncmc.nbtv.cn' in req_url or 'nbtv.cn' in req_url):
                    m3u8_url = req_url
                    break

        if m3u8_url:
            with open(SAVE_PATH, "a", encoding="utf-8") as f:
                f.write(f"{name},{m3u8_url}\n")
            print(f"✅ 捕获成功: {name}")
        else:
            print(f"❌ 捕获失败: {name}")

    except Exception as e:
        print(f"⚠️ 报错: {e}")
    finally:
        if 'driver' in locals(): driver.quit()

if __name__ == "__main__":
    if len(sys.argv) > 2:
        run_capture(sys.argv[1], sys.argv[2])
