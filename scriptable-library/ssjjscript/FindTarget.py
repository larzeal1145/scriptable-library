import time
from fileinput import close
from time import sleep

import pyautogui
from random import randint
from threading import Thread
from keyboard import *
import keyboard



def _find_image_on_screen(target_img_path, confidence=0.8):
    try:
        # 查找图像（confidence 参数仅支持 OpenCV 后端,需安装 opencv-python）
        match_pos = pyautogui.locateOnScreen(
            target_img_path,
            confidence=confidence,
            grayscale=True  # 灰度匹配-提速,降低颜色干扰
        )
        if match_pos:
            center_x, center_y = pyautogui.center(match_pos)
            print(f"找到目标 位置：{match_pos}，中点：({center_x}, {center_y})")
            return match_pos, (center_x, center_y)
        else:
            print("未找到")
            return None, None
    except Exception as e:
        print(f"失败：{e}")
        return None, None
def find_photo(target):#"target.png" or "target.png"  # 需提前准备目标图像,把照片名字改成  target.png
    """
    寻找特定图片
    将图片名传入
    如'1145.PNG'
    match_center:中点坐标
    match_pos:<这个东西是几年前写的,我忘记是什么了>
    """
    match_region, match_center = _find_image_on_screen(target, confidence=0.7)
    if match_center:    # NOQA
        pass
        # pyautogui.click(match_center)  #点击中点
        return True
if __name__ == '__main__':
    time.sleep(3)
    if find_photo('123.png'):
        print('找到')
