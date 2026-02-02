import subprocess
import time
import os

# Linux uses 'python3' or 'python'
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
    if not os.path.exists(TXT_PATH): return
    with open(TXT_PATH, "r", encoding="utf-8") as txt_file:
        lines = txt_file.readlines()
    with open(M3U_PATH, "w", encoding="utf-8") as m3u_file:
        m3u_file.write("#EXTM3U\n")
        for line in lines:
            if "," in line:
                name, url = line.strip().split(",", 1)
                m3u_file.write(f"#EXTINF:-1,{name}\n")
                m3u_file.write(f"{url}\n")

if __name__ == "__main__":
    if os.path.exists(TXT_PATH): os.remove(TXT_PATH)
    processes = []
    for ch in channels:
        p = subprocess.Popen([PYTHON_EXE, TASK_SCRIPT, ch['name'], ch['url']])
        processes.append(p)
        time.sleep(1)
    for p in processes:
        p.wait()
    convert_to_m3u()
