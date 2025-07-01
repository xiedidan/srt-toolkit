import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import threading
import os
import sys
from datetime import datetime
import queue
import base64
from io import BytesIO
try:
    from PIL import Image, ImageTk
except ImportError:
    pass  # 如果没有PIL库，就不显示图标

# 导入原有的srt_tts模块
from srt_tts import SrtTTS

# 定义深色主题颜色
DARK_BG = "#121212"
DARK_FG = "#FFFFFF"
ACCENT_COLOR = "#007BFF"
SECONDARY_BG = "#1E1E1E"
BUTTON_BG = "#2D2D2D"
BUTTON_ACTIVE_BG = "#3D3D3D"
ENTRY_BG = "#2D2D2D"
ENTRY_FG = "#FFFFFF"
HIGHLIGHT_BG = "#3D3D3D"
BORDER_COLOR = "#555555"

# 编码的应用图标 (一个简单的音频波形图标)
ICON_DATA = """
iVBORw0KGgoAAAANSUhEUgAAAEAAAABACAYAAACqaXHeAAAACXBIWXMAAAsTAAALEwEAmpwYAAAF8WlUWHRYTUw6Y29tLmFkb2JlLnhtcAAAAAAAPD94cGFja2V0IGJlZ2luPSLvu78iIGlkPSJXNU0wTXBDZWhpSHpyZVN6TlRjemtjOWQiPz4gPHg6eG1wbWV0YSB4bWxuczp4PSJhZG9iZTpuczptZXRhLyIgeDp4bXB0az0iQWRvYmUgWE1QIENvcmUgNS42LWMxNDUgNzkuMTYzNDk5LCAyMDE4LzA4LzEzLTE2OjQwOjIyICAgICAgICAiPiA8cmRmOlJERiB4bWxuczpyZGY9Imh0dHA6Ly93d3cudzMub3JnLzE5OTkvMDIvMjItcmRmLXN5bnRheC1ucyMiPiA8cmRmOkRlc2NyaXB0aW9uIHJkZjphYm91dD0iIiB4bWxuczp4bXA9Imh0dHA6Ly9ucy5hZG9iZS5jb20veGFwLzEuMC8iIHhtbG5zOmRjPSJodHRwOi8vcHVybC5vcmcvZGMvZWxlbWVudHMvMS4xLyIgeG1sbnM6cGhvdG9zaG9wPSJodHRwOi8vbnMuYWRvYmUuY29tL3Bob3Rvc2hvcC8xLjAvIiB4bWxuczp4bXBNTT0iaHR0cDovL25zLmFkb2JlLmNvbS94YXAvMS4wL21tLyIgeG1sbnM6c3RFdnQ9Imh0dHA6Ly9ucy5hZG9iZS5jb20veGFwLzEuMC9zVHlwZS9SZXNvdXJjZUV2ZW50IyIgeG1wOkNyZWF0b3JUb29sPSJBZG9iZSBQaG90b3Nob3AgQ0MgMjAxOSAoV2luZG93cykiIHhtcDpDcmVhdGVEYXRlPSIyMDIzLTA3LTI4VDEwOjA3OjI2KzA4OjAwIiB4bXA6TW9kaWZ5RGF0ZT0iMjAyMy0wNy0yOFQxMDoxMDozOCswODowMCIgeG1wOk1ldGFkYXRhRGF0ZT0iMjAyMy0wNy0yOFQxMDoxMDozOCswODowMCIgZGM6Zm9ybWF0PSJpbWFnZS9wbmciIHBob3Rvc2hvcDpDb2xvck1vZGU9IjMiIHBob3Rvc2hvcDpJQ0NQcm9maWxlPSJzUkdCIElFQzYxOTY2LTIuMSIgeG1wTU06SW5zdGFuY2VJRD0ieG1wLmlpZDo1YTFiNjdlMy1mNDQ5LWE3NDItODc2ZC01MzlkYzg3YTM0MjMiIHhtcE1NOkRvY3VtZW50SUQ9InhtcC5kaWQ6NmNhMzk0ZjAtYzQ0OS0yOTRlLWIxNWQtMmIyNzFjZDUzOTRiIiB4bXBNTTpPcmlnaW5hbERvY3VtZW50SUQ9InhtcC5kaWQ6NmNhMzk0ZjAtYzQ0OS0yOTRlLWIxNWQtMmIyNzFjZDUzOTRiIj4gPHhtcE1NOkhpc3Rvcnk+IDxyZGY6U2VxPiA8cmRmOmxpIHN0RXZ0OmFjdGlvbj0iY3JlYXRlZCIgc3RFdnQ6aW5zdGFuY2VJRD0ieG1wLmlpZDo2Y2EzOTRmMC1jNDQ5LTI5NGUtYjE1ZC0yYjI3MWNkNTM5NGIiIHN0RXZ0OndoZW49IjIwMjMtMDctMjhUMTA6MDc6MjYrMDg6MDAiIHN0RXZ0OnNvZnR3YXJlQWdlbnQ9IkFkb2JlIFBob3Rvc2hvcCBDQyAyMDE5IChXaW5kb3dzKSIvPiA8cmRmOmxpIHN0RXZ0OmFjdGlvbj0ic2F2ZWQiIHN0RXZ0Omluc3RhbmNlSUQ9InhtcC5paWQ6NWExYjY3ZTMtZjQ0OS1hNzQyLTg3NmQtNTM5ZGM4N2EzNDIzIiBzdEV2dDp3aGVuPSIyMDIzLTA3LTI4VDEwOjEwOjM4KzA4OjAwIiBzdEV2dDpzb2Z0d2FyZUFnZW50PSJBZG9iZSBQaG90b3Nob3AgQ0MgMjAxOSAoV2luZG93cykiIHN0RXZ0OmNoYW5nZWQ9Ii8iLz4gPC9yZGY6U2VxPiA8L3htcE1NOkhpc3Rvcnk+IDwvcmRmOkRlc2NyaXB0aW9uPiA8L3JkZjpSREY+IDwveDp4bXBtZXRhPiA8P3hwYWNrZXQgZW5kPSJyIj8+oZMm4wAABdxJREFUeJztm1tsFFUYx3+zLZdSoC0FpFwsUMAIGBRQDBiQSwxKQsQHE0WJiRofNPpkTPTBxGh8IDEmxgQTjbcYNdGIEbwgGFBuItAiCMhNKlJLaSnQ0t3x4ZuTs9PZ3dndmZ0t7j/ZZGfOd77vnP+c+c53LlNgjBEjRoxRi7zRFiDGKGJk1QOyVQnYBMwHLgGvAj9lS5gcxTTgJLABmAP8DWwEzmVDoFyc/gbgHHAvcAR4FtgHzAc+BZYMt1C5aAHzgM+BR4DTwCpgL/AE8B0wdTiFymULAFgIfAMsw1jDRuAHYNJwCZMLFuCgCPgQeAYoB1qBN4C3gfahECJXLcBBMfAa8AJQCPQAW4FXgKZsCpLLFuCgBHgdWI+xhm5gG/AiUJ8NIUaKBTgoBTYDzwFFQBfwLvA8cCWTDY80C3BQBmwBnsNYQyfwHvAscDnshkaqBTgoBzYBGzDW0AG8j7GG2jAbGKkW4KAS2Ao8jbGGduADjDXUhFH5SLcAB1XANuApjDW0AR9iJk21QSsdLRbgYCzwOPAkUAK0AB8DzwDnB6pstFmAg7HAE8AqoBj4F9gBrAXO9lfJaLUAB+OA1cDjmDHRDOwEHgXO9FV4tFuAg/HAU8BKzJhoAnYBK4A/4wtGAoKoGCgBKoBxQCPQEPesCHgYWIEZEw3A18CDwCmvEJGAYFQELAEexUjfCBwGfgb+Ay4CU4B7gAcwA6IeOAA8BPwaCQhGRcBi4GFgEcYKTgC/AH8C1zCDvxhzZrgXuA+4DtQAB4H7gdORgGBUBCwEHgLuw1jAaeAocBy4gpmLFAOTgTuAezADvg44AiwFjkUCglERMA9YDizFWMA54ARwEriIcXsLgInALGABMA+oFRk+wVhDJCAYFQGzgGXAYmAGJvLzJ3AKqMW4vXlAFTATmA3MwQyGWuAYsBj4LRIQjIqAGcBSzOSoCuP3/w6cAeowA74Ks+U1HZiKsYALwK/AImBfJCAYFQHTgAcxA34CZsv7LHAeaMS4vRMxVjAZmIixgIvASeB7YGEkIBhNB+YCC4E7MZbQgJn8XMZYQAVm8jMBGI+xgFrgNPBDJCAYTQbuw0x+pmDc3nrgKsYCyjCTnwrMWKjDWMDvwKFIQDAqBhZgBvwsjNt7DWMBPZiQdxlm8lOOmQecB/4AfowEBKMiYD5mwM/G+P3NmMlPL2byU4aZ/FzCWMBp4MdIQDAqAuZiJj/zMG5vK8btzcNYQClm8nMRYwG/AD9FAoJREXA3ZvJzF8bv78BMfgowbm8JZvJzAWMBvwE/RwKCURFwJ2byswDj9nZhJj95GMsvxkx+zmMs4BfgaCQgGBUBszGTn4UYt7cHM/nJx1h+IWbyU4OxgGPAL5GAYFQEzMJMfhZh/P5ejOXnYSy/ADP5OYexgOPAkUhAMCoCZmImP4sxbm8fxvLzMJZfgJn81GAs4ATwayQgGBUBMzCTnyUYv78fY/l5GMsvwEx+ajAWcBL4LRIQjIqA6ZjJz1KM2zuAsfx8jOXnYyY/NRgLOAUcjwQEoyJgGmbyswzj9x/EWH4+xvLzMJOfGowFnAZ+jwQEoyJgKmbyswzj9h7CWH4BxvLzMJOfGowFnAGORwKCURFQjZn8LMO4vYcxll+Asfx8zOSnBmMBZ4ETkYBgVARMwUx+lmPc3iMYyy/AWH4+ZvJzFmMBZ4GTkYBgVARMxkx+lmPc3qMYyy/AWH4+ZvJzFmMB54CTkYBgVARMwkx+VmDc3mMYyy/AWH4+ZvJzDmMB54FTkYBgVARMxEx+VmDc3uMYyy/AWH4+ZvJzHmMBF4DTkYBgVARMwEx+HsK4vScwll+Isfx8zOTnAsYCLgJnIgHBqAgYj5n8rMS4vScxll+Isfx8zOTnAsYCLgF/RQKCURFQhZn8rMS4vacwll+Isfx8zOTnEsYCLgN/RwKCURFQiZn8rMK4vacxll+Isfx8zOTnMsYC6oAzkYBgVASMw0x+VmHc3jWkWn5dJCAYFQEVmMnPKozb+1wkIBgVAeWYyc8q4LNIQIwYMWKMXvwPZk5taYLyYV4AAAAASUVORK5CYII=
"""

