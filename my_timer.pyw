import time
import winsound
import tkinter as tk
from tkinter import messagebox
import os

# --- 設定區 ---
WORK_MINUTES = 30
SHORT_BREAK_MINUTES = 10
LONG_BREAK_MINUTES = 20

def is_dnd_active():
    """
    這裡預留給你未來擴充偵測功能。
    目前我們先預設為 False 讓它能正常彈窗。
    """
    return False 

def alert_with_delay(title, message):
    # 如果在勿擾模式，就每 10 秒檢查一次直到關閉
    while is_dnd_active():
        time.sleep(10)
    
    # 連續播放 3 次星際感音效
    for i in range(3):
    winsound.PlaySound("SystemAsterisk", winsound.SND_ALIAS)
    time.sleep(0.5)  # 每次聲音之間停頓 0.5 秒，聽起來比較舒服   
    # 跳出視窗
    root = tk.Tk()
    root.withdraw()
    messagebox.showinfo(title, message)
    root.destroy()

def start_timer():
    work_count = 0
    while True:
        # 1. 工作階段
        time.sleep(WORK_MINUTES * 60)
        work_count += 1
        
        # 2. 判斷休息長度
        if work_count % 3 == 0:
            break_mins = LONG_BREAK_MINUTES
            msg = f"已完成 3 次工作 (90分鐘)！\n請大休息 {break_mins} 分鐘 🧘"
        else:
            break_mins = SHORT_BREAK_MINUTES
            msg = f"30 分鐘工作結束！\n請休息 {break_mins} 分鐘 ☕ (第 {work_count} 次)"
        
        alert_with_delay("提醒：該休息了", msg)
        
        # 3. 休息階段
        time.sleep(break_mins * 60)
        alert_with_delay("提醒：休息結束", "休息時間到囉，該開始工作了！💻")

if __name__ == "__main__":
    start_timer()