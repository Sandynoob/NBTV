import sys
import json
import time
import os
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

# 必须使用相对路径，不能带 D:\py\
SAVE_PATH = "nbtv_live.txt"

def run_capture(name, url):
    # 提前创建文件，防止 Git 找不到文件而报错
    if not os.path.exists(SAVE_PATH):
        with open(SAVE_PATH, 'a') as f: pass

    options = Options()
    options.add_argument('--headless=new') 
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage') # Linux 容器必须加这个
    options.add_argument('--mute-audio')
    options.set_capability('goog:loggingPrefs', {'performance': 'ALL'})
    # 模拟标准的 Linux Chrome 用户代理
    options.add_argument("user-agent=Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")

    try:
        # 自动安装 Linux 版驱动
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=options)
        driver.get(url)
        
        # 增加等待时间，适应 GitHub 的慢速网络
        print(f"正在抓取 {name}，请稍候...")
        time.sleep(25) 

        logs = driver.get_log('performance')
        for entry in logs:
            log_data = json.loads(entry['message'])['message']
            if log_data['method'] == 'Network.requestWillBeSent':
                req_url = log_data['params']['request']['url']
                if '.m3u8' in req_url and 'ncmc.nbtv.cn' in req_url:
                    with open(SAVE_PATH, "a", encoding="utf-8") as f:
                        f.write(f"{name},{req_url}\n")
                    print(f"✅ 捕获成功: {name}")
                    return
        print(f"❌ 捕获失败: {name}")
    except Exception as e:
        print(f"⚠️ 运行出错: {e}")
    finally:
        if 'driver' in locals(): driver.quit()

if __name__ == "__main__":
    if len(sys.argv) > 2:
        run_capture(sys.argv[1], sys.argv[2])
