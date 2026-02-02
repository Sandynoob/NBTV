import subprocess
import time
import os

# GitHub Uses 'python'
PYTHON_EXE = "python"
TASK_SCRIPT = "get_nbtv_single.py"
TXT_PATH = "nbtv_live.txt"
M3U_PATH = "nbtv_live.m3u"

channels = [
    {"name": "NBTV1-新闻综合", "url": "https://www.ncmc.nbtv.cn/gbds/folder8458/NBTV1/index.shtml"},
    {"name": "NBTV2-经济生活", "url": "https://www.ncmc.nbtv.cn/gbds/folder8458/NBTV2/index.shtml"},
    {"name": "NBTV3-都市文体", "url": "https://www.ncmc.nbtv.cn/gbds/folder8458/NBTV3/index.shtml"},
    {"name": "NBTV4-影视剧", "url": "https://www.ncmc.nbtv.cn/gbds/folder8458/NBTV4/index.shtml"},
]

def convert_to_m3u():
    if not os.path.exists(TXT_PATH):
        print("⚠️ No results to convert.")
        return
    
    with open(TXT_PATH, "r", encoding="utf-8") as txt:
        lines = txt.readlines()
    
    with open(M3U_PATH, "w", encoding="utf-8") as m3u:
        m3u.write("#EXTM3U\n")
        for line in lines:
            if "," in line:
                name, url = line.strip().split(",", 1)
                m3u.write(f"#EXTINF:-1,{name}\n{url}\n")
    print(f"✨ M3U File Generated: {M3U_PATH}")

if __name__ == "__main__":
    # Cleanup old files
    if os.path.exists(TXT_PATH): os.remove(TXT_PATH)
    
    start_time = time.time()
    print("🚀 Starting Parallel Scraper...")
    
    processes = []
    for ch in channels:
        # Launch independent processes
        p = subprocess.Popen([PYTHON_EXE, TASK_SCRIPT, ch['name'], ch['url']])
        processes.append(p)
        time.sleep(1) # Small stagger for stability

    # Wait for all processes to finish
    for p in processes:
        p.wait()

    # Convert TXT to M3U
    convert_to_m3u()
    print(f"⏱️ Finished in {round(time.time() - start_time, 2)}s")
