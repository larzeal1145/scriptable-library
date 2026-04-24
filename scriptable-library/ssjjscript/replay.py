import time
import threading
import queue
from ctypes import *

from mouse import *
from keyboard import *
from ssjjscript.BasicsFunction import *
from ssjjscript.MouseMoveSmooth import *

# ======================
# 全局停止信号 & 鼠标绝对坐标获取
# ======================
stop_event = threading.Event()
user32 = windll.user32


class POINT(Structure):
    _fields_ = [("x", c_long), ("y", c_long)]


def get_cursor_pos():
    pt = POINT()
    user32.GetCursorPos(byref(pt))
    return pt.x, pt.y


# ======================
# 线程1：鼠标移动（平滑 / 小偏移瞬时）
# ======================
def _mouse_move_worker(q):
    MOVE_THRESHOLD = 26  # 小于26用瞬时移动
    while not stop_event.is_set():
        task = q.get()
        if task is None:
            q.task_done()
            break

        dx, dy = task
        try:
            # 小偏移: 取当前坐标-偏移-瞬时移动
            if abs(dx) < MOVE_THRESHOLD and abs(dy) < MOVE_THRESHOLD:
                curr_x, curr_y = get_cursor_pos()
                target_x = curr_x + dx
                target_y = curr_y + dy
                mouse_move(target_x, target_y)
            else:
                # 大偏移: 平滑移动
                mouse_move_smooth(dx, dy, 0.02)
        except:
            pass
        q.task_done()


# ======================
# 鼠标按键（左/右/中/滚轮）
# ======================
def _mouse_button_worker(q):
    while not stop_event.is_set():
        task = q.get()
        if task is None:
            q.task_done()
            break

        cmd, *args = task
        try:
            if cmd == "left_down":
                mouse_left_down()
            elif cmd == "left_up":
                mouse_left_up()
            elif cmd == "right_down":
                mouse_right_down()
            elif cmd == "right_up":
                mouse_right_up()
            elif cmd == "middle_down":
                mouse_middle_down()
            elif cmd == "middle_up":
                mouse_middle_up()
            elif cmd == "wheel":
                mouse_wheel(args[0])
        except:
            pass
        q.task_done()


# ======================
# 键盘
# ======================
def _keyboard_worker(q):
    while not stop_event.is_set():
        task = q.get()
        if task is None:
            q.task_done()
            break

        cmd, key = task
        try:
            if cmd == "down":
                key_down(key)
            elif cmd == "up":
                key_up(key)
        except:
            pass
        q.task_done()


# ======================
# 中断控制 ALT+I
# ======================
def _stop_listener():
    while not stop_event.is_set():
        if is_pressed('alt + i'):
            print("\n[停止] 中断重放")
            stop_event.set()
            break
        time.sleep(0.01)


# ======================
# 主重放
# ======================
def start_replay(filename):
    """
    重放你的文件
    |:param filename: 刚录制或手写的重放文件
    |:return: 报错会return的
    """
    q_move = queue.Queue()
    q_btn = queue.Queue()
    q_key = queue.Queue()

    # 启动所有线程
    # 踩踩背
    threading.Thread(target=_mouse_move_worker, args=(q_move,), daemon=True).start()
    threading.Thread(target=_mouse_button_worker, args=(q_btn,), daemon=True).start()
    threading.Thread(target=_keyboard_worker, args=(q_key,), daemon=True).start()
    threading.Thread(target=_stop_listener, daemon=True).start()

    print(f"重放：{filename}")
    print("按 alt + i 停止")

    with open(filename, 'r', encoding='utf-8') as f:
        # 起点
        line = f.readline()
        if line.startswith("START_POS"):
            parts = line.strip().split()
            mouse_move(int(parts[1]), int(parts[2]))
            time.sleep(0.2)

        base_time = None
        while not stop_event.is_set():
            line = f.readline()
            if not line:
                break
            line = line.strip()
            if not line:
                continue

            parts = line.split()
            ts = float(parts[0])
            act = parts[1]

            # 时间同步
            if base_time is None:
                base_time = ts
            wait = ts - base_time
            base_time = ts

            # 可中断等待
            t0 = time.time()
            while time.time() - t0 < wait and not stop_event.is_set():
                time.sleep(0.001)
            if stop_event.is_set():
                break

            # 执行任务
            try:
                if act == "MOUSE_MOVE":
                    dx = int(parts[2])
                    dy = int(parts[3])
                    q_move.put((dx, dy))

                elif act == "MOUSE_LEFT":
                    q_btn.put((f"left_{parts[2]}",))
                elif act == "MOUSE_RIGHT":
                    q_btn.put((f"right_{parts[2]}",))
                elif act == "MOUSE_MIDDLE":
                    q_btn.put((f"middle_{parts[2]}",))

                elif act == "MOUSE_WHEEL":
                    val = 120 if parts[2] == "forward" else -120
                    q_btn.put(("wheel", val))

                elif act == "KEY":
                    key = int(parts[2], 16)
                    q_key.put((parts[3], key))
            except:
                pass

    # 等待执行完毕
    q_move.join()
    q_btn.join()
    q_key.join()
    print("重放已结束")


# ======================
# 运行
# ======================
if __name__ == "__main__":
    replay("record_1_20260424_165737.txt")