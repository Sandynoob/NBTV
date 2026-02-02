import subprocess
import time
import os

# --- 配置 ---
PYTHON_EXE = "python"
TASK_SCRIPT = r"D:\py\get_nbtv_single.py"
TXT_PATH = r"D:\py\nbtv_live.txt"
M3U_PATH = r"D:\py\nbtv_live.m3u"

channels = [
    {"name": "NBTV1-新闻综合", "url": "https://www.ncmc.nbtv.cn/gbds/folder8458/NBTV1/index.shtml"},
    {"name": "NBTV2-经济生活", "url": "https://www.ncmc.nbtv.cn/gbds/folder8458/NBTV2/index.shtml"},
    {"name": "NBTV3-都市文体", "url": "https://www.ncmc.nbtv.cn/gbds/folder8458/NBTV3/index.shtml"},
    {"name": "NBTV4-影视剧", "url": "https://www.ncmc.nbtv.cn/gbds/folder8458/NBTV4/index.shtml"},
]

def convert_to_m3u():
    """将捕获成功的 TXT 转换为 M3U 格式"""
    if not os.path.exists(TXT_PATH):
        print("❌ 未找到 TXT 结果文件，无法转换 M3U。")
        return

    try:
        with open(TXT_PATH, "r", encoding="utf-8") as txt_file:
            lines = txt_file.readlines()
        
        with open(M3U_PATH, "w", encoding="utf-8") as m3u_file:
            m3u_file.write("#EXTM3U\n")
            for line in lines:
                if "," in line:
                    name, url = line.strip().split(",", 1)
                    m3u_file.write(f"#EXTINF:-1,{name}\n")
                    m3u_file.write(f"{url}\n")
        print(f"✨ M3U 文件转换成功: {M3U_PATH}")
    except Exception as e:
        print(f"❌ 转换过程出错: {e}")

if __name__ == "__main__":
    # 1. 清理旧文件
    if os.path.exists(TXT_PATH): os.remove(TXT_PATH)
    if os.path.exists(M3U_PATH): os.remove(M3U_PATH)
    
    start_time = time.time()
    print("🚀 启动并行抓取任务...")
    
    # 2. 启动并发进程
    processes = []
    for ch in channels:
        p = subprocess.Popen([PYTHON_EXE, TASK_SCRIPT, ch['name'], ch['url']])
        processes.append(p)
        time.sleep(0.5)

    # 3. 等待所有进程结束
    for p in processes:
        p.wait()

    # 4. 执行转换步骤
    print("\n--- 正在生成 M3U 播放列表 ---")
    convert_to_m3u()

    print(f"\n⏱️ 总耗时: {round(time.time() - start_time, 2)} 秒")
