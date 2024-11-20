import tkinter as tk
from tkinter import ttk
import pyautogui
import time
import random
import threading
import os
from itertools import cycle

class CustomStyle:
    BG_COLOR = "#FFFFFF"
    TEXT_COLOR = "#333333"
    BUTTON_COLOR = "#000000"  # 按钮黑色
    BUTTON_ACTIVE_COLOR = "#808080"  # 按钮点击后的灰色
    
    @staticmethod
    def apply_style():
        style = ttk.Style()
        style.theme_use('clam')
        
        # 配置按钮样式
        style.configure('Custom.TButton',
                      background=CustomStyle.BUTTON_COLOR,
                      foreground='white',  # 按钮文字颜色设为白色
                      padding=(20, 10))
        
        # 配置按钮激活状态的样式
        style.map('Custom.TButton',
                 background=[('active', CustomStyle.BUTTON_ACTIVE_COLOR),
                           ('disabled', CustomStyle.BUTTON_ACTIVE_COLOR)])

class KeepOnlineApp:
    def __init__(self, root):
        self.root = root
        self.root.title("值班小猫")
        self.root.geometry("400x600")
        self.root.configure(bg=CustomStyle.BG_COLOR)
        
        # 设置程序图标
        icon_path = os.path.join('assets', 'cat_icon.ico')
        if os.path.exists(icon_path):
            self.root.iconbitmap(icon_path)
        
        self.is_running = False
        self.thread = None
        self.cursor_thread = None
        
        # 检查文件是否存在
        files_to_check = ['background.png', 'start_btn_bg.png', 'stop_btn_bg.png']
        for file in files_to_check:
            path = os.path.join('assets', file)
            if os.path.exists(path):
                print(f"文件存在: {path}")
            else:
                print(f"文件不存在: {path}")
        
        # 修改背景图片加载和显示方式
        try:
            self.bg_image = tk.PhotoImage(file=os.path.join('assets', 'background.png'))
            self.bg_label = tk.Label(self.root, image=self.bg_image)
            self.bg_label.place(x=0, y=0, relwidth=1, relheight=1)
            self.bg_label.lower()  # 将背景置于底层
        except Exception as e:
            print(f"背景图片加载失败: {str(e)}")
            
        # 主容器需要设置透明背景
        self.main_frame = ttk.Frame(self.root, style='Transparent.TFrame')
        self.main_frame.pack(fill='both', expand=True, padx=20, pady=20)
        
        # 确保在创建任何组件之前应用样式
        CustomStyle.apply_style()
        
        self.create_settings_frame()
        self.create_control_buttons()
        self.create_status_display()
        
        # 加载光标动画
        self.cursor_frames = self.load_cursor_frames()
        
        # 修改默认移动距离
        self.distance.delete(0, tk.END)
        self.distance.insert(0, "500")  # 将默认值改为500
        
    def load_cursor_frames(self):
        frames = []
        for i in range(1, 3):
            cursor_path = os.path.join('assets', f'cat{i}.cur')
            if os.path.exists(cursor_path):
                # 转换为绝对路径并规范化
                abs_path = os.path.abspath(cursor_path)
                abs_path = abs_path.replace('\\', '/')
                frames.append(abs_path)
                print(f"已加载光标文件: {abs_path}")
            else:
                print(f"未找到光标文件: {cursor_path}")
        return frames
    
    def animate_cursor(self):
        if self.cursor_frames:
            print(f"找到光标文件: {len(self.cursor_frames)} 个")
            while self.is_running:
                for cursor in self.cursor_frames:
                    if not self.is_running:
                        break
                    try:
                        # 获取当前鼠标位置的窗口
                        x, y = pyautogui.position()
                        window_at_point = self.root.winfo_containing(x, y)
                        
                        # 如果鼠标在主窗口内
                        if window_at_point and window_at_point.winfo_toplevel() == self.root:
                            try:
                                # 直接使用已经处理好的路径
                                print(f"正在设置光标: {cursor}")
                                self.root.config(cursor=f'@{cursor}')
                            except Exception as e:
                                print(f"设置光标失败: {str(e)}")
                        else:
                            # 恢复默认光标
                            self.root.config(cursor='')
                    except Exception as e:
                        print(f"设置光标时出错: {str(e)}")
                    time.sleep(0.2)
    
    def create_settings_frame(self):
        settings_frame = ttk.LabelFrame(
            self.main_frame,
            text=" 小猫值班设置 ",
            style='Transparent.TLabelframe',  # 使用透明样式
            padding="15"
        )
        settings_frame.pack(fill="x", pady=(0, 15))
        
        # 标签和输入框也设置透明背景
        ttk.Label(settings_frame,
                 text="小猫移动间隔 (秒):",
                 background='').grid(row=0, column=0, pady=8)
        self.interval = ttk.Entry(settings_frame, width=10, style='Custom.TEntry')
        self.interval.insert(0, "20")
        self.interval.grid(row=0, column=1, pady=8, padx=(10, 0))
        
        ttk.Label(settings_frame,
                 text="小猫移动距离 (像素):",
                 background='').grid(row=1, column=0, pady=8)
        self.distance = ttk.Entry(settings_frame, width=10, style='Custom.TEntry')
        self.distance.insert(0, "3")
        self.distance.grid(row=1, column=1, pady=8, padx=(10, 0))
    
    def create_control_buttons(self):
        btn_frame = ttk.Frame(self.main_frame, style='Transparent.TFrame')
        btn_frame.pack(pady=20)
        
        self.start_btn = ttk.Button(
            btn_frame,
            text="开始打工",
            command=self.start,
            style='Custom.TButton',  # 使用自定义按钮样式
            width=25
        )
        self.start_btn.pack(side="top", pady=15)
        
        self.stop_btn = ttk.Button(
            btn_frame,
            text="停止打工",
            command=self.stop,
            style='Custom.TButton',  # 使用自定义按钮样式
            state="disabled",
            width=25
        )
        self.stop_btn.pack(side="top", pady=15)
    
    def create_status_display(self):
        self.status_text = tk.Text(
            self.main_frame,
            height=12,
            width=35,
            bg='white',  # 将空字符串改为 'white' 或 CustomStyle.BG_COLOR
            fg=CustomStyle.TEXT_COLOR,
            font=('Helvetica', 9),
            relief='solid',
            borderwidth=1
        )
        self.status_text.pack(pady=10)
        self.status_text.config(state="disabled")
    
    def update_status(self, message):
        self.status_text.config(state="normal")
        self.status_text.insert("end", message + "\n")
        self.status_text.see("end")
        self.status_text.config(state="disabled")
    
    def keep_active(self):
        while self.is_running:
            try:
                # 获取当前鼠标位置
                current_x, current_y = pyautogui.position()
                
                # 随机移动鼠标
                max_distance = int(self.distance.get())
                offset_x = random.randint(-max_distance, max_distance)
                offset_y = random.randint(-max_distance, max_distance)
                
                # 移动鼠标
                pyautogui.moveRel(offset_x, offset_y, duration=0.5)
                pyautogui.moveTo(current_x, current_y, duration=0.5)
                
                self.update_status(f"鼠标已移动 ({offset_x}, {offset_y})")
                
                # 等待指定时间
                time.sleep(float(self.interval.get()))
                
            except Exception as e:
                self.update_status(f"错误: {str(e)}")
                self.stop()
                break
    
    def start(self):
        try:
            interval = float(self.interval.get())
            distance = int(self.distance.get())
            if interval <= 0 or distance <= 0:
                raise ValueError("间隔时间和移动距离必须大于0喵！")
            
            self.is_running = True
            
            # 启动鼠标移动线程
            self.thread = threading.Thread(target=self.keep_active)
            self.thread.daemon = True
            self.thread.start()
            
            # 启动光标动画线程
            self.cursor_thread = threading.Thread(target=self.animate_cursor)
            self.cursor_thread.daemon = True
            self.cursor_thread.start()
            
            self.start_btn.config(state="disabled")
            self.stop_btn.config(state="normal")
            self.update_status("小猫已开始打工！")
            
        except ValueError as e:
            self.update_status(f"输入错误喵: {str(e)}")
    
    def stop(self):
        self.is_running = False
        if self.thread:
            self.thread.join(timeout=1.0)
        if self.cursor_thread:
            self.cursor_thread.join(timeout=1.0)
        self.root.config(cursor="")  # 恢复默认光标
        self.start_btn.config(state="normal")
        self.stop_btn.config(state="disabled")
        self.update_status("小猫休息了~")

if __name__ == "__main__":
    # 设置防止程序失控
    pyautogui.FAILSAFE = True
    
    root = tk.Tk()
    app = KeepOnlineApp(root)
    root.mainloop() 