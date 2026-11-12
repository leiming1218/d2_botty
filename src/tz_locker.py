import ctypes
import time
from datetime import datetime
import argparse

# Windows API 結構
class SYSTEMTIME(ctypes.Structure):
    _fields_ = [
    ("wYear", ctypes.c_ushort), ("wMonth", ctypes.c_ushort),
    ("wDayOfWeek", ctypes.c_ushort), ("wDay", ctypes.c_ushort),
    ("wHour", ctypes.c_ushort), ("wMinute", ctypes.c_ushort),
    ("wSecond", ctypes.c_ushort), ("wMilliseconds", ctypes.c_ushort),
    ]

def set_custom_time(hour, minute):
    """將系統時間設定為：今天的日期 + 指定的小時:分鐘"""
    now = datetime.now()
    st = SYSTEMTIME()
    st.wYear = now.year
    st.wMonth = now.month
    st.wDay = now.day
    st.wHour = hour
    st.wMinute = minute
    st.wSecond = 0
    st.wMilliseconds = 0

    if not ctypes.windll.kernel32.SetLocalTime(ctypes.byref(st)):
        print("設定失敗！請確保以管理員權限運行。")
        return False
    return True
def check_time_and_update(target_hour, target_minute, threshold_mins):
    now = datetime.now()
    # 計算當前分鐘與目標分鐘的差距（簡單邏輯：只看當前小時內的偏移）
    # 如果小時不對，或者分鐘偏移超過閾值
    current_offset = (now.hour - target_hour) * 60 + (now.minute - target_minute)

    if current_offset >= threshold_mins or current_offset < 0:
        set_custom_time(target_hour, target_minute)
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 誤差過大，已重置回 {target_hour:02d}:{target_minute:02d}")
    else:
        print(f"[{datetime.now().strftime('%H:%M:%S')}] 目前偏移 {current_offset} 分鐘，運行正常...", end="\r")
    

def lock_tz_smart(target_hour, target_minute, threshold_mins=20):
    """
    target_hour/minute: 你想鎖定的 TZ 起始時間 (例如 7, 5)
    threshold_mins: 允許流逝的分鐘數，超過則重置
    """
    print(f"--- 智能日期同步 TZ 鎖定 ---")
    print(f"目標鎖定時間: {target_hour:02d}:{target_minute:02d}")
    print(f"重置閾值: {threshold_mins} 分鐘")

    # 啟動時先執行一次設定
    set_custom_time(target_hour, target_minute)

    try:
        while True:
            check_time_and_update(target_hour, target_minute)

            # 每 60 秒檢查一次即可，不占用資源
            time.sleep(60)

    except KeyboardInterrupt:
        print("\n已停止鎖定。請記得在 Windows 設定中點擊『立即同步』恢復正常時間。")

if __name__ == "__main__":
    # 假設你想刷 10:30 開始的「塔·拉夏古墓」
    # 設定 target_hour=10, target_minute=5 (留5分鐘緩衝)
    # eldretch tz time period: 3:00 to 3:30

    #Disable TZ time adjustment.
    '''
    # Create the parser
    parser = argparse.ArgumentParser(description="Process two parameters.")

    # Add arguments
    parser.add_argument("hour", type=int, help="Given hour")
    parser.add_argument("min", type=int, help="Given minitue")

    # Parse the arguments
    args = parser.parse_args()

    lock_tz_smart(target_hour=args.hour, target_minute=args.min, threshold_mins=20)
    '''
