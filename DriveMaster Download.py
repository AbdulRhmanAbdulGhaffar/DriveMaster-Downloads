import os
import sys
import threading
import datetime
import time  # Added for sleep logic
import tkinter as tk
from tkinter import filedialog, messagebox
import customtkinter as ctk

# استيراد محرك التحميل مباشرة داخل البايثون (بدون برامج خارجية)
import yt_dlp

# --- Theme Configuration ---
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("dark-blue")

class DriveMasterApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        # Window Setup
        self.title("DriveMaster Downloads - Professional")
        self.geometry("900x680")
        self.resizable(False, False)
        
        self.is_downloading = False
        self.should_cancel = False # للتحكم في الإيقاف
        self.is_paused_flag = False # للتحكم في حالة التوقف المؤقت

        # --- Header Section ---
        self.header_frame = ctk.CTkFrame(self, corner_radius=0, fg_color="transparent")
        self.header_frame.pack(pady=10)
        
        self.lbl_title = ctk.CTkLabel(self.header_frame, text="DriveMaster Download Professional ", font=("Roboto", 30, "bold"), text_color="#3B8ED0")
        self.lbl_title.pack()
        
        self.lbl_subtitle = ctk.CTkLabel(self.header_frame, text="All-in-One Engine | Turbo Mode Activated ", font=("Roboto", 11), text_color="gray")
        self.lbl_subtitle.pack()

        # --- Tab View ---
        self.tab_view = ctk.CTkTabview(self, width=850, height=280)
        self.tab_view.pack(pady=5)
        
        self.tab_main = self.tab_view.add("Main Settings")
        self.tab_advanced = self.tab_view.add("Advanced Options")

        # === TAB 1: Main Settings ===
        self.lbl_link = ctk.CTkLabel(self.tab_main, text="Target URL:", font=("Roboto", 13, "bold"))
        self.lbl_link.grid(row=0, column=0, padx=15, pady=15, sticky="w")
        
        self.entry_link = ctk.CTkEntry(self.tab_main, placeholder_text="Paste Google Drive, YouTube, or Direct Link here...", width=550, height=35)
        self.entry_link.grid(row=0, column=1, padx=10, pady=15)
        
        self.btn_paste = ctk.CTkButton(self.tab_main, text="Paste Link", width=100, height=35, command=self.paste_link, fg_color="#F39C12", hover_color="#D68910")
        self.btn_paste.grid(row=0, column=2, padx=10, pady=15)

        self.lbl_out = ctk.CTkLabel(self.tab_main, text="Save Location:", font=("Roboto", 13, "bold"))
        self.lbl_out.grid(row=1, column=0, padx=15, pady=10, sticky="w")
        
        self.entry_out = ctk.CTkEntry(self.tab_main, placeholder_text="Default: Downloads Folder", width=550, height=35)
        self.entry_out.grid(row=1, column=1, padx=10, pady=10)
        
        self.btn_browse_out = ctk.CTkButton(self.tab_main, text="Browse", width=100, height=35, command=self.browse_output)
        self.btn_browse_out.grid(row=1, column=2, padx=10, pady=10)

        self.lbl_fmt = ctk.CTkLabel(self.tab_main, text="Format:", font=("Roboto", 13, "bold"))
        self.lbl_fmt.grid(row=2, column=0, padx=15, pady=10, sticky="w")
        
        self.option_format = ctk.CTkOptionMenu(self.tab_main, values=["Best Video + Audio", "Audio Only (Best Quality)", "Video Only"], width=200)
        self.option_format.grid(row=2, column=1, padx=10, pady=10, sticky="w")

        # === TAB 2: Advanced Options ===
        self.lbl_auth_title = ctk.CTkLabel(self.tab_advanced, text="Access & Authentication Mode:", font=("Roboto", 14, "bold"))
        self.lbl_auth_title.pack(pady=(15, 5), padx=20, anchor="w")

        self.auth_mode_var = ctk.StringVar(value="Public Link")
        self.seg_auth_mode = ctk.CTkSegmentedButton(self.tab_advanced, 
                                                    values=["Public Link", "Browser Cookies", "Cookies File", "User/Pass (Basic)"],
                                                    command=self.update_auth_ui,
                                                    variable=self.auth_mode_var,
                                                    width=700, height=35,
                                                    dynamic_resizing=False)
        self.seg_auth_mode.pack(pady=10)

        self.frame_auth_container = ctk.CTkFrame(self.tab_advanced, fg_color="transparent")
        self.frame_auth_container.pack(fill="x", pady=5, padx=20)

        self.frame_browser = ctk.CTkFrame(self.frame_auth_container, fg_color="transparent")
        self.lbl_browser = ctk.CTkLabel(self.frame_browser, text="Select Source Browser:", font=("Roboto", 12))
        self.lbl_browser.pack(side="left", padx=10)
        self.combo_browser = ctk.CTkComboBox(self.frame_browser, values=["Chrome", "Edge", "Firefox", "Brave", "Opera"], width=250)
        self.combo_browser.pack(side="left", padx=10)

        self.frame_file = ctk.CTkFrame(self.frame_auth_container, fg_color="transparent")
        self.entry_cookie_file = ctk.CTkEntry(self.frame_file, placeholder_text="Path to cookies.txt...", width=400)
        self.entry_cookie_file.pack(side="left", padx=(0, 10))
        self.btn_browse_cookie_file = ctk.CTkButton(self.frame_file, text="Browse File", width=100, command=self.browse_cookies_file)
        self.btn_browse_cookie_file.pack(side="left")

        self.frame_userpass = ctk.CTkFrame(self.frame_auth_container, fg_color="transparent")
        self.entry_user = ctk.CTkEntry(self.frame_userpass, placeholder_text="Username / Email", width=200)
        self.entry_user.pack(side="left", padx=(0, 10))
        self.entry_pass = ctk.CTkEntry(self.frame_userpass, placeholder_text="Password", show="*", width=200)
        self.entry_pass.pack(side="left", padx=(0, 10))

        self.update_auth_ui("Public Link")

        # --- Dashboard & Controls ---
        self.status_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.status_frame.pack(pady=5, padx=20, fill="x")

        self.lbl_speed = ctk.CTkLabel(self.status_frame, text="Speed: -- MiB/s", font=("Consolas", 14, "bold"), text_color="#2ECC71")
        self.lbl_speed.pack(side="left", padx=20)
        
        self.lbl_eta = ctk.CTkLabel(self.status_frame, text="ETA: --:--", font=("Consolas", 14, "bold"), text_color="#F1C40F")
        self.lbl_eta.pack(side="right", padx=20)

        self.lbl_progress = ctk.CTkLabel(self, text="Ready.", font=("Roboto", 13))
        self.lbl_progress.pack(pady=(0, 5))

        self.progress_bar = ctk.CTkProgressBar(self, width=750, height=15, progress_color="#3B8ED0")
        self.progress_bar.set(0)
        self.progress_bar.pack(pady=5)

        self.btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.btn_frame.pack(pady=10)

        # 1. Start Button
        self.btn_start = ctk.CTkButton(self.btn_frame, text="START DOWNLOAD", font=("Roboto", 15, "bold"), height=40, width=180, command=self.start_thread, fg_color="#27AE60", hover_color="#219150")
        self.btn_start.pack(side="left", padx=10)

        # 2. Pause Button
        self.btn_pause = ctk.CTkButton(self.btn_frame, text="PAUSE", font=("Roboto", 15, "bold"), height=40, width=140, command=self.pause_download, fg_color="#F39C12", hover_color="#D68910", state="disabled")
        self.btn_pause.pack(side="left", padx=10)

        # 3. Stop Button
        self.btn_cancel = ctk.CTkButton(self.btn_frame, text="STOP", font=("Roboto", 15, "bold"), height=40, width=140, command=self.cancel_download, fg_color="#C0392B", hover_color="#922B21", state="disabled")
        self.btn_cancel.pack(side="left", padx=10)
        
        self.btn_open_folder = ctk.CTkButton(self.btn_frame, text="📂 Open Folder", font=("Roboto", 13), height=40, width=140, command=self.open_output_folder, fg_color="#555", state="disabled")
        self.btn_open_folder.pack(side="left", padx=10)

        self.log_box = ctk.CTkTextbox(self, width=850, height=80, font=("Consolas", 10), activate_scrollbars=True)
        self.log_box.pack(pady=10)
        self.log_box.configure(state="disabled")

        self.lbl_credits = ctk.CTkLabel(self, text="Developed by AbdulRhman AbdulGhaffar", font=("Code New Roman", 11, "bold"), text_color="#3B8ED0")
        self.lbl_credits.pack(side="bottom", pady=5)

    # --- UI Logic ---
    def update_auth_ui(self, value):
        self.frame_browser.pack_forget()
        self.frame_file.pack_forget()
        self.frame_userpass.pack_forget()
        if value == "Browser Cookies":
            self.frame_browser.pack(pady=5)
        elif value == "Cookies File":
            self.frame_file.pack(pady=5)
        elif value == "User/Pass (Basic)":
            self.frame_userpass.pack(pady=5)

    def paste_link(self):
        try:
            self.entry_link.delete(0, "end")
            self.entry_link.insert(0, self.clipboard_get())
        except: pass

    def browse_output(self):
        f = filedialog.askdirectory()
        if f:
            self.entry_out.delete(0, "end")
            self.entry_out.insert(0, f)

    def browse_cookies_file(self):
        f = filedialog.askopenfilename(filetypes=[("Text Files", "*.txt")])
        if f:
            self.entry_cookie_file.delete(0, "end")
            self.entry_cookie_file.insert(0, f)
            
    def open_output_folder(self):
        path = self.entry_out.get().strip()
        if not path: path = os.path.join(os.path.expanduser("~"), "Downloads")
        try: os.startfile(path)
        except Exception as e: messagebox.showerror("Error", f"Could not open folder: {e}")

    def log(self, msg):
        self.log_box.configure(state="normal")
        self.log_box.insert("end", f"> {msg}\n")
        self.log_box.see("end")
        self.log_box.configure(state="disabled")

    # --- NEW: Embedded Download Engine ---
    def start_thread(self):
        # 1. حالة الاستكمال (Resume) - إذا كان البرنامج في وضع Pause
        if self.is_downloading and self.is_paused_flag:
            self.is_paused_flag = False
            self.log("▶ Resuming download...")
            self.update_ui_state("running")
            return # خروج، لا تبدأ خيط جديد

        # 2. حالة البدء الجديد (New Start)
        if not self.is_downloading:
            self.should_cancel = False
            self.is_paused_flag = False
            threading.Thread(target=self.run_download_embedded, daemon=True).start()

    # دالة مساعدة لتنسيق حجم الملفات (شكل أفضل)
    def format_bytes(self, size):
        if size is None: return "N/A"
        power = 1024
        n = 0
        power_labels = {0 : 'B', 1: 'KiB', 2: 'MiB', 3: 'GiB', 4: 'TiB'}
        while size > power:
            size /= power
            n += 1
        return f"{size:.2f} {power_labels.get(n, '')}"

    def progress_hook(self, d):
        if self.should_cancel:
            raise Exception("Download Cancelled by User")

        # --- منطق التوقف المؤقت (Sleep Loop) ---
        # هنا البرنامج هيفضل يلف حول نفسه وينام 0.5 ثانية طول ما الزرار Pause
        while self.is_paused_flag:
            # نتحقق من الإلغاء داخل اللوب عشان لو داس Stop وهو واقف
            if self.should_cancel:
                raise Exception("Download Cancelled by User")
            time.sleep(0.5) 
        
        # --- باقي كود التحديث الطبيعي ---
        if d['status'] == 'downloading':
            # 1. حساب النسبة المئوية
            try:
                total = d.get('total_bytes') or d.get('total_bytes_estimate')
                downloaded = d.get('downloaded_bytes', 0)
                
                if total:
                    percent = downloaded / total
                    self.progress_bar.set(percent)
                    self.lbl_progress.configure(text=f"Downloading: {percent:.1%}  ({self.format_bytes(downloaded)} / {self.format_bytes(total)})")
                else:
                    self.lbl_progress.configure(text=f"Downloading: {self.format_bytes(downloaded)} (Total Unknown)")
            except: 
                pass
            
            # 2. السرعة
            try:
                speed = d.get('speed')
                if speed:
                    self.lbl_speed.configure(text=f"Speed: {self.format_bytes(speed)}/s")
            except: pass
            
            # 3. الوقت المتبقي
            try:
                eta = d.get('eta')
                if eta:
                    eta_str = str(datetime.timedelta(seconds=int(eta)))
                    self.lbl_eta.configure(text=f"ETA: {eta_str}")
            except: pass

        elif d['status'] == 'finished':
            self.progress_bar.set(1)
            self.lbl_progress.configure(text="Processing / Merging...")
            self.log("Download finished. Processing file...")

    def logger_hook(self, msg):
        # تصفية الرسائل المزعجة
        if not msg.startswith("[debug]"):
            self.log(msg)

    def run_download_embedded(self):
        link = self.entry_link.get().strip()
        out_path = self.entry_out.get().strip()
        auth_mode = self.auth_mode_var.get()
        fmt_mode = self.option_format.get()

        if not link:
            messagebox.showerror("Error", "Please enter a Link first!")
            return

        self.is_downloading = True
        self.update_ui_state("running")
        self.log("Initializing Embedded Engine (Turbo Mode)...")

        # --- إعدادات المحرك الداخلي ---
        ydl_opts = {
            'logger': self, 
            'progress_hooks': [self.progress_hook],
            'outtmpl': f'{out_path}/%(title)s.%(ext)s' if out_path else '%(title)s.%(ext)s',
            'nocheckcertificate': True,
            'ignoreerrors': True,
            'quiet': True,
            'no_warnings': True,
            
            # === إعدادات التسريع ===
            'concurrent_fragment_downloads': 5,
            'buffersize': 1024 * 1024,
            'http_chunk_size': 10485760,
            'retries': 10,
            'fragment_retries': 10,
        }

        if not out_path:
             ydl_opts['outtmpl'] = os.path.join(os.path.expanduser("~"), "Downloads", '%(title)s.%(ext)s')

        # --- خيارات المصادقة ---
        if auth_mode == "Browser Cookies":
            browser_name = self.combo_browser.get().lower()
            ydl_opts['cookiesfrombrowser'] = (browser_name, None, None, None)
            self.log(f"Using cookies from: {browser_name}")
        elif auth_mode == "Cookies File":
            c_file = self.entry_cookie_file.get().strip()
            if c_file:
                ydl_opts['cookiefile'] = c_file
                self.log(f"Using cookie file: {c_file}")
        elif auth_mode == "User/Pass (Basic)":
            u = self.entry_user.get().strip()
            p = self.entry_pass.get().strip()
            if u and p:
                ydl_opts['username'] = u
                ydl_opts['password'] = p

        # --- خيارات الجودة ---
        if "Audio Only" in fmt_mode:
            ydl_opts['format'] = 'bestaudio/best'
            ydl_opts['postprocessors'] = [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }]
        elif "Video Only" in fmt_mode:
            ydl_opts['format'] = 'bestvideo'
        else:
            ydl_opts['format'] = 'best' 

        # --- بدء التحميل ---
        try:
            if getattr(sys, 'frozen', False):
                ffmpeg_local = os.path.join(sys._MEIPASS, "ffmpeg.exe")
                if os.path.exists(ffmpeg_local):
                    ydl_opts['ffmpeg_location'] = sys._MEIPASS

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.params['logger'] = type('Logger', (), {'debug': lambda s: None, 'warning': lambda s: self.log(f"Warning: {s}"), 'error': lambda s: self.log(f"Error: {s}"), 'info': lambda s: self.logger_hook(s)})
                ydl.download([link])
            
            if not self.should_cancel:
                self.log("✅ Download Completed Successfully!")
                self.update_ui_state("stopped")
                self.btn_open_folder.configure(state="normal", fg_color="#2980B9")
                messagebox.showinfo("Success", "Download Finished!")

        except Exception as e:
            if "Download Cancelled" in str(e):
                self.log("🛑 Download Cancelled by User.")
                self.update_ui_state("stopped")
            else:
                self.log(f"Error: {e}")
                if "ffmpeg" in str(e).lower():
                     self.log("👉 Note: High quality merging requires FFmpeg.")
                self.update_ui_state("stopped")
        finally:
            self.is_downloading = False

    def pause_download(self):
        # شرط التوقف: لازم يكون بيحمل ومش واقف أصلاً
        if self.is_downloading and not self.is_paused_flag:
            self.is_paused_flag = True
            self.log("⏸ Paused. Click RESUME to continue.")
            self.update_ui_state("paused")

    def cancel_download(self):
        self.should_cancel = True
        self.is_paused_flag = False # لازم نفك التجميد عشان يعرف يقفل
        self.log("Stopping...")

    def update_ui_state(self, state):
        if state == "running":
            self.btn_start.configure(state="disabled", text="Running...")
            self.btn_pause.configure(state="normal")
            self.btn_cancel.configure(state="normal")
            self.btn_open_folder.configure(state="disabled")
        elif state == "paused":
            # زر الاستكمال هو نفسه زر البدء
            self.btn_start.configure(state="normal", text="▶ RESUME", fg_color="#F39C12")
            self.btn_pause.configure(state="disabled")
            self.btn_cancel.configure(state="normal")
        else: # stopped
            self.btn_start.configure(state="normal", text="START DOWNLOAD", fg_color="#27AE60")
            self.btn_pause.configure(state="disabled")
            self.btn_cancel.configure(state="disabled")

    # For yt_dlp logger redirect
    def debug(self, msg): pass
    def warning(self, msg): self.log(f"Warning: {msg}")
    def error(self, msg): self.log(f"Error: {msg}")
    def info(self, msg): self.logger_hook(msg)

if __name__ == "__main__":
    app = DriveMasterApp()
    app.mainloop()