import os
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import json
import threading
import time
from datetime import datetime
import re

class FileLauncher:
    def __init__(self, root):
        self.root = root
        self.root.title("文件快速启动")
        self.root.geometry("800x600")
        self.root.resizable(True, True)
        
        # 设置中文字体支持
        self.style = ttk.Style()
        self.style.configure("TLabel", font=("SimHei", 10))
        self.style.configure("TButton", font=("SimHei", 10))
        self.style.configure("TEntry", font=("SimHei", 10))
        self.style.configure("Treeview", font=("SimHei", 10))
        
        # 数据存储
        self.file_index = {}  # 文件索引 {文件名: [文件路径]}
        self.search_results = []  # 当前搜索结果
        self.history = []  # 搜索历史
        self.max_history = 20  # 最大历史记录数
        self.history_file = "launcher_history.json"  # 历史记录文件
        self.index_file = "file_index.json"  # 索引文件
        self.excluded_dirs = {  # 排除的目录
            "System Volume Information", "$Recycle.Bin", "Windows", 
            "Program Files", "Program Files (x86)", "AppData"
        }
        self.excluded_extensions = {  # 排除的文件扩展名
            ".sys", ".dll", ".exe", ".com", ".tmp", ".log", ".bin", 
            ".msi", ".cab", ".dat", ".ini", ".db", ".sqlite"
        }
        
        # 加载历史记录和索引
        self.load_history()
        self.load_index()
        
        # 创建界面
        self.create_widgets()
        
        # 启动索引线程（后台运行）
        if not self.file_index:
            self.start_indexing()
    
    def create_widgets(self):
        # 顶部搜索框区域
        top_frame = ttk.Frame(self.root, padding=10)
        top_frame.pack(fill=tk.X)
        
        ttk.Label(top_frame, text="搜索文件:").pack(side=tk.LEFT, padx=5)
        
        self.search_var = tk.StringVar()
        self.search_entry = ttk.Entry(top_frame, textvariable=self.search_var, width=50)
        self.search_entry.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        self.search_entry.bind("<Return>", self.on_search)
        self.search_entry.bind("<Down>", self.focus_results)
        
        self.search_btn = ttk.Button(top_frame, text="搜索", command=self.on_search)
        self.search_btn.pack(side=tk.LEFT, padx=5)
        
        self.clear_btn = ttk.Button(top_frame, text="清除历史", command=self.clear_history)
        self.clear_btn.pack(side=tk.LEFT, padx=5)
        
        # 索引状态区域
        status_frame = ttk.Frame(self.root, padding=5)
        status_frame.pack(fill=tk.X)
        
        self.status_var = tk.StringVar()
        self.status_var.set("准备就绪")
        self.status_label = ttk.Label(status_frame, textvariable=self.status_var, foreground="blue")
        self.status_label.pack(side=tk.LEFT)
        
        self.progress = ttk.Progressbar(status_frame, mode="indeterminate", length=200)
        self.progress.pack(side=tk.LEFT, padx=10)
        
        # 结果显示区域
        results_frame = ttk.PanedWindow(self.root, orient=tk.HORIZONTAL)
        results_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # 左侧历史记录
        history_frame = ttk.LabelFrame(results_frame, text="搜索历史")
        results_frame.add(history_frame, weight=1)
        
        self.history_listbox = tk.Listbox(history_frame, font=("SimHei", 10), selectbackground="#a6a6a6")
        self.history_listbox.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.history_listbox.bind("<Double-1>", self.on_history_select)
        self.update_history_display()
        
        # 右侧搜索结果
        results_tree_frame = ttk.LabelFrame(results_frame, text="搜索结果")
        results_frame.add(results_tree_frame, weight=3)
        
        columns = ("name", "path", "size", "modified")
        self.results_tree = ttk.Treeview(results_tree_frame, columns=columns, show="headings")
        self.results_tree.heading("name", text="文件名")
        self.results_tree.heading("path", text="路径")
        self.results_tree.heading("size", text="大小")
        self.results_tree.heading("modified", text="修改时间")
        
        self.results_tree.column("name", width=150)
        self.results_tree.column("path", width=300)
        self.results_tree.column("size", width=80, anchor=tk.E)
        self.results_tree.column("modified", width=120)
        
        self.results_tree.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.results_tree.bind("<Double-1>", self.on_double_click)
        self.results_tree.bind("<Return>", self.on_double_click)
        self.results_tree.bind("<Up>", self.on_tree_key)
        self.results_tree.bind("<Down>", self.on_tree_key)
    
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
    
    def load_index(self):
        """加载文件索引"""
        try:
            if os.path.exists(self.index_file):
                with open(self.index_file, 'r', encoding='utf-8') as f:
                    self.file_index = json.load(f)
                self.status_var.set(f"已加载索引，包含 {len(self.file_index)} 个文件")
        except Exception as e:
            print(f"加载索引失败: {e}")
            self.file_index = {}
    
    def save_index(self):
        """保存文件索引"""
        try:
            with open(self.index_file, 'w', encoding='utf-8') as f:
                json.dump(self.file_index, f, ensure_ascii=False, indent=2)
            self.status_var.set(f"索引已保存，包含 {len(self.file_index)} 个文件")
        except Exception as e:
            print(f"保存索引失败: {e}")
    
    def start_indexing(self):
        """启动索引线程"""
        self.status_var.set("正在建立文件索引...")
        self.progress.start()
        self.index_thread = threading.Thread(target=self.build_index)
        self.index_thread.daemon = True
        self.index_thread.start()
    
    def build_index(self):
        """构建文件索引"""
        start_time = time.time()
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
        
        end_time = time.time()
        self.progress.stop()
        self.save_index()
        self.status_var.set(f"索引完成，共 {count} 个文件，耗时 {end_time - start_time:.2f} 秒")
    
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
        
        # 模糊搜索
        pattern = '.*?'.join(map(re.escape, query))
        regex = re.compile(pattern, re.IGNORECASE)
        
        for filename, paths in self.file_index.items():
            if regex.search(filename):
                for path in paths:
                    try:
                        # 获取文件信息
                        stat = os.stat(path)
                        size = self.format_size(stat.st_size)
                        modified = datetime.fromtimestamp(stat.st_mtime).strftime('%Y-%m-%d %H:%M')
                        self.search_results.append((filename, path, size, modified))
                    except (PermissionError, OSError):
                        continue
        
        # 按文件名匹配度排序
        self.search_results.sort(key=lambda x: self.match_score(x[0], query), reverse=True)
        
        # 显示结果
        self.display_results()
        self.status_var.set(f"搜索完成，找到 {len(self.search_results)} 个结果")
    
    def match_score(self, filename, query):
        """计算文件名与查询的匹配度"""
        filename_lower = filename.lower()
        query_lower = query.lower()
        
        # 完全匹配得高分
        if filename_lower == query_lower:
            return 100
        
        # 前缀匹配次之
        if filename_lower.startswith(query_lower):
            return 80
        
        # 包含匹配再次之
        if query_lower in filename_lower:
            return 60
        
        # 模糊匹配得分更低
        pattern = '.*?'.join(map(re.escape, query_lower))
        if re.search(pattern, filename_lower):
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
            file_path = item['values'][1]  # 路径在第2列
            self.open_file(file_path)
    
    def open_file(self, file_path):
        """打开文件"""
        try:
            if os.path.exists(file_path):
                if os.name == 'nt':  # Windows系统
                    os.startfile(file_path)
                else:  # Linux/Unix/Mac系统
                    import subprocess
                    subprocess.run(['open' if os.name == 'posix' else 'xdg-open', file_path])
                self.status_var.set(f"已打开: {file_path}")
            else:
                messagebox.showerror("错误", f"文件不存在: {file_path}")
                self.status_var.set("文件不存在")
        except Exception as e:
            messagebox.showerror("错误", f"无法打开文件: {e}")
            self.status_var.set("打开文件失败")
    
    def clear_history(self):
        """清除搜索历史"""
        self.history = []
        self.save_history()
        self.update_history_display()
        self.status_var.set("已清除搜索历史")

if __name__ == "__main__":
    root = tk.Tk()
    app = FileLauncher(root)
    root.mainloop()    