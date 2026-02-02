import sys
import json
import time
import os
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

def run_capture(name, url):
    # 为每个频道创建独立的临时文件，避免写入冲突
    temp_file = f"{name}.tmp"
    
    options = Options()
    options.add_argument('--headless=new')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--mute-audio')
    # 模拟 Windows 用户代理，减少被拦截风险
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36")
    options.set_capability('goog:loggingPrefs', {'performance': 'ALL'})

    try:
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=options)
        driver.set_page_load_timeout(40) # 增加超时时间
        
        print(f"🚀 正在访问: {url}")
        driver.get(url)
        
        # 模拟点击和滚动
        time.sleep(5)
        driver.execute_script("window.scrollTo(0, 400);")
        
        # 监控流量 (30秒)
        print(f"⏳ {name} 正在搜寻带 auth_key 的信号...")
        time.sleep(30) 

        logs = driver.get_log('performance')
        m3u8_url = None
        
        for entry in logs:
            log_data = json.loads(entry['message'])['message']
            if log_data['method'] == 'Network.requestWillBeSent':
                req_url = log_data['params']['request']['url']
                # 捕获包含 auth_key 的完整 m3u8 链接
                if '.m3u8' in req_url and 'auth_key=' in req_url:
                    m3u8_url = req_url
                    break

        if m3u8_url:
            # 写入临时文件
            with open(temp_file, "w", encoding="utf-8") as f:
                f.write(f"{name},{m3u8_url}")
            print(f"✅ {name} 捕获成功")
        else:
            print(f"❌ {name} 捕获失败 (未找到带鉴权的链接)")

    except Exception as e:
        print(f"⚠️ {name} 运行报错: {e}")
    finally:
        if 'driver' in locals(): driver.quit()

if __name__ == "__main__":
    if len(sys.argv) > 2:
        run_capture(sys.argv[1], sys.argv[2])
