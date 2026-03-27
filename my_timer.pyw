import tkinter as tk
from PIL import Image, ImageTk, ImageSequence
import winsound
import time
import datetime
import os
from threading import Thread

# ============ 核心設定區 ============
WORK_MINUTES = 30        # 專注 30 分鐘
SHORT_REST = 10         # 短休息 10 分鐘
LONG_REST = 20          # 每3次後的大休息 20 分鐘
OFF_WORK_TIME = "18:00" # 下班時間
GIF_FILE = "alarm.gif"   
SOUND_FILE = "alarm.wav" 
WOOD_FRAME = "wood_frame.png"
# ============ ======================

try:
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
except:
    pass

class MiniTimeManager(tk.Tk):
    def __init__(self):
        super().__init__()
        
        self.title("Mini's Time Manager")
        self.overrideredirect(True) 
        self.attributes("-topmost", True)
        self.transparent_color = "gray" 
        self.configure(bg=self.transparent_color)
        self.attributes("-transparentcolor", self.transparent_color)
        
        self.is_ringing = False
        self.focus_count = 0
        self.is_off_work = False
        self.current_mode = "FOCUS" # FOCUS, REST, OFF_WORK

        # 畫布與圖層
        self.canvas = tk.Canvas(self, width=280, height=280, bg=self.transparent_color, highlightthickness=0)
        self.canvas.pack()

        # 下層 GIF
        self.load_gif(GIF_FILE)
        self.gif_label = tk.Label(self, bg="white", highlightthickness=0)
        self.gif_label.place(relx=0.5, rely=0.5, anchor="center")
        self.gif_label.bind("<Button-1>", lambda e: self.stop_alarm())

        # 上層木框
        self.load_wood_frame()
        if self.frame_tk:
            self.frame_on_canvas = self.canvas.create_image(140, 140, image=self.frame_tk)
            self.canvas.tag_bind(self.frame_on_canvas, "<Button-1>", lambda e: self.stop_alarm())
        
        # 初始狀態：隱藏並啟動計時
        self.withdraw()
        
        # 啟動下班監測
        Thread(target=self.check_off_work_loop, daemon=True).start()
        # 啟動主要計時循環
        Thread(target=self.main_timer_loop, daemon=True).start()

    def load_wood_frame(self):
        self.frame_tk = None
        if os.path.exists(WOOD_FRAME):
            img = Image.open(WOOD_FRAME).convert("RGBA").resize((280, 280), Image.Resampling.LANCZOS)
            self.frame_tk = ImageTk.PhotoImage(img)

    def load_gif(self, gif_path):
        self.frames = []
        if os.path.exists(gif_path):
            img = Image.open(gif_path)
            for frame in ImageSequence.Iterator(img):
                self.frames.append(ImageTk.PhotoImage(frame.copy().convert("RGBA").resize((180, 180))))
            self.current_frame = 0

    def start_animation(self):
        if self.frames:
            self.current_frame = 0
            self.play_next_frame()

    def play_next_frame(self):
        if self.is_ringing:
            self.gif_label.configure(image=self.frames[self.current_frame])
            self.current_frame = (self.current_frame + 1) % len(self.frames)
            self.after(100, self.play_next_frame)

    # --- 核心邏輯循環 ---
    def main_timer_loop(self):
        while not self.is_off_work:
            # 1. 專注 30 分鐘
            self.current_mode = "FOCUS"
            time.sleep(WORK_MINUTES * 60)
            if self.is_off_work: break
            
            # 2. 專注結束，鬧鐘響
            self.focus_count += 1
            self.after(0, self.trigger_alarm)
            
            # 等待使用者點擊關閉鬧鐘（停止 ringing）
            while self.is_ringing:
                time.sleep(1)
            
            # 3. 進入休息時間
            self.current_mode = "REST"
            rest_time = LONG_REST if self.focus_count % 3 == 0 else SHORT_REST
            time.sleep(rest_time * 60)
            if self.is_off_work: break
            
            # 4. 休息結束，鬧鐘再次響（呼嘯提醒開工）
            self.after(0, self.trigger_alarm)
            while self.is_ringing:
                time.sleep(1)

    def check_off_work_loop(self):
        while True:
            now = datetime.datetime.now().strftime("%H:%M")
            if now == OFF_WORK_TIME:
                self.is_off_work = True
                self.current_mode = "OFF_WORK"
                self.after(0, self.trigger_alarm)
                break
            time.sleep(30)

    def trigger_alarm(self):
        self.is_ringing = True
        self.deiconify()
        self.center_window()
        self.start_animation()
        Thread(target=self.play_sound_loop, daemon=True).start()

    def play_sound_loop(self):
        while self.is_ringing:
            winsound.PlaySound(SOUND_FILE if os.path.exists(SOUND_FILE) else "SystemAsterisk", winsound.SND_FILENAME)
            time.sleep(0.1)

    def stop_alarm(self):
        if self.is_ringing:
            self.is_ringing = False
            winsound.PlaySound(None, winsound.SND_PURGE)
            self.withdraw()
            self.log_focus()
            if self.current_mode == "OFF_WORK":
                self.destroy()

    def log_focus(self):
        now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with open("focus_log.txt", "a", encoding="utf-8") as f:
            f.write(f"[{now}] 模式:{self.current_mode} 次數:{self.focus_count}\n")
            
    def center_window(self):
        sw, sh = self.winfo_screenwidth(), self.winfo_screenheight()
        self.geometry(f"280x280+{int(sw/2-140)}+{int(sh/3-140)}")

if __name__ == "__main__":
    app = MiniTimeManager()
    app.mainloop()
