import subprocess
import time
import os
from webdriver_manager.chrome import ChromeDriverManager

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

def main():
    print("--- 预下载驱动防止并发冲突 ---")
    # 关键：在这里先运行一次，确保所有子进程共享已下载好的驱动
    ChromeDriverManager().install()

    processes = []
    for ch in channels:
        print(f"🚀 启动任务: {ch['name']}")
        # 显式传递参数，并用引号包裹防止 URL 里的特殊字符截断
        p = subprocess.Popen([PYTHON_EXE, TASK_SCRIPT, ch['name'], ch['url']])
        processes.append(p)
        time.sleep(3) # 错开启动时间

    for p in processes:
        p.wait()

    # 合并逻辑保持不变...
    results = []
    for ch in channels:
        tmp_file = f"{ch['name']}.tmp"
        if os.path.exists(tmp_file):
            with open(tmp_file, "r", encoding="utf-8") as f:
                results.append(f.read().strip())
            os.remove(tmp_file)

    if results:
        with open(TXT_PATH, "w", encoding="utf-8") as f:
            f.write("\n".join(results))
        with open(M3U_PATH, "w", encoding="utf-8") as f:
            f.write("#EXTM3U\n")
            for item in results:
                name, url = item.split(",", 1)
                f.write(f"#EXTINF:-1,{name}\n{url}\n")
        print(f"✨ 成功合并 {len(results)} 个频道")

if __name__ == "__main__":
    main()


