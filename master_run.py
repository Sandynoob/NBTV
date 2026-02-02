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

def convert_to_m3u():
    if not os.path.exists(TXT_PATH):
        print("⚠️ 未发现 TXT 结果文件。")
        return
    with open(TXT_PATH, "r", encoding="utf-8") as txt:
        lines = txt.readlines()
    with open(M3U_PATH, "w", encoding="utf-8") as m3u:
        m3u.write("#EXTM3U\n")
        for line in lines:
            if "," in line:
                name, url = line.strip().split(",", 1)
                m3u.write(f"#EXTINF:-1,{name}\n{url}\n")
    print(f"✨ M3U 文件已生成: {M3U_PATH}")

if __name__ == "__main__":
    if os.path.exists(TXT_PATH): os.remove(TXT_PATH)
    
    start_time = time.time()
    print("🚀 启动串行抓取任务 (确保稳定性)...")
    
    for ch in channels:
        print(f"\n🎬 正在处理: {ch['name']}...")
        # 使用 subprocess.run 确保当前进程结束后才开始下一个
        subprocess.run([PYTHON_EXE, TASK_SCRIPT, ch['name'], ch['url']])
        # 间隔 2 秒释放资源
        time.sleep(2)

    # 转换结果
    convert_to_m3u()
    print(f"\n⏱️ 总耗时: {round(time.time() - start_time, 2)}s")

