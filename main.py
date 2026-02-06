import subprocess, time, os
from concurrent.futures import ThreadPoolExecutor

CHANNELS = [
    {"name": "NBTV1-新闻综合", "url": "https://www.ncmc.nbtv.cn/gbds/folder8458/NBTV1/index.shtml"},
    {"name": "NBTV2-经济生活", "url": "https://www.ncmc.nbtv.cn/gbds/folder8458/NBTV2/index.shtml"},
    {"name": "NBTV3-都市文体", "url": "https://www.ncmc.nbtv.cn/gbds/folder8458/NBTV3/index.shtml"},
    {"name": "NBTV4-影视剧", "url": "https://www.ncmc.nbtv.cn/gbds/folder8458/NBTV4/index.shtml"},
]

M3U_PATH = "nbtv_live.m3u"

def worker(ch):
    cmd = ["python", "capture.py", ch['name'], ch['url']]
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=40)
        for line in result.stdout.splitlines():
            if "RESULT:" in line:
                return line.replace("RESULT:", "").strip()
    except subprocess.TimeoutExpired:
        print(f"⚠️ 任務超時: {ch['name']}")
    except: pass
    return None

if __name__ == "__main__":
    print("🚀 群暉 Docker 抓取任務啟動...")
    start_time = time.time()
    
    with ThreadPoolExecutor(max_workers=4) as executor:
        results = list(filter(None, executor.map(worker, CHANNELS)))

    with open(M3U_PATH, "w", encoding="utf-8") as f:
        f.write("#EXTM3U\n")
        for res in results:
            name, url = res.split("|")
            f.write(f"#EXTINF:-1,{name}\n{url}\n")
    
    print(f"✅ 完成！共抓取 {len(results)} 個頻道，耗時 {round(time.time()-start_time, 2)}s")
