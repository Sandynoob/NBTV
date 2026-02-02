import subprocess
import time
import os

# GitHub 环境下直接用 python
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

if __name__ == "__main__":
    if os.path.exists(TXT_PATH): os.remove(TXT_PATH)
    
    print("--- 启动并行抓取 ---")
    processes = []
    for ch in channels:
        p = subprocess.Popen([PYTHON_EXE, TASK_SCRIPT, ch['name'], ch['url']])
        processes.append(p)
        time.sleep(2) # 稍微错开启动时间，降低 CPU 负载

    for p in processes:
        p.wait()

    # 转换 M3U
    if os.path.exists(TXT_PATH):
        with open(TXT_PATH, "r", encoding="utf-8") as txt:
            lines = txt.readlines()
        with open(M3U_PATH, "w", encoding="utf-8") as m3u:
            m3u.write("#EXTM3U\n")
            for line in lines:
                if "," in line:
                    name, url = line.strip().split(",", 1)
                    m3u.write(f"#EXTINF:-1,{name}\n{url}\n")
        print("--- M3U 转换完成 ---")
    else:
        print("--- 抓取彻底失败，未生成 TXT ---")

