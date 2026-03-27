import tkinter as tk
from PIL import Image, ImageTk, ImageSequence
import winsound
import time
import datetime
import os
from threading import Thread
import socket

# ============ 核心設定區 ============
WORK_MINUTES = 30        
SHORT_REST = 10         
LONG_REST = 20          
OFF_WORK_TIME = "18:00" 

# 音效檔名設定
SOUND_FOCUS_DONE = "alarm.wav"   # 專注結束
SOUND_REST_DONE = "timeup.wav"  # 休息結束 (準備開工)
SOUND_OFF_WORK = "off.wav"      # 下班囉
GIF_FILE = "alarm.gif"   
WOOD_FRAME = "wood_frame.png"
# ============ ======================

try:
    lock_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    lock_socket.bind(('127.0.0.1', 45678))
except socket.error:
    os._exit(0)

try:
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
except:
    pass

class MiniProfessionalTimer(tk.Tk):
    def __init__(self):
        super().__init__()
        
        self.title("Mini's Manager")
        self.overrideredirect(True) 
        self.attributes("-topmost", True)
        self.transparent_color = "gray" 
        self.configure(bg=self.transparent_color)
        self.attributes("-transparentcolor", self.transparent_color)
        
        self.is_ringing = False
        self.focus_count = 0
        self.is_off_work = False
        self.current_mode = "FOCUS"
        self.current_sound = SOUND_FOCUS_DONE # 預設音效

        self.canvas = tk.Canvas(self, width=280, height=280, bg=self.transparent_color, highlightthickness=0)
        self.canvas.pack()

        self.load_gif(GIF_FILE)
        self.gif_label = tk.Label(self, bg="white", highlightthickness=0)
        self.gif_label.place(relx=0.5, rely=0.5, anchor="center")
        self.gif_label.bind("<Button-1>", lambda e: self.stop_alarm())

        self.load_wood_frame()
        if self.frame_tk:
            self.frame_on_canvas = self.canvas.create_image(140, 140, image=self.frame_tk)
            self.canvas.tag_bind(self.frame_on_canvas, "<Button-1>", lambda e: self.stop_alarm())
        
        self.withdraw()
        
        Thread(target=self.check_off_work_loop, daemon=True).start()
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

    def main_timer_loop(self):
        while not self.is_off_work:
            # 專注階段
            self.current_mode = "FOCUS"
            time.sleep(WORK_MINUTES * 60)
            if self.is_off_work: break
            
            # 專注結束 -> 播 alarm.wav
            self.focus_count += 1
            self.current_sound = SOUND_FOCUS_DONE
            self.after(0, self.trigger_alarm)
            while self.is_ringing: time.sleep(1)
            
            # 休息階段
            self.current_mode = "REST"
            rest_time = LONG_REST if self.focus_count % 3 == 0 else SHORT_REST
            time.sleep(rest_time * 60)
            if self.is_off_work: break
            
            # 休息結束 -> 播 timeup.wav
            self.current_sound = SOUND_REST_DONE
            self.after(0, self.trigger_alarm)
            while self.is_ringing: time.sleep(1)

    def check_off_work_loop(self):
        while True:
            now = datetime.datetime.now().strftime("%H:%M")
            if now == OFF_WORK_TIME:
                self.is_off_work = True
                self.current_mode = "OFF_WORK"
                self.current_sound = SOUND_OFF_WORK # 下班播 off.wav
                self.after(0, self.trigger_alarm)
                break
            time.sleep(30)

    def trigger_alarm(self):
        self.is_ringing = True
        self.deiconify()
        self.center_window()
        self.start_animation()
        # 開啟獨立執行緒播放音效
        Thread(target=self.play_sound_loop, daemon=True).start()

    def play_sound_loop(self):
        while self.is_ringing:
            target_sound = self.current_sound
            if os.path.exists(target_sound):
                # 使用 SND_NODEFAULT 防止沒檔案時發出系統預設嗶聲
                winsound.PlaySound(target_sound, winsound.SND_FILENAME | winsound.SND_NODEFAULT)
            else:
                winsound.PlaySound("SystemAsterisk", winsound.SND_ALIAS)
            time.sleep(0.1)

    def stop_alarm(self):
        if self.is_ringing:
            self.is_ringing = False
            # 【關鍵修復】點擊瞬間強制關閉音效卡所有聲音輸出
            winsound.PlaySound(None, winsound.SND_PURGE)
            self.withdraw()
            self.log_focus()
            if self.current_mode == "OFF_WORK":
                os._exit(0)

    def log_focus(self):
        now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with open("focus_log.txt", "a", encoding="utf-8") as f:
            f.write(f"[{now}] 模式:{self.current_mode} 音效:{self.current_sound} 次數:{self.focus_count}\n")
            
    def center_window(self):
        sw, sh = self.winfo_screenwidth(), self.winfo_screenheight()
        self.geometry(f"280x280+{int(sw/2-140)}+{int(sh/3-140)}")

if __name__ == "__main__":
    app = MiniProfessionalTimer()
    app.mainloop()
