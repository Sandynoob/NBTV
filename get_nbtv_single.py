import sys
import json
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By

def run_capture(name, url):
    temp_file = f"{name}.tmp"
    options = Options()
    options.add_argument('--headless=new')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--mute-audio')
    # 模拟移动端，移动端网页通常鉴权更宽松，且加载更快
    options.add_argument("user-agent=Mozilla/5.0 (iPhone; CPU iPhone OS 16_3 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.3 Mobile/15E148 Safari/604.1")
    options.set_capability('goog:loggingPrefs', {'performance': 'ALL'})

    try:
        driver = webdriver.Chrome(options=options)
        print(f"🚀 尝试激活: {url}")
        driver.get(url)
        
        # --- 暴力激活步骤 ---
        time.sleep(10)
        
        # 1. 模拟点击页面所有可能的播放位置 (强制触发 JS 逻辑)
        driver.execute_script("""
            var clickEvent = new MouseEvent('click', { 'view': window, 'bubbles': True, 'cancelable': True });
            document.querySelectorAll('div, video, canvas').forEach(el => el.dispatchEvent(clickEvent));
        """)
        
        # 2. 模拟播放器所需的 resize 事件
        driver.execute_script("window.dispatchEvent(new Event('resize'));")
        
        # 3. 循环检查流量 (每 5 秒查一次，直到抓到或超时)
        print(f"⏳ 正在深度监控流量 (最高 60 秒)...")
        found = False
        for _ in range(12): 
            time.sleep(5)
            logs = driver.get_log('performance')
            for entry in logs:
                msg = json.loads(entry['message'])['message']
                if msg['method'] == 'Network.requestWillBeSent':
                    req_url = msg['params']['request']['url']
                    # 只要包含 m3u8，不论带不带 key 先记录下来，看看区别
                    if '.m3u8' in req_url and 'ncmc.nbtv.cn' in req_url:
                        with open(temp_file, "w", encoding="utf-8") as f:
                            f.write(f"{name},{req_url}")
                        print(f"✅ 捕获到链接: {req_url[:60]}...")
                        if 'auth_key=' in req_url:
                            print("✨ 完美！抓到了带 Token 的链接")
                            return
                        found = True # 抓到了但不带 key，继续找更好的
            if found and _ > 6: break # 如果抓到了普通的且等了很久还没带 key 的，就收工
            
        if not found:
            print(f"❌ {name} 彻底无信号")

    except Exception as e:
        print(f"⚠️ 报错: {e}")
    finally:
        if 'driver' in locals(): driver.quit()

if __name__ == "__main__":
    if len(sys.argv) >= 3:
        run_capture(sys.argv[1], sys.argv[2])
