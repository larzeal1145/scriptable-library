import ctypes
import time
from ctypes import wintypes
import sys
import keyboard

# ==============================================
# 鼠标平滑移动
# ==============================================

user32 = ctypes.WinDLL("user32", use_last_error=True)

# 常量
INPUT_MOUSE = 0
MOUSEEVENTF_MOVE = 0x0001

# 结构体定义
class MOUSEINPUT(ctypes.Structure):
    _fields_ = [
        ("dx", wintypes.LONG),
        ("dy", wintypes.LONG),
        ("mouseData", wintypes.DWORD),
        ("dwFlags", wintypes.DWORD),
        ("time", wintypes.DWORD),
        ("dwExtraInfo", ctypes.POINTER(wintypes.ULONG)),
    ]

class INPUT(ctypes.Structure):
    _fields_ = [
        ("type", wintypes.DWORD),
        ("mi", MOUSEINPUT),
    ]

def mouse_move_relative(dx, dy):
    inp = INPUT()
    inp.type = INPUT_MOUSE
    inp.mi.dx = dx
    inp.mi.dy = dy
    inp.mi.dwFlags = MOUSEEVENTF_MOVE
    user32.SendInput(1, ctypes.byref(inp), ctypes.sizeof(INPUT))

def mouse_move_smooth(dx_total, dy_total, duration=0.3, steps=50):
    """
    平滑相对移动鼠标
     | dx_total:总横向位移
     | dy_total:总纵向位移
     | duration:总耗时秒
     | steps:分多少步移动
     | 当位移<=25时无法运行,你可以检测鼠标当前坐标然后加上偏移量用瞬间移动
    """
    step_dx = dx_total / steps
    step_dy = dy_total / steps
    delay = duration / steps  # 每步延时

    for _ in range(steps):
        mouse_move_relative(int(round(step_dx)), int(round(step_dy)))
        time.sleep(delay)

# def is_admin():
#     try:
#         return ctypes.windll.shell32.IsUserAnAdmin() != 0
#     except:
#         return False
#
#
# def run_as_admin():
#     try:
#         ctypes.windll.shell32.ShellExecuteW(
#             None, "runas", sys.executable, " ".join(sys.argv), None, 1
#         )
#         sys.exit()
#     except Exception as e:
#         print("权限没拿到:", e)
#         sys.exit(1)
#
#
# if not is_admin():
#     print("请求管理权限")
#     run_as_admin()

if __name__ == "__main__":

    time.sleep(6)
    # 平滑右移200
    mouse_move_smooth(2000, 0, 0.1)
    time.sleep(0.3)

    # 平滑下移200
    mouse_move_smooth(0, 200, 0.1)
    time.sleep(0.3)
    #
    # # 平滑左移200
    # mouse_move_smooth(-200, 0, 0.4)
    # time.sleep(0.3)
    #
    # # 平滑上移200
    # mouse_move_smooth(0, -200, 0.4)

    print("移动完成")