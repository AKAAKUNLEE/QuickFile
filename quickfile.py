import os
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import json
import threading
import time
from datetime import datetime
import re
import subprocess
import platform
import shutil

class QuickFile:
    def __init__(self, root):
        self.root = root
        self.root.title("QuickFile - 快速启动器")
        self.root.geometry("900x650")
        self.root.resizable(True, True)
        
        # 设置中文字体支持
        self.style = ttk.Style()
        self.style.configure("TLabel", font=("SimHei", 10))
        self.style.configure("TButton", font=("SimHei", 10))
        self.style.configure("TEntry", font=("SimHei", 10))
        self.style.configure("Treeview", font=("SimHei", 10))
        
        # 数据存储
        self.file_index = {}          # 文件索引 {文件名: [文件路径]}
        self.apps_index = {}          # 应用程序索引 {应用名: 路径}
        self.workspaces = {}          # 工作区配置
        self.custom_commands = {}     # 自定义命令
        self.search_results = []      # 当前搜索结果
        self.history = []             # 搜索历史
        self.max_history = 50         # 最大历史记录数
        
        # 文件路径
        self.data_dir = os.path.join(os.path.expanduser("~"), ".quickfile")
        self.index_file = os.path.join(self.data_dir, "file_index.json")
        self.apps_file = os.path.join(self.data_dir, "apps_index.json")
        self.workspaces_file = os.path.join(self.data_dir, "workspaces.json")
        self.commands_file = os.path.join(self.data_dir, "commands.json")
        self.history_file = os.path.join(self.data_dir, "history.json")
        
        # 排除配置
        self.excluded_dirs = {
            "System Volume Information", "$Recycle.Bin", "Windows", 
            "Program Files", "Program Files (x86)", "AppData"
        }
        self.excluded_extensions = {
            ".sys", ".dll", ".exe", ".com", ".tmp", ".log", ".bin", 
            ".msi", ".cab", ".dat", ".ini", ".db", ".sqlite"
        }
        
        # 创建数据目录
        if not os.path.exists(self.data_dir):
            os.makedirs(self.data_dir)
        
        # 加载数据
        self.load_all_data()
        
        # 创建界面
        self.create_widgets()
        
        # 启动索引线程
        if not self.file_index or not self.apps_index:
            self.start_indexing()
    
    def load_all_data(self):
        """加载所有配置数据"""
        self.load_file_index()
        self.load_apps_index()
        self.load_workspaces()
        self.load_custom_commands()
        self.load_history()
    
    def create_widgets(self):
        """创建用户界面"""
        # 顶部搜索区域
        top_frame = ttk.Frame(self.root, padding=10)
        top_frame.pack(fill=tk.X)
        
        # 搜索类型选择
        ttk.Label(top_frame, text="搜索类型:").pack(side=tk.LEFT, padx=5)
        self.search_type = tk.StringVar(value="all")
        search_types = [("全部", "all"), ("文件", "file"), ("应用", "app"), 
                        ("工作区", "workspace"), ("命令", "command")]
        
        for text, value in search_types:
            ttk.Radiobutton(top_frame, text=text, variable=self.search_type, value=value).pack(side=tk.LEFT, padx=5)
        
        # 搜索框
        self.search_var = tk.StringVar()
        self.search_entry = ttk.Entry(top_frame, textvariable=self.search_var, width=50)
        self.search_entry.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        self.search_entry.bind("<Return>", self.on_search)
        self.search_entry.bind("<Down>", self.focus_results)
        
        # 搜索按钮
        self.search_btn = ttk.Button(top_frame, text="搜索", command=self.on_search)
        self.search_btn.pack(side=tk.LEFT, padx=5)
        
        # 状态栏
        status_frame = ttk.Frame(self.root, padding=5)
        status_frame.pack(fill=tk.X)
        
        self.status_var = tk.StringVar()
        self.status_var.set("准备就绪")
        self.status_label = ttk.Label(status_frame, textvariable=self.status_var, foreground="blue")
        self.status_label.pack(side=tk.LEFT)
        
        self.progress = ttk.Progressbar(status_frame, mode="indeterminate", length=200)
        
        # 结果显示区域
        results_frame = ttk.PanedWindow(self.root, orient=tk.HORIZONTAL)
        results_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # 左侧面板 - 工作区和历史
        left_frame = ttk.LabelFrame(results_frame, text="工作区/历史")
        results_frame.add(left_frame, weight=1)
        
        # 工作区选项卡
        workspace_frame = ttk.Frame(left_frame)
        workspace_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        ttk.Label(workspace_frame, text="工作区:").pack(anchor=tk.W)
        self.workspace_listbox = tk.Listbox(workspace_frame, font=("SimHei", 10), height=8)
        self.workspace_listbox.pack(fill=tk.X, padx=5, pady=5)
        self.workspace_listbox.bind("<Double-1>", self.on_workspace_select)
        
        workspace_btn_frame = ttk.Frame(workspace_frame)
        workspace_btn_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Button(workspace_btn_frame, text="新建", command=self.create_workspace).pack(side=tk.LEFT, padx=2)
        ttk.Button(workspace_btn_frame, text="删除", command=self.delete_workspace).pack(side=tk.LEFT, padx=2)
        ttk.Button(workspace_btn_frame, text="添加到工作区", command=self.add_to_workspace).pack(side=tk.LEFT, padx=2)
        
        # 历史记录
        ttk.Label(left_frame, text="搜索历史:").pack(anchor=tk.W, padx=5)
        self.history_listbox = tk.Listbox(left_frame, font=("SimHei", 10))
        self.history_listbox.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.history_listbox.bind("<Double-1>", self.on_history_select)
        
        # 右侧面板 - 搜索结果
        right_frame = ttk.LabelFrame(results_frame, text="搜索结果")
        results_frame.add(right_frame, weight=3)
        
        columns = ("name", "type", "path", "info")
        self.results_tree = ttk.Treeview(right_frame, columns=columns, show="headings")
        self.results_tree.heading("name", text="名称")
        self.results_tree.heading("type", text="类型")
        self.results_tree.heading("path", text="路径/命令")
        self.results_tree.heading("info", text="信息")
        
        self.results_tree.column("name", width=150)
        self.results_tree.column("type", width=80, anchor=tk.CENTER)
        self.results_tree.column("path", width=300)
        self.results_tree.column("info", width=120)
        
        self.results_tree.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.results_tree.bind("<Double-1>", self.on_double_click)
        self.results_tree.bind("<Return>", self.on_double_click)
        self.results_tree.bind("<Up>", self.on_tree_key)
        self.results_tree.bind("<Down>", self.on_tree_key)
        
        # 更新UI数据
        self.update_workspace_display()
        self.update_history_display()
    
    # 索引管理功能
    def load_file_index(self):
        """加载文件索引"""
        try:
            if os.path.exists(self.index_file):
                with open(self.index_file, 'r', encoding='utf-8') as f:
                    self.file_index = json.load(f)
                self.status_var.set(f"已加载文件索引，包含 {len(self.file_index)} 个文件")
        except Exception as e:
            print(f"加载文件索引失败: {e}")
            self.file_index = {}
    
    def load_apps_index(self):
        """加载应用程序索引"""
        try:
            if os.path.exists(self.apps_file):
                with open(self.apps_file, 'r', encoding='utf-8') as f:
                    self.apps_index = json.load(f)
                self.status_var.set(f"已加载应用索引，包含 {len(self.apps_index)} 个应用")
        except Exception as e:
            print(f"加载应用索引失败: {e}")
            self.apps_index = {}
    
    def save_file_index(self):
        """保存文件索引"""
        try:
            with open(self.index_file, 'w', encoding='utf-8') as f:
                json.dump(self.file_index, f, ensure_ascii=False, indent=2)
            self.status_var.set(f"文件索引已保存，包含 {len(self.file_index)} 个文件")
        except Exception as e:
            print(f"保存文件索引失败: {e}")
    
    def save_apps_index(self):
        """保存应用程序索引"""
        try:
            with open(self.apps_file, 'w', encoding='utf-8') as f:
                json.dump(self.apps_index, f, ensure_ascii=False, indent=2)
            self.status_var.set(f"应用索引已保存，包含 {len(self.apps_index)} 个应用")
        except Exception as e:
            print(f"保存应用索引失败: {e}")
    
    def start_indexing(self):
        """启动索引线程"""
        self.status_var.set("正在建立索引...")
        self.progress.start()
        self.index_thread = threading.Thread(target=self.build_all_indexes)
        self.index_thread.daemon = True
        self.index_thread.start()
    
    def build_all_indexes(self):
        """构建所有索引"""
        start_time = time.time()
        
        # 构建文件索引
        self.build_file_index()
        self.save_file_index()
        
        # 构建应用程序索引
        self.build_apps_index()
        self.save_apps_index()
        
        end_time = time.time()
        self.progress.stop()
        self.status_var.set(f"索引完成，共耗时 {end_time - start_time:.2f} 秒")
    
    def build_file_index(self):
        """构建文件索引"""
        count = 0
        self.file_index = {}
        
        # 获取所有磁盘驱动器
        if os.name == 'nt':  # Windows系统
            import win32api
            drives = win32api.GetLogicalDriveStrings()
            drives = drives.split('\000')[:-1]
        else:  # Linux/Unix/Mac系统
            drives = ['/']
        
        for drive in drives:
            try:
                for root, dirs, files in os.walk(drive):
                    # 排除系统目录
                    dirs[:] = [d for d in dirs if d not in self.excluded_dirs and not d.startswith('.')]
                    
                    for file in files:
                        # 排除特定扩展名的文件
                        ext = os.path.splitext(file)[1].lower()
                        if ext in self.excluded_extensions:
                            continue
                        
                        file_path = os.path.join(root, file)
                        # 排除大文件和无法访问的文件
                        try:
                            if os.path.getsize(file_path) > 1024 * 1024 * 100:  # 大于100MB
                                continue
                        except (PermissionError, OSError):
                            continue
                        
                        # 更新索引
                        if file not in self.file_index:
                            self.file_index[file] = []
                        self.file_index[file].append(file_path)
                        
                        count += 1
                        if count % 1000 == 0:
                            self.status_var.set(f"已索引 {count} 个文件...")
            except Exception as e:
                print(f"索引 {drive} 时出错: {e}")
    
    def build_apps_index(self):
        """构建应用程序索引"""
        self.apps_index = {}
        count = 0
        
        if platform.system() == "Windows":
            # Windows应用程序搜索
            app_dirs = [
                os.path.join(os.environ["ProgramFiles"], "Common Files"),
                os.path.join(os.environ["ProgramFiles"]),
                os.path.join(os.environ.get("ProgramFiles(x86)", "")),
                os.path.join(os.environ["LOCALAPPDATA"], "Programs")
            ]
            
            for app_dir in app_dirs:
                if not os.path.exists(app_dir):
                    continue
                
                try:
                    for root, dirs, files in os.walk(app_dir):
                        for file in files:
                            if file.endswith(".exe") or file.endswith(".lnk"):
                                app_name = os.path.splitext(file)[0]
                                app_path = os.path.join(root, file)
                                
                                if app_name not in self.apps_index:
                                    self.apps_index[app_name] = app_path
                                    count += 1
                except Exception as e:
                    print(f"索引应用程序时出错: {e}")
        
        elif platform.system() == "Darwin":  # macOS
            # macOS应用程序搜索
            app_dirs = ["/Applications", os.path.expanduser("~/Applications")]
            
            for app_dir in app_dirs:
                if not os.path.exists(app_dir):
                    continue
                
                try:
                    for app in os.listdir(app_dir):
                        if app.endswith(".app"):
                            app_name = os.path.splitext(app)[0]
                            app_path = os.path.join(app_dir, app)
                            
                            if app_name not in self.apps_index:
                                self.apps_index[app_name] = app_path
                                count += 1
                except Exception as e:
                    print(f"索引应用程序时出错: {e}")
        
        else:  # Linux
            # Linux应用程序搜索
            app_dirs = ["/usr/bin", "/bin", "/usr/local/bin"]
            
            for app_dir in app_dirs:
                if not os.path.exists(app_dir):
                    continue
                
                try:
                    for app in os.listdir(app_dir):
                        app_path = os.path.join(app_dir, app)
                        if os.path.isfile(app_path) and os.access(app_path, os.X_OK):
                            if app not in self.apps_index:
                                self.apps_index[app] = app_path
                                count += 1
                except Exception as e:
                    print(f"索引应用程序时出错: {e}")
        
        self.status_var.set(f"已索引 {count} 个应用程序")
    
    # 工作区管理功能
    def load_workspaces(self):
        """加载工作区配置"""
        try:
            if os.path.exists(self.workspaces_file):
                with open(self.workspaces_file, 'r', encoding='utf-8') as f:
                    self.workspaces = json.load(f)
        except Exception as e:
            print(f"加载工作区配置失败: {e}")
            self.workspaces = {}
    
    def save_workspaces(self):
        """保存工作区配置"""
        try:
            with open(self.workspaces_file, 'w', encoding='utf-8') as f:
                json.dump(self.workspaces, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"保存工作区配置失败: {e}")
    
    def update_workspace_display(self):
        """更新工作区显示"""
        self.workspace_listbox.delete(0, tk.END)
        for workspace in self.workspaces.keys():
            self.workspace_listbox.insert(tk.END, workspace)
    
    def create_workspace(self):
        """创建新工作区"""
        ws_name = tk.simpledialog.askstring("创建工作区", "请输入工作区名称:")
        if ws_name and ws_name.strip():
            ws_name = ws_name.strip()
            if ws_name not in self.workspaces:
                self.workspaces[ws_name] = []
                self.save_workspaces()
                self.update_workspace_display()
            else:
                messagebox.showerror("错误", f"工作区 '{ws_name}' 已存在!")
    
    def delete_workspace(self):
        """删除选中的工作区"""
        selection = self.workspace_listbox.curselection()
        if selection:
            ws_name = self.workspace_listbox.get(selection[0])
            if messagebox.askyesno("确认", f"确定要删除工作区 '{ws_name}' 吗?"):
                del self.workspaces[ws_name]
                self.save_workspaces()
                self.update_workspace_display()
    
    def add_to_workspace(self):
        """将选中项添加到工作区"""
        selection = self.results_tree.selection()
        if not selection:
            messagebox.showinfo("提示", "请先选择要添加的项目")
            return
        
        item = self.results_tree.item(selection[0])
        item_type = item['values'][1]
        item_name = item['values'][0]
        item_path = item['values'][2]
        
        # 选择工作区
        ws_name = tk.simpledialog.askstring("添加到工作区", "请输入工作区名称:")
        if ws_name and ws_name.strip():
            ws_name = ws_name.strip()
            if ws_name not in self.workspaces:
                self.workspaces[ws_name] = []
            
            # 添加到工作区
            self.workspaces[ws_name].append({
                'type': item_type,
                'name': item_name,
                'path': item_path
            })
            
            self.save_workspaces()
            self.update_workspace_display()
            messagebox.showinfo("成功", f"已将 '{item_name}' 添加到工作区 '{ws_name}'")
    
    def on_workspace_select(self, event):
        """处理工作区选择"""
        selection = self.workspace_listbox.curselection()
        if selection:
            ws_name = self.workspace_listbox.get(selection[0])
            items = self.workspaces.get(ws_name, [])
            
            # 清空现有结果
            for item in self.results_tree.get_children():
                self.results_tree.delete(item)
            
            # 添加工作区项目
            for item in items:
                self.results_tree.insert("", tk.END, values=(
                    item['name'], item['type'], item['path'], "工作区项目"
                ))
            
            self.status_var.set(f"已加载工作区 '{ws_name}'，包含 {len(items)} 个项目")
    
    # 自定义命令功能
    def load_custom_commands(self):
        """加载自定义命令"""
        try:
            if os.path.exists(self.commands_file):
                with open(self.commands_file, 'r', encoding='utf-8') as f:
                    self.custom_commands = json.load(f)
        except Exception as e:
            print(f"加载自定义命令失败: {e}")
            self.custom_commands = {}
    
    def save_custom_commands(self):
        """保存自定义命令"""
        try:
            with open(self.commands_file, 'w', encoding='utf-8') as f:
                json.dump(self.custom_commands, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"保存自定义命令失败: {e}")
    
    # 历史记录功能
    def load_history(self):
        """加载搜索历史记录"""
        try:
            if os.path.exists(self.history_file):
                with open(self.history_file, 'r', encoding='utf-8') as f:
                    self.history = json.load(f)
        except Exception as e:
            print(f"加载历史记录失败: {e}")
            self.history = []
    
    def save_history(self):
        """保存搜索历史记录"""
        try:
            with open(self.history_file, 'w', encoding='utf-8') as f:
                json.dump(self.history, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"保存历史记录失败: {e}")
    
    def update_history_display(self):
        """更新历史记录显示"""
        self.history_listbox.delete(0, tk.END)
        for item in reversed(self.history):
            self.history_listbox.insert(tk.END, item)
    
    # 搜索功能
    def on_search(self, event=None):
        """处理搜索请求"""
        query = self.search_var.get().strip()
        if not query:
            return
        
        # 添加到历史记录
        if query in self.history:
            self.history.remove(query)
        self.history.append(query)
        if len(self.history) > self.max_history:
            self.history = self.history[-self.max_history:]
        self.save_history()
        self.update_history_display()
        
        # 执行搜索
        self.status_var.set(f"正在搜索 '{query}'...")
        self.root.update()
        self.search_results = []
        search_type = self.search_type.get()
        
        # 模糊搜索
        pattern = '.*?'.join(map(re.escape, query))
        regex = re.compile(pattern, re.IGNORECASE)
        
        # 根据搜索类型执行不同搜索
        if search_type in ["all", "file"]:
            # 搜索文件
            for filename, paths in self.file_index.items():
                if regex.search(filename):
                    for path in paths:
                        try:
                            stat = os.stat(path)
                            size = self.format_size(stat.st_size)
                            modified = datetime.fromtimestamp(stat.st_mtime).strftime('%Y-%m-%d %H:%M')
                            self.search_results.append((filename, "文件", path, f"{size} | {modified}"))
                        except (PermissionError, OSError):
                            continue
        
        if search_type in ["all", "app"]:
            # 搜索应用程序
            for app_name, app_path in self.apps_index.items():
                if regex.search(app_name):
                    info = "应用程序"
                    if platform.system() == "Windows" and app_path.endswith(".lnk"):
                        info = "快捷方式"
                    self.search_results.append((app_name, "应用", app_path, info))
        
        if search_type in ["all", "workspace"]:
            # 搜索工作区
            for ws_name, items in self.workspaces.items():
                if regex.search(ws_name):
                    self.search_results.append((ws_name, "工作区", ws_name, f"{len(items)} 个项目"))
        
        if search_type in ["all", "command"]:
            # 搜索自定义命令
            for cmd_name, cmd_data in self.custom_commands.items():
                if regex.search(cmd_name):
                    cmd_type = cmd_data.get("type", "未知")
                    cmd_desc = cmd_data.get("description", "")
                    self.search_results.append((cmd_name, "命令", cmd_data["command"], f"{cmd_type} | {cmd_desc}"))
        
        # 按匹配度排序
        self.search_results.sort(key=lambda x: self.match_score(x[0], query), reverse=True)
        
        # 显示结果
        self.display_results()
        self.status_var.set(f"搜索完成，找到 {len(self.search_results)} 个结果")
    
    def match_score(self, text, query):
        """计算文本与查询的匹配度"""
        text_lower = text.lower()
        query_lower = query.lower()
        
        # 完全匹配得高分
        if text_lower == query_lower:
            return 100
        
        # 前缀匹配次之
        if text_lower.startswith(query_lower):
            return 80
        
        # 包含匹配再次之
        if query_lower in text_lower:
            return 60
        
        # 模糊匹配得分更低
        pattern = '.*?'.join(map(re.escape, query_lower))
        if re.search(pattern, text_lower):
            return 40
        
        return 0
    
    def format_size(self, size_bytes):
        """格式化文件大小显示"""
        units = ['B', 'KB', 'MB', 'GB', 'TB']
        unit_index = 0
        while size_bytes >= 1024 and unit_index < len(units) - 1:
            size_bytes /= 1024
            unit_index += 1
        return f"{size_bytes:.2f} {units[unit_index]}"
    
    def display_results(self):
        """显示搜索结果"""
        # 清空现有结果
        for item in self.results_tree.get_children():
            self.results_tree.delete(item)
        
        # 添加新结果
        for result in self.search_results:
            self.results_tree.insert("", tk.END, values=result)
    
    # 交互功能
    def on_history_select(self, event):
        """处理历史记录选择"""
        selection = self.history_listbox.curselection()
        if selection:
            query = self.history_listbox.get(selection[0])
            self.search_var.set(query)
            self.on_search()
    
    def on_double_click(self, event):
        """处理双击结果项"""
        selection = self.results_tree.selection()
        if selection:
            item = self.results_tree.item(selection[0])
            item_type = item['values'][1]
            item_path = item['values'][2]
            
            if item_type == "文件":
                self.open_file(item_path)
            elif item_type == "应用":
                self.launch_application(item_path)
            elif item_type == "工作区":
                self.on_workspace_select(None)
            elif item_type == "命令":
                self.execute_command(item_path)
    
    def on_tree_key(self, event):
        """处理结果树中的上下方向键"""
        selection = self.results_tree.selection()
        if not selection:
            if event.keysym == "Down":
                try:
                    first_item = self.results_tree.get_children()[0]
                    self.results_tree.selection_set(first_item)
                    self.results_tree.see(first_item)
                except IndexError:
                    pass
            return "break"
        
        current_item = selection[0]
        children = self.results_tree.get_children()
        current_index = children.index(current_item)
        
        if event.keysym == "Up" and current_index > 0:
            new_index = current_index - 1
        elif event.keysym == "Down" and current_index < len(children) - 1:
            new_index = current_index + 1
        else:
            return "break"
        
        new_item = children[new_index]
        self.results_tree.selection_set(new_item)
        self.results_tree.see(new_item)
        return "break"
    
    def focus_results(self, event):
        """将焦点从搜索框转移到结果列表"""
        if self.search_results:
            self.results_tree.focus_set()
            first_item = self.results_tree.get_children()[0]
            self.results_tree.selection_set(first_item)
            self.results_tree.see(first_item)
        return "break"
    
    # 执行功能
    def open_file(self, file_path):
        """打开文件"""
        try:
            if os.path.exists(file_path):
                if platform.system() == "Windows":
                    os.startfile(file_path)
                else:
                    subprocess.run(['open' if platform.system() == "Darwin" else 'xdg-open', file_path])
                self.status_var.set(f"已打开: {file_path}")
            else:
                messagebox.showerror("错误", f"文件不存在: {file_path}")
                self.status_var.set("文件不存在")
        except Exception as e:
            messagebox.showerror("错误", f"无法打开文件: {e}")
            self.status_var.set("打开文件失败")
    
    def launch_application(self, app_path):
        """启动应用程序"""
        try:
            if platform.system() == "Windows":
                # 处理快捷方式
                if app_path.endswith(".lnk"):
                    import win32com.client
                    shell = win32com.client.Dispatch("WScript.Shell")
                    shortcut = shell.CreateShortCut(app_path)
                    app_path = shortcut.TargetPath
                
                os.startfile(app_path)
            else:
                subprocess.Popen([app_path], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            
            self.status_var.set(f"已启动应用: {os.path.basename(app_path)}")
        except Exception as e:
            messagebox.showerror("错误", f"无法启动应用: {e}")
            self.status_var.set("启动应用失败")
    
    def execute_command(self, command):
        """执行命令"""
        try:
            result = subprocess.run(command, shell=True, capture_output=True, text=True)
            if result.returncode == 0:
                self.status_var.set(f"命令执行成功: {command}")
                if result.stdout:
                    print(f"命令输出:\n{result.stdout}")
            else:
                self.status_var.set(f"命令执行失败: {command}")
                if result.stderr:
                    print(f"错误信息:\n{result.stderr}")
        except Exception as e:
            messagebox.showerror("错误", f"执行命令失败: {e}")
            self.status_var.set("执行命令失败")

if __name__ == "__main__":
    root = tk.Tk()
    app = QuickFile(root)
    root.mainloop()    