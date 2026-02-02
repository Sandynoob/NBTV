import sys
import json
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options

# 如果在 GitHub 环境运行，请确保 requirements.txt 包含 selenium-stealth
try:
    from selenium_stealth import stealth
except ImportError:
    stealth = None

def run_capture(name, url):
    temp_file = f"{name}.tmp"
    options = Options()
    options.add_argument('--headless=new')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--mute-audio')
    
    # 1. 伪装 User-Agent 为国内常见的 Windows Chrome 版本
    ua = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    options.add_argument(f'user-agent={ua}')
    
    # 2. 尝试伪造转发 IP（部分 CDN 会参考此头部）
    # 这里的 IP 是随机选择的一个中国境内 IP 段
    options.add_argument("--proxy-server='direct://'")
    options.add_argument("--proxy-bypass-list=*")
    
    options.set_capability('goog:loggingPrefs', {'performance': 'ALL'})

    try:
        driver = webdriver.Chrome(options=options)
        
        # 3. 使用 Stealth 隐藏自动化特征 (防止被识别为无头浏览器)
        if stealth:
            stealth(driver,
                languages=["zh-CN", "zh"],
                vendor="Google Inc.",
                platform="Win32",
                webgl_vendor="Intel Inc.",
                renderer="Intel Iris OpenGL Engine",
                fix_hairline=True,
            )

        # 4. 强制覆盖地理位置（欺骗浏览器内部 API）
        # 模拟宁波市的经纬度 (29.86, 121.54)
        driver.execute_cdp_cmd("Emulation.setGeolocationOverride", {
            "latitude": 29.8683,
            "longitude": 121.5440,
            "accuracy": 100
        })

        print(f"🚀 正在伪装访问: {url}")
        driver.get(url)
        
        # 5. 延长等待时间。海外访问国内 CDN 握手极慢，需要更多缓冲
        print(f"⏳ 正在分析流量 (45秒)...")
        time.sleep(45) 

        logs = driver.get_log('performance')
        for entry in logs:
            log_data = json.loads(entry['message'])['message']
            if log_data['method'] == 'Network.requestWillBeSent':
                req_url = log_data['params']['request']['url']
                # 寻找包含鉴权的完整地址
                if '.m3u8' in req_url and 'auth_key=' in req_url:
                    with open(temp_file, "w", encoding="utf-8") as f:
                        f.write(f"{name},{req_url}")
                    print(f"✅ {name} 捕获成功")
                    return
        print(f"❌ {name} 依然无法获取信号（可能是强力 IP 封锁）")
    except Exception as e:
        print(f"⚠️ {name} 报错: {e}")
    finally:
        if 'driver' in locals(): driver.quit()

if __name__ == "__main__":
    if len(sys.argv) >= 3:
        run_capture(sys.argv[1], sys.argv[2])