class RedirectText:
    """重定向输出到GUI文本框"""
    def __init__(self, text_widget):
        self.text_widget = text_widget
        self.queue = queue.Queue()
        self.running = True
        self.update_thread = threading.Thread(target=self._update_text, daemon=True)
        self.update_thread.start()

    def write(self, string):
        self.queue.put(string)

    def flush(self):
        pass

    def _update_text(self):
        while self.running:
            try:
                while True:
                    string = self.queue.get_nowait()
                    self.text_widget.insert(tk.END, string)
                    self.text_widget.see(tk.END)
                    self.text_widget.update_idletasks()
            except queue.Empty:
                self.text_widget.after(100, lambda: None)

    def stop(self):
        self.running = False

class SrtTTSGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("SRT字幕语音合成工具 - 专业版")
        self.root.geometry("800x700")
        
        # 设置应用图标
        self.set_app_icon()
        
        # 设置深色主题
        self.configure_dark_theme()
        
        # 创建主框架
        self.main_frame = ttk.Frame(root, padding="10", style="Dark.TFrame")
        self.main_frame.grid(row=0, column=0, sticky="nsew")
        
        # 配置网格权重
        root.columnconfigure(0, weight=1)
        root.rowconfigure(0, weight=1)
        self.main_frame.columnconfigure(1, weight=1)
        
        # 创建变量
        self.input_dir = tk.StringVar()
        self.output_dir = tk.StringVar()
        self.subtitle_suffix = tk.StringVar(value="_cn")
        self.audio_suffix = tk.StringVar(value="")
        self.audio_codec = tk.StringVar(value="aac")
        self.audio_quality = tk.StringVar(value="-vbr 3")
        self.audio_format = tk.StringVar(value="m4a")
        self.speech_speed = tk.StringVar(value="moderate")
        self.speech_pitch = tk.StringVar(value="moderate")
        self.voice_role = tk.StringVar(value="male")
        self.clone_role = tk.StringVar(value="")
        self.verbose = tk.BooleanVar(value=True)
        self.speed_detection = tk.BooleanVar(value=True)
        self.speed_adjust = tk.BooleanVar(value=False)
        self.alternative = tk.IntVar(value=0)
        
        # 创建界面
        self.create_widgets()
        
        # 重定向输出
        self.redirect = RedirectText(self.log_text)
        sys.stdout = self.redirect
        
        # 处理线程
        self.processing_thread = None
        self.is_processing = False
        
        # 添加标题栏
        self.create_title_bar()

    def set_app_icon(self):
        """设置应用图标"""
        try:
            # 解码Base64图标数据
            icon_data = base64.b64decode(ICON_DATA)
            icon_image = Image.open(BytesIO(icon_data))
            
            # 转换为PhotoImage
            icon_photo = ImageTk.PhotoImage(icon_image)
            
            # 设置窗口图标
            self.root.iconphoto(True, icon_photo)
        except Exception:
            # 如果设置图标失败，静默忽略
            pass
    
    def create_title_bar(self):
        """创建标题栏"""
        # 创建标题栏框架
        title_frame = ttk.Frame(self.main_frame, style="Dark.TFrame")
        title_frame.grid(row=0, column=0, columnspan=2, sticky="we", pady=(0, 10))
        
        # 标题标签
        title_label = ttk.Label(title_frame, text="SRT字幕语音合成工具 - 专业版", 
                               font=("Arial", 14, "bold"), foreground=ACCENT_COLOR, background=DARK_BG)
        title_label.pack(side=tk.LEFT, padx=10, pady=5)
        
        # 添加分隔线
        separator = ttk.Separator(self.main_frame, orient="horizontal")
        separator.grid(row=1, column=0, columnspan=2, sticky="we", pady=(0, 10))
        
        # 调整其他组件的行索引
        for widget in self.main_frame.grid_slaves():
            if int(widget.grid_info()["row"]) > 0:
                widget.grid_configure(row=int(widget.grid_info()["row"]) + 2)

    def configure_dark_theme(self):
        """配置深色主题样式"""
        self.root.configure(bg=DARK_BG)
        
        style = ttk.Style()
        style.theme_use('clam')
        
        # 配置主要样式
        style.configure("TFrame", background=DARK_BG)
        style.configure("Dark.TFrame", background=DARK_BG)
        style.configure("TLabel", background=DARK_BG, foreground=DARK_FG)
        style.configure("TButton", background=BUTTON_BG, foreground=DARK_FG, borderwidth=1, focusthickness=0)
        style.map("TButton", 
                  background=[("active", BUTTON_ACTIVE_BG), ("pressed", ACCENT_COLOR)],
                  foreground=[("active", DARK_FG)])
        
        # 配置标签框架样式
        style.configure("TLabelframe", background=DARK_BG, foreground=DARK_FG)
        style.configure("TLabelframe.Label", background=DARK_BG, foreground=ACCENT_COLOR, font=("Arial", 9, "bold"))
        
        # 配置输入框样式
        style.configure("TEntry", fieldbackground=ENTRY_BG, foreground=ENTRY_FG, bordercolor=BORDER_COLOR)
        style.map("TEntry", fieldbackground=[("focus", ENTRY_BG)])
        
        # 配置组合框样式
        style.configure("TCombobox", fieldbackground=ENTRY_BG, background=BUTTON_BG, foreground=ENTRY_FG, arrowcolor=DARK_FG)
        style.map("TCombobox", 
                  fieldbackground=[("readonly", ENTRY_BG)],
                  selectbackground=[("readonly", HIGHLIGHT_BG)])
        
        # 配置复选框样式
        style.configure("TCheckbutton", background=DARK_BG, foreground=DARK_FG)
        style.map("TCheckbutton", 
                  background=[("active", DARK_BG)],
                  foreground=[("active", ACCENT_COLOR)])
        
        # 配置笔记本样式
        style.configure("TNotebook", background=DARK_BG, tabmargins=[2, 5, 2, 0])
        style.configure("TNotebook.Tab", background=SECONDARY_BG, foreground=DARK_FG, padding=[10, 2])
        style.map("TNotebook.Tab", 
                  background=[("selected", ACCENT_COLOR)],
                  foreground=[("selected", DARK_FG)])
        
        # 配置滚动条样式
        style.configure("Vertical.TScrollbar", background=SECONDARY_BG, arrowcolor=DARK_FG, troughcolor=DARK_BG, bordercolor=BORDER_COLOR)
        style.map("Vertical.TScrollbar", 
                  background=[("active", BUTTON_ACTIVE_BG), ("pressed", ACCENT_COLOR)])
        
        # 创建自定义按钮样式
        style.configure("Accent.TButton", background=ACCENT_COLOR, foreground=DARK_FG)
        style.map("Accent.TButton",
                 background=[("active", BUTTON_ACTIVE_BG), ("pressed", ACCENT_COLOR)])
        
        # 配置分隔线样式
        style.configure("TSeparator", background=BORDER_COLOR)

    def create_widgets(self):
        # 创建notebook用于分页
        notebook = ttk.Notebook(self.main_frame)
        notebook.grid(row=0, column=0, columnspan=2, sticky="nsew", pady=(0, 10))
        
        # 主设置页面
        main_frame = ttk.Frame(notebook, style="Dark.TFrame")
        notebook.add(main_frame, text="主设置")
        
        # 输入输出设置
        self.create_io_frame(main_frame)
        
        # 音频设置
        self.create_audio_frame(main_frame)
        
        # 语音设置
        self.create_speech_frame(main_frame)
        
        # 高级设置页面
        advanced_frame = ttk.Frame(notebook, style="Dark.TFrame")
        notebook.add(advanced_frame, text="高级设置")
        
        # 高级选项
        self.create_advanced_frame(advanced_frame)
        
        # 角色选择页面
        roles_frame = ttk.Frame(notebook, style="Dark.TFrame")
        notebook.add(roles_frame, text="角色选择")
        
        # 角色设置
        self.create_roles_frame(roles_frame)
        
        # 控制按钮
        self.create_control_frame()
        
        # 日志区域
        self.create_log_frame()

    def create_io_frame(self, parent):
        # 输入输出设置框架
        io_frame = ttk.LabelFrame(parent, text="输入输出设置", padding="10")
        io_frame.grid(row=0, column=0, columnspan=2, sticky="we", pady=(0, 10))
        io_frame.columnconfigure(1, weight=1)
        
        # 输入目录
        ttk.Label(io_frame, text="输入目录:").grid(row=0, column=0, sticky="w", pady=5)
        entry_input = ttk.Entry(io_frame, textvariable=self.input_dir, width=50)
        entry_input.grid(row=0, column=1, sticky="we", padx=(5, 5), pady=5)
        ttk.Button(io_frame, text="浏览", command=self.browse_input_dir).grid(row=0, column=2, pady=5)
        
        # 输出目录
        ttk.Label(io_frame, text="输出目录:").grid(row=1, column=0, sticky="w", pady=5)
        entry_output = ttk.Entry(io_frame, textvariable=self.output_dir, width=50)
        entry_output.grid(row=1, column=1, sticky="we", padx=(5, 5), pady=5)
        ttk.Button(io_frame, text="浏览", command=self.browse_output_dir).grid(row=1, column=2, pady=5)
        
        # 字幕后缀
        ttk.Label(io_frame, text="字幕后缀:").grid(row=2, column=0, sticky="w", pady=5)
        ttk.Entry(io_frame, textvariable=self.subtitle_suffix, width=20).grid(row=2, column=1, sticky="w", padx=(5, 0), pady=5)

    def create_audio_frame(self, parent):
        # 音频设置框架
        audio_frame = ttk.LabelFrame(parent, text="音频设置", padding="10")
        audio_frame.grid(row=1, column=0, columnspan=2, sticky="we", pady=(0, 10))
        audio_frame.columnconfigure(1, weight=1)
        
        # 音频格式
        ttk.Label(audio_frame, text="音频格式:").grid(row=0, column=0, sticky="w", pady=5)
        format_combo = ttk.Combobox(audio_frame, textvariable=self.audio_format, values=["m4a", "mp3", "wav", "flac"], width=15)
        format_combo.grid(row=0, column=1, sticky="w", padx=(5, 0), pady=5)
        
        # 音频编码
        ttk.Label(audio_frame, text="音频编码:").grid(row=0, column=2, sticky="w", padx=(20, 0), pady=5)
        codec_combo = ttk.Combobox(audio_frame, textvariable=self.audio_codec, values=["aac", "mp3", "pcm_s16le"], width=15)
        codec_combo.grid(row=0, column=3, sticky="w", padx=(5, 0), pady=5)
        
        # 音频质量
        ttk.Label(audio_frame, text="音频质量:").grid(row=1, column=0, sticky="w", pady=5)
        ttk.Entry(audio_frame, textvariable=self.audio_quality, width=20).grid(row=1, column=1, sticky="w", padx=(5, 0), pady=5)
        
        # 音频后缀
        ttk.Label(audio_frame, text="音频后缀:").grid(row=1, column=2, sticky="w", padx=(20, 0), pady=5)
        ttk.Entry(audio_frame, textvariable=self.audio_suffix, width=20).grid(row=1, column=3, sticky="w", padx=(5, 0), pady=5)

    def create_speech_frame(self, parent):
        # 语音设置框架
        speech_frame = ttk.LabelFrame(parent, text="语音设置", padding="10")
        speech_frame.grid(row=2, column=0, columnspan=2, sticky="we", pady=(0, 10))
        speech_frame.columnconfigure(1, weight=1)
        
        # 语速
        ttk.Label(speech_frame, text="语速:").grid(row=0, column=0, sticky="w", pady=5)
        speed_combo = ttk.Combobox(speech_frame, textvariable=self.speech_speed, 
                                  values=["very_low", "low", "moderate", "high", "very_high"], width=15)
        speed_combo.grid(row=0, column=1, sticky="w", padx=(5, 0), pady=5)
        
        # 音高
        ttk.Label(speech_frame, text="音高:").grid(row=0, column=2, sticky="w", padx=(20, 0), pady=5)
        pitch_combo = ttk.Combobox(speech_frame, textvariable=self.speech_pitch, 
                                  values=["very_low", "low", "moderate", "high", "very_high"], width=15)
        pitch_combo.grid(row=0, column=3, sticky="w", padx=(5, 0), pady=5)
        
        # 语音角色
        ttk.Label(speech_frame, text="语音角色:").grid(row=1, column=0, sticky="w", pady=5)
        role_combo = ttk.Combobox(speech_frame, textvariable=self.voice_role, 
                                 values=["male", "female", "child"], width=15)
        role_combo.grid(row=1, column=1, sticky="w", padx=(5, 0), pady=5)

    def create_advanced_frame(self, parent):
        # 高级设置框架
        advanced_frame = ttk.LabelFrame(parent, text="高级选项", padding="10")
        advanced_frame.grid(row=0, column=0, columnspan=2, sticky="we", pady=(0, 10))
        advanced_frame.columnconfigure(1, weight=1)
        
        # 详细输出
        ttk.Checkbutton(advanced_frame, text="详细输出", variable=self.verbose).grid(row=0, column=0, sticky="w", pady=5)
        
        # 语速探测
        ttk.Checkbutton(advanced_frame, text="语速探测", variable=self.speed_detection).grid(row=0, column=1, sticky="w", padx=(20, 0), pady=5)
        
        # 语音时长调整
        ttk.Checkbutton(advanced_frame, text="语音时长调整", variable=self.speed_adjust).grid(row=0, column=2, sticky="w", padx=(20, 0), pady=5)
        
        # 替代角色数量
        ttk.Label(advanced_frame, text="替代角色数量:").grid(row=1, column=0, sticky="w", pady=5)
        ttk.Spinbox(advanced_frame, from_=0, to=10, textvariable=self.alternative, width=10).grid(row=1, column=1, sticky="w", padx=(5, 0), pady=5)

    def create_roles_frame(self, parent):
        # 角色设置框架
        roles_frame = ttk.LabelFrame(parent, text="克隆角色设置", padding="10")
        roles_frame.grid(row=0, column=0, columnspan=2, sticky="we", pady=(0, 10))
        roles_frame.columnconfigure(1, weight=1)
        
        # 克隆角色
        ttk.Label(roles_frame, text="克隆角色:").grid(row=0, column=0, sticky="w", pady=5)
        self.clone_role_combo = ttk.Combobox(roles_frame, textvariable=self.clone_role, width=30)
        self.clone_role_combo.grid(row=0, column=1, sticky="we", padx=(5, 0), pady=5)
        
        # 刷新角色列表按钮
        ttk.Button(roles_frame, text="刷新角色列表", command=self.refresh_roles).grid(row=0, column=2, padx=(10, 0), pady=5)
        
        # 角色信息显示
        self.role_info_text = scrolledtext.ScrolledText(roles_frame, height=10, width=60, bg=ENTRY_BG, fg=ENTRY_FG, insertbackground=DARK_FG)
        self.role_info_text.grid(row=1, column=0, columnspan=3, sticky="we", pady=(10, 0))
        
        # 初始化角色列表
        self.refresh_roles()

    def create_control_frame(self):
        # 控制按钮框架
        control_frame = ttk.Frame(self.main_frame, style="Dark.TFrame")
        control_frame.grid(row=1, column=0, columnspan=2, pady=(0, 10))
        
        # 开始处理按钮
        self.start_button = ttk.Button(control_frame, text="开始处理", command=self.start_processing, style="Accent.TButton")
        self.start_button.pack(side=tk.LEFT, padx=(0, 10))
        
        # 停止处理按钮
        self.stop_button = ttk.Button(control_frame, text="停止处理", command=self.stop_processing, state=tk.DISABLED)
        self.stop_button.pack(side=tk.LEFT, padx=(0, 10))
        
        # 清空日志按钮
        ttk.Button(control_frame, text="清空日志", command=self.clear_log).pack(side=tk.LEFT, padx=(0, 10))
        
        # 打开输出目录按钮
        ttk.Button(control_frame, text="打开输出目录", command=self.open_output_dir).pack(side=tk.LEFT)

    def create_log_frame(self):
        # 日志框架
        log_frame = ttk.LabelFrame(self.main_frame, text="处理日志", padding="10")
        log_frame.grid(row=2, column=0, columnspan=2, sticky="nsew", pady=(0, 10))
        log_frame.columnconfigure(0, weight=1)
        log_frame.rowconfigure(0, weight=1)
        self.main_frame.rowconfigure(2, weight=1)
        
        # 日志文本框
        self.log_text = scrolledtext.ScrolledText(log_frame, height=15, width=80, bg=ENTRY_BG, fg=ACCENT_COLOR, insertbackground=DARK_FG)
        self.log_text.grid(row=0, column=0, sticky="nsew")

    def browse_input_dir(self):
        directory = filedialog.askdirectory(title="选择输入目录")
        if directory:
            self.input_dir.set(directory)
            # 如果输出目录为空，设置为输入目录
            if not self.output_dir.get():
                self.output_dir.set(directory)

    def browse_output_dir(self):
        directory = filedialog.askdirectory(title="选择输出目录")
        if directory:
            self.output_dir.set(directory)

    def refresh_roles(self):
        """刷新角色列表"""
        roles = []
        roles_dir = os.path.join("flashtts_data", "roles")
        
        if os.path.exists(roles_dir):
            for role_name in os.listdir(roles_dir):
                role_path = os.path.join(roles_dir, role_name)
                if os.path.isdir(role_path):
                    # 检查是否有参考音频文件
                    ref_audio = os.path.join(role_path, "reference_audio.wav")
                    if os.path.exists(ref_audio):
                        roles.append(role_name)
        
        self.clone_role_combo['values'] = roles
        
        # 更新角色信息显示
        self.update_role_info()

    def update_role_info(self):
        """更新角色信息显示"""
        selected_role = self.clone_role.get()
        if not selected_role:
            self.role_info_text.delete(1.0, tk.END)
            self.role_info_text.insert(tk.END, "请选择一个克隆角色查看详细信息")
            return
        
        role_dir = os.path.join("flashtts_data", "roles", selected_role)
        info = f"角色: {selected_role}\n"
        info += f"目录: {role_dir}\n\n"
        
        # 检查文件
        ref_audio = os.path.join(role_dir, "reference_audio.wav")
        ref_text = os.path.join(role_dir, "reference_text.txt")
        
        if os.path.exists(ref_audio):
            size = os.path.getsize(ref_audio)
            info += f"✓ 参考音频: {ref_audio}\n"
            info += f"  大小: {size} 字节\n"
        else:
            info += f"✗ 参考音频: 未找到\n"
        
        if os.path.exists(ref_text):
            with open(ref_text, 'r', encoding='utf-8') as f:
                text_content = f.read().strip()
            info += f"✓ 参考文本: {ref_text}\n"
            info += f"  内容: {text_content[:100]}{'...' if len(text_content) > 100 else ''}\n"
        else:
            info += f"✗ 参考文本: 未找到\n"
        
        self.role_info_text.delete(1.0, tk.END)
        self.role_info_text.insert(tk.END, info)

    def start_processing(self):
        """开始处理"""
        if self.is_processing:
            return
        
        # 验证输入
        if not self.input_dir.get():
            messagebox.showerror("错误", "请选择输入目录")
            return
        
        if not self.output_dir.get():
            messagebox.showerror("错误", "请选择输出目录")
            return
        
        # 检查输入目录是否存在
        if not os.path.exists(self.input_dir.get()):
            messagebox.showerror("错误", "输入目录不存在")
            return
        
        # 创建输出目录
        os.makedirs(self.output_dir.get(), exist_ok=True)
        
        # 更新UI状态
        self.start_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)
        self.is_processing = True
        
        # 在新线程中处理
        self.processing_thread = threading.Thread(target=self.process_files, daemon=True)
        self.processing_thread.start()

    def stop_processing(self):
        """停止处理"""
        if not self.is_processing:
            return
        
        self.is_processing = False
        self.start_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)
        
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 用户停止处理")

    def process_files(self):
        """处理文件"""
        try:
            # 创建SrtTTS实例
            tts = SrtTTS(
                input=self.input_dir.get(),
                output=self.output_dir.get(),
                subtitle_suffix=self.subtitle_suffix.get(),
                audio_suffix=self.audio_suffix.get(),
                audio_codec=self.audio_codec.get(),
                audio_quality=self.audio_quality.get(),
                audio_format=self.audio_format.get(),
                speech_speed=self.speech_speed.get(),
                speech_pitch=self.speech_pitch.get(),
                voice_role=self.voice_role.get(),
                clone_role=self.clone_role.get(),
                verbose=self.verbose.get(),
                speed_detection=self.speed_detection.get(),
                speed_adjust=self.speed_adjust.get(),
                alternative=self.alternative.get()
            )
            
            print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 开始处理SRT文件...")
            print(f"输入目录: {self.input_dir.get()}")
            print(f"输出目录: {self.output_dir.get()}")
            print(f"字幕后缀: {self.subtitle_suffix.get()}")
            print(f"音频格式: {self.audio_format.get()}")
            print(f"语速: {self.speech_speed.get()}")
            print(f"音高: {self.speech_pitch.get()}")
            print(f"语音角色: {self.voice_role.get()}")
            if self.clone_role.get():
                print(f"克隆角色: {self.clone_role.get()}")
            print("-" * 50)
            
            # 处理文件
            tts.process_srt_files()
            
            if self.is_processing:  # 检查是否被用户停止
                print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 处理完成!")
                messagebox.showinfo("完成", "SRT文件处理完成!")
            
        except Exception as e:
            print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 处理过程中出现错误: {str(e)}")
            messagebox.showerror("错误", f"处理过程中出现错误:\n{str(e)}")
        
        finally:
            # 恢复UI状态
            self.root.after(0, self.reset_ui_state)

    def reset_ui_state(self):
        """重置UI状态"""
        self.is_processing = False
        self.start_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)

    def clear_log(self):
        """清空日志"""
        self.log_text.delete(1.0, tk.END)

    def open_output_dir(self):
        """打开输出目录"""
        output_dir = self.output_dir.get()
        if output_dir and os.path.exists(output_dir):
            if sys.platform == "win32":
                os.startfile(output_dir)
            elif sys.platform == "darwin":
                os.system(f"open '{output_dir}'")
            else:
                os.system(f"xdg-open '{output_dir}'")
        else:
            messagebox.showwarning("警告", "输出目录不存在")

    def on_clone_role_change(self, event):
        """克隆角色选择改变时的回调"""
        self.update_role_info()

    def on_closing(self):
        """窗口关闭时的处理"""
        if self.is_processing:
            if messagebox.askokcancel("确认", "正在处理中，确定要退出吗?"):
                self.stop_processing()
                self.root.destroy()
        else:
            self.root.destroy()

def main():
    root = tk.Tk()
    app = SrtTTSGUI(root)
    
    # 绑定克隆角色选择事件
    app.clone_role_combo.bind('<<ComboboxSelected>>', app.on_clone_role_change)
    
    # 绑定窗口关闭事件
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    
    root.mainloop()

if __name__ == "__main__":
    main() 