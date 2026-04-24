import time
import os
import threading
from ctypes import *

from ssjjscript.GetInfo import *
from keyboard import *
from ssjjscript.BasicsFunction import *
from mouse import *

# ======================
# 全局停止标志（线程安全）
# ======================
stop_flag = False

# ======================
# 鼠标绝对坐标
# ======================
user32 = windll.user32

class POINT(Structure):
    _fields_ = [("x", c_long), ("y", c_long)]

def _get_absolute_pos():
    pt = POINT()
    user32.GetCursorPos(byref(pt))
    return pt.x, pt.y

# ======================
# 中断监听线程
# ======================
def _stop_listener():
    global stop_flag
    while not stop_flag:
        if is_pressed('alt + i'):
            print("\n[中断] 收到停止信号")
            stop_flag = True
            break
        time.sleep(0.02)

# ======================
# 自动生成文件名
# ======================
def _create_record_filename():
    index = 1
    while True:
        timestr = time.strftime("%Y%m%d_%H%M%S")
        filename = f"record_{index}_{timestr}.txt"
        if not os.path.exists(filename):
            return filename
        index += 1

# ======================
# 配置
# ======================
INTERVAL = 1 / 50

# ======================
# 录制主函数
# ======================
def start_record():
    """
    进行录制
    |:param filename: record_1_20260424_175845
    |录制_1号_年月日_今日具体时间
    |:return: nothing
    """
    global stop_flag
    stop_flag = False  # 重置标志

    RECORD_FILE = _create_record_filename()



    # 启动中断监听线程
    threading.Thread(target=_stop_listener, daemon=True).start()

    # 起始位置
    start_x, start_y = _get_absolute_pos()
    with open(RECORD_FILE, "w", encoding="utf-8") as f:
        f.write(f"START_POS                      {start_x} {start_y}\n")

    print(f"开始录制 → 文件：{RECORD_FILE}")
    print("按 alt + i 停止")

    last = time.time()
    last_x, last_y = _get_absolute_pos()  # 初始坐标

    # ======================
    # 主录制循环
    # ======================
    while not stop_flag:
        now = time.time()
        if now - last < INTERVAL:
            continue
        last = now

        # 获取当前坐标
        current_x, current_y = _get_absolute_pos()

        # 计算偏移（你要的逻辑）
        delta_x = current_x - last_x
        delta_y = current_y - last_y

        # 记录移动
        if delta_x != 0 or delta_y != 0:
            ts = f"{time.time():.3f}"
            line = f"{ts} MOUSE_MOVE      {delta_x} {delta_y}"
            with open(RECORD_FILE, "a", encoding="utf-8") as f:
                f.write(line + "\n")

        # 更新坐标
        last_x = current_x
        last_y = current_y

        # ============= 鼠标按键 =============
        left = check_mouse_left_change()
        if left in ("down", "up"):
            ts = f"{time.time():.3f}"
            line = f"{ts} MOUSE_LEFT                                 {left}"
            with open(RECORD_FILE, "a", encoding="utf-8") as f:
                f.write(line + "\n")

        right = check_mouse_right_change()
        if right in ("down", "up"):
            ts = f"{time.time():.3f}"
            line = f"{ts} MOUSE_RIGHT                                {right}"
            with open(RECORD_FILE, "a", encoding="utf-8") as f:
                f.write(line + "\n")

        middle = check_mouse_middle_change()
        if middle in ("down", "up"):
            ts = f"{time.time():.3f}"
            line = f"{ts} MOUSE_MIDDLE                                {middle}"
            with open(RECORD_FILE, "a", encoding="utf-8") as f:
                f.write(line + "\n")

        # ============= 滚轮 =============
        wheel = check_wheel_change()
        if wheel in ("forward", "backward", "stop"):
            ts = f"{time.time():.3f}"
            line = f"{ts} MOUSE_WHEEL                                {wheel}"
            with open(RECORD_FILE, "a", encoding="utf-8") as f:
                f.write(line + "\n")

        # ============= 键盘 =============
        key_data = check_key()
        if key_data and isinstance(key_data, list) and len(key_data) > 0:
            try:
                key_code, state = key_data[0]
                hex_key = f"0x{key_code:02X}"
                ts = f"{time.time():.3f}"
                line = f"{ts} KEY {hex_key}                        {state}"
                with open(RECORD_FILE, "a", encoding="utf-8") as f:
                    f.write(line + "\n")
            except:            # noqa
                pass

    print("录制已安全停止")



# ======================
# 启动
# ======================
if __name__ == "__main__":
    get_admin()
    enable_fast_relative()
    record()