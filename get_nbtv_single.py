import sys
import json
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains
from webdriver_manager.chrome import ChromeDriverManager

# 结果保存路径
SAVE_PATH = "nbtv_live.txt"

def run_capture(name, url):
    options = Options()
    options.add_argument('--headless=new') 
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--mute-audio')
    # 模拟真实的浏览器指纹，增加鉴权成功率
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
    options.set_capability('goog:loggingPrefs', {'performance': 'ALL'})

    driver = None
    try:
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=options)
        driver.set_page_load_timeout(30)
        
        print(f"🚀 正在处理: {name} -> {url}")
        driver.get(url)
        
        # 1. 给页面一点基础加载时间
        time.sleep(8) 
        
        # 2. 模拟人为操作：点击播放器中心以触发 JS 鉴权
        try:
            actions = ActionChains(driver)
            # 点击页面中心位置 (通常是播放器所在处)
            actions.move_by_offset(600, 400).click().perform()
            # 模拟微量滚动
            driver.execute_script("window.scrollBy(0, 100);")
        except:
            pass

        # 3. 延长监控时间。NBTV 的 Token 通常在播放器握手完成后生成
        print(f"   [监控中] 等待带 auth_key 的信号弹出 (30秒)...")
        time.sleep(30) 

        logs = driver.get_log('performance')
        m3u8_url = None
        
        for entry in logs:
            log_data = json.loads(entry['message'])['message']
            if log_data['method'] == 'Network.requestWillBeSent':
                req_url = log_data['params']['request']['url']
                
                # 核心过滤：必须包含 .m3u8 且包含 auth_key
                if '.m3u8' in req_url and 'auth_key=' in req_url:
                    # 额外校验是否属于 NBTV 域名，排除第三方统计干扰
                    if 'ncmc.nbtv.cn' in req_url or 'liveplay8.nbtv.cn' in req_url:
                        m3u8_url = req_url
                        break

        if m3u8_url:
            with open(SAVE_PATH, "a", encoding="utf-8") as f:
                f.write(f"{name},{m3u8_url}\n")
            print(f"✅ 捕获成功: {name}")
        else:
            print(f"❌ 捕获失败: {name} (未发现带鉴权的链接)")

    except Exception as e:
        print(f"⚠️ 运行报错: {e}")
    finally:
        if driver:
            driver.quit()

if __name__ == "__main__":
    if len(sys.argv) >= 3:
        run_capture(sys.argv[1], sys.argv[2])
