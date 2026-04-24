import ctypes
from ctypes import wintypes
import time

user32 = ctypes.WinDLL("user32", use_last_error=True)

# ==========================
# 定义 POINT 结构
# ==========================
class POINT(ctypes.Structure):
    _fields_ = [("x", wintypes.LONG), ("y", wintypes.LONG)]

# ==========================
# 两个开关
# ==========================
_enable_fast_relative = False
_enable_digital_conversion = False

def enable_fast_relative():
    """
    打开 enable_fast_relative 功能
     | 在屏幕上生成 30*30 像素网格,只有鼠标经过时才返回信息,以节省性能
    """
    global _enable_fast_relative
    _enable_fast_relative = True
    print("[Fast] 鼠标快速模式 启用")

def disable_fast_relative():
    """
    关掉 enable_fast_relative 功能
    """
    global _enable_fast_relative
    _enable_fast_relative = False
    print("[Fast] 鼠标快速模式 关闭")

def enable_digital_conversion():
    """
    暂时无效果
    :return:
    """
    global _enable_digital_conversion
    _enable_digital_conversion = True
    print("[Digital] 数字转换 启用：1=按下 0=抬起 -1=滚轮下")

def disable_digital_conversion():
    """
    暂时无效果
    :return:
    """
    global _enable_digital_conversion
    _enable_digital_conversion = False
    print("[Digital] 数字转换 关闭")

# ==========================
# 数字转换装饰器
# ==========================
def digital_convert(func):
    def wrapper(*args, **kwargs):
        result = func(*args, **kwargs)
        if not _enable_digital_conversion or result is None:
            return result
        convert_map = {
            "down": 1,
            "up": 0,
            "forward": 1,
            "backward": -1,
            "stop": 0
        }
        return convert_map.get(result, result)
    return wrapper

# ==========================
# 全局状态
# ==========================
_key_state = {}
_mouse_l = False
_mouse_r = False
_mouse_m = False
_wheel_prev = 0

# 鼠标移动
_last_x = _last_y = None
_last_gx = _last_gy = None
GRID = 30

# ==========================
# 键盘检测
# ==========================
@digital_convert
def check_key(vk):
    """
    监听键盘
     | 若传参则检查特定按键，否则检查全部
     | :param vk: 16进制键码
     | :return: x, y
    """
    current = (user32.GetAsyncKeyState(vk) & 0x8000) != 0
    prev = _key_state.get(vk, False)
    _key_state[vk] = current

    if current and not prev:
        return "down"
    if not current and prev:
        return "up"
    return None

# ==========================
# 鼠标按键
# ==========================
@digital_convert
def check_left():
    """
    检测鼠标左键状态
     | :return: up down
    """
    global _mouse_l
    current = (user32.GetAsyncKeyState(0x01) & 0x8000) != 0
    prev = _mouse_l
    _mouse_l = current

    if current and not prev:
        return "down"
    if not current and prev:
        return "up"
    return None

@digital_convert
def check_right():
    """
    检测鼠标右键状态
     | :return: up down
    """
    global _mouse_r
    current = (user32.GetAsyncKeyState(0x02) & 0x8000) != 0
    prev = _mouse_r
    _mouse_r = current

    if current and not prev:
        return "down"
    if not current and prev:
        return "up"
    return None

@digital_convert
def check_middle():
    """
    检测鼠标中键状态
     | :return: up down
    """
    global _mouse_m
    current = (user32.GetAsyncKeyState(0x04) & 0x8000) != 0
    prev = _mouse_m
    _mouse_m = current

    if current and not prev:
        return "down"
    if not current and prev:
        return "up"
    return None

# ==========================
# 鼠标滚轮
# ==========================
@digital_convert
def check_wheel():
    global _wheel_prev
    delta = user32.GetAsyncKeyState(0x02E) & 0xFFFF
    res = None

    if delta > 0 and _wheel_prev <= 0:
        res = "forward"
    elif delta < 0 and _wheel_prev >= 0:
        res = "backward"
    elif delta == 0 and _wheel_prev != 0:
        res = "stop"

    _wheel_prev = delta
    return res

# ==========================
# 鼠标移动
# ==========================
def get_mouse_delta():
    global _last_x, _last_y, _last_gx, _last_gy
    pt = POINT()
    user32.GetCursorPos(ctypes.byref(pt))
    x = pt.x
    y = pt.y

    if _last_x is None:
        _last_x = x
        _last_y = y
        _last_gx = x // GRID
        _last_gy = y // GRID
        return 0, 0

    if not _enable_fast_relative:
        dx = x - _last_x
        dy = y - _last_y
        _last_x = x
        _last_y = y
        return dx, dy

    gx = x // GRID
    gy = y // GRID
    if gx == _last_gx and gy == _last_gy:
        return 0, 0

    dx = x - _last_x
    dy = y - _last_y
    _last_x = x
    _last_y = y
    _last_gx = gx
    _last_gy = gy
    return dx * GRID, dy * GRID

# ==========================
# 主程序
# ==========================
if __name__ == '__main__':
    enable_fast_relative()
    enable_digital_conversion()

    print("=== 监控启动 ===")
    while True:
        dx, dy = get_mouse_delta()
        if dx or dy:
            print(f"移动 {dx} {dy}")

        # 仅调用一次，不吞抬起
        left = check_left()
        right = check_right()
        middle = check_middle()
        wheel = check_wheel()
        key_a = check_key(0x41)

        if left: print("左键", left)
        if right: print("右键", right)
        if middle: print("中键", middle)
        if wheel: print("滚轮", wheel)
        if key_a: print("键盘A", key_a)

        time.sleep(0.01)