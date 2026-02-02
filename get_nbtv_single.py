import sys
import json
import time
import os
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options

SAVE_PATH = "nbtv_live.txt"

def run_capture(name, url):
    # 确保文件夹里先有个文件
    if not os.path.exists(SAVE_PATH):
        with open(SAVE_PATH, 'w') as f: pass

    options = Options()
    options.add_argument('--headless=new')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--mute-audio')
    # 尝试使用移动端 UA，有时移动端接口对海外 IP 稍微宽松一点
    options.add_argument("user-agent=Mozilla/5.0 (iPhone; CPU iPhone OS 16_3 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.3 Mobile/15E148 Safari/604.1")
    options.set_capability('goog:loggingPrefs', {'performance': 'ALL'})

    try:
        driver = webdriver.Chrome(options=options)
        driver.set_page_load_timeout(60)
        driver.get(url)
        
        # 模拟点击和滚动，激活 JS
        time.sleep(10)
        driver.execute_script("window.scrollBy(0, 300);")
        
        # 增加循环检测，因为海外加载极慢
        print(f"   [监控中] 正在深度扫描网络包 (60秒)...")
        found = False
        for i in range(12): # 循环 12 次，每次 5 秒
            time.sleep(5)
            logs = driver.get_log('performance')
            for entry in logs:
                msg = json.loads(entry['message'])['message']
                if msg['method'] == 'Network.requestWillBeSent':
                    req_url = msg['params']['request']['url']
                    # 只要发现 m3u8，无论带不带 key 都记录下来对比
                    if '.m3u8' in req_url and 'nbtv' in req_url:
                        with open(SAVE_PATH, "a", encoding="utf-8") as f:
                            f.write(f"{name},{req_url}\n")
                        print(f"✅ {name} 捕获到链接 (检查日志看是否带key)")
                        found = True
                        if 'auth_key=' in req_url: return # 抓到带 key 的直接退出
            if found and i > 4: break # 如果抓到了普通的且等了 30 秒还没带 key 的，也结束

        if not found: print(f"❌ {name} 彻底无信号")
    except Exception as e:
        print(f"⚠️ 报错: {e}")
    finally:
        if 'driver' in locals(): driver.quit()

if __name__ == "__main__":
    if len(sys.argv) >= 3:
        run_capture(sys.argv[1], sys.argv[2])
