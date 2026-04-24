# import ctypes
# from ctypes import wintypes
# import time
#
# user32 = ctypes.WinDLL("user32", use_last_error=True)    # NOQA
#
# class POINT(ctypes.Structure):
#     _fields_ = [("x", wintypes.LONG), ("y", wintypes.LONG)]
#
# # ======================
# # 全局状态
# # ======================
# _key_state = {}
# _mouse_left_state = False
# _mouse_right_state = False
# _mouse_middle_state = False
# _wheel_last_delta = 0
# _last_mx, _last_my = None, None
#
# # ======================
# # 键盘检测：传参=指定键 | 空白=全键盘
# # 已把【打印逻辑】放进这里
# # ======================
# def check_key(vk=None):
#     global _key_state
#
#     # 传参：检测单个键
#     if vk is not None:
#         current = (user32.GetAsyncKeyState(vk) & 0x8000) != 0
#         prev = _key_state.get(vk, False)
#         _key_state[vk] = current
#
#         if current and not prev:
#             return "down"
#         elif not current and prev:
#             return "up"
#         return None
#
#     # 无参 = 全键盘检测（0x08起）+ 内部直接打印
#     changes = []
#     for code in range(0x08, 0xFF + 1):
#         current = (user32.GetAsyncKeyState(code) & 0x8000) != 0
#         prev = _key_state.get(code, False)
#         _key_state[code] = current
#
#         if current and not prev:
#             print(f"[按键] 0x{code:02X} down")
#             changes.append((code, "down"))
#         elif not current and prev:
#             print(f"[按键] 0x{code:02X} up")
#             changes.append((code, "up"))
#
#     return changes
#
# # ======================
# # 鼠标按键
# # ======================
# def check_mouse_left_change():
#     global _mouse_left_state
#     current = (user32.GetAsyncKeyState(0x01) & 0x8000) != 0
#     prev = _mouse_left_state
#     _mouse_left_state = current
#     return "down" if current and not prev else "up" if not current and prev else None
#
# def check_mouse_right_change():
#     global _mouse_right_state
#     current = (user32.GetAsyncKeyState(0x02) & 0x8000) != 0
#     prev = _mouse_right_state
#     _mouse_right_state = current
#     return "down" if current and not prev else "up" if not current and prev else None
#
# def check_mouse_middle_change():
#     global _mouse_middle_state
#     current = (user32.GetAsyncKeyState(0x04) & 0x8000) != 0
#     prev = _mouse_middle_state
#     _mouse_middle_state = current
#     return "down" if current and not prev else "up" if not current and prev else None
#
# # ======================
# # 鼠标滚轮（已修复）
# # ======================
# def check_wheel_change():
#     global _wheel_last_delta
#     delta = user32.GetAsyncKeyState(0x02E) & 0xFFFF
#
#     change = None
#     if delta > 0 and _wheel_last_delta <= 0:
#         change = "forward"
#     elif delta < 0 and _wheel_last_delta >= 0:
#         change = "backward"
#     elif delta == 0 and _wheel_last_delta != 0:
#         change = "stop"
#
#     _wheel_last_delta = delta
#     return change
#
# # ======================
# # 鼠标相对移动
# # ======================
# def get_mouse_relative():
#     global _last_mx, _last_my
#     pt = POINT()
#     user32.GetCursorPos(ctypes.byref(pt))
#     x, y = pt.x, pt.y
#
#     if _last_mx is None:
#         _last_mx, _last_my = x, y
#         return 0, 0
#
#     dx = x - _last_mx
#     dy = y - _last_my
#     _last_mx, _last_my = x, y
#     return dx, dy
#
# # ======================
# # 测试主循环
# # ======================
# if __name__ == "__main__":
#     print("=== 键盘鼠标监控 ===")
#     print("按 ESC 退出\n")
#
#     while True:
#         # 现在这里超级干净：只调用+判断ESC
#         key_changes = check_key()
#         for vk, action in key_changes:
#             # 只保留ESC退出逻辑
#             if vk == 0x1B and action == "down":
#                 print("→ 退出程序")
#                 exit()
#
#         # 鼠标
#         ml = check_mouse_left_change()
#         mr = check_mouse_right_change()
#         mm = check_mouse_middle_change()
#         wheel = check_wheel_change()
#         dx, dy = get_mouse_relative()
#
#         if ml: print("[鼠标] 左键", ml)
#         if mr: print("[鼠标] 右键", mr)
#         if mm: print("[鼠标] 中键", mm)
#         if wheel: print("[滚轮]", wheel)
#         if dx != 0 or dy != 0:
#             print(f"[鼠标移动] X:{dx:>3} Y:{dy:>3}")
#
#         time.sleep(0.01)
