import tkinter as tk
from tkinter import ttk, messagebox
import time
import csv
import os
from datetime import datetime


class StudyTimer:
    def __init__(self, root):
        self.root = root
        self.root.title("学习计时器")
        self.root.geometry("500x400")
        self.root.resizable(False, False)
        # 添加窗口状态变量
        self.minimized = False
        self.always_on_top = False
        self.remark_font_size = 12  # 默认备注字体大小
        # 预设的备注选项 (必须在 create_widgets 之前定义)
        self.remark_options = [
            "高数", "线代", "概率论",
            "英语", "政治",
            "结构", "计组", "计网", "系统"
        ]
        # 初始化计时器变量
        self.running = False
        self.start_time = 0
        self.elapsed_time = 0
        self.history_file = "timer_history.csv"
        # 创建历史文件（如果不存在）
        self.create_history_file()
        # +++ 修正：启动时加载当天已有的总学习时间 +++
        self.elapsed_time = self.load_today_total_time_value()
        # +++ 结束修正 +++
        # 创建UI (此时 remark_options 已经存在)
        self.create_widgets()
        # 定期更新计时器
        self.update_timer()

    def create_history_file(self):
        """创建历史记录文件（如果不存在）"""
        if not os.path.exists(self.history_file):
            with open(self.history_file, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(["日期", "开始时间", "结束时间", "持续时间(秒)", "备注"])

    def load_today_total_time_value(self):
        """加载并返回今天已有的总学习时间（秒），不修改实例变量"""
        if not os.path.exists(self.history_file):
            return 0.0
        today = datetime.now().strftime("%Y-%m-%d")
        total_seconds = 0.0
        try:
            with open(self.history_file, 'r', encoding='utf-8') as f:
                reader = csv.reader(f)
                header = next(reader, None)
                if header is None:
                    return 0.0
                for row in reader:
                    if len(row) >= 5:
                        date_str = row[0]
                        duration_str = row[3]
                        if date_str == today:
                            total_seconds += float(duration_str)
        except Exception as e:
            print(f"读取今日学习时间失败: {e}")
        return total_seconds

    def create_widgets(self):
        """创建UI组件"""
        # 计时显示区域
        timer_frame = tk.Frame(self.root, pady=10)
        timer_frame.pack(fill="x")

        self.time_var = tk.StringVar(value="00:00:00")
        time_label = tk.Label(
            timer_frame,
            textvariable=self.time_var,
            font=("Helvetica", 36, "bold"),
            fg="#2c3e50"
        )
        time_label.pack()

        # 备注选择区域 (替换原来的Entry)
        remark_frame = tk.Frame(self.root, padx=20, pady=5)
        remark_frame.pack(fill="x", expand=True)
        tk.Label(remark_frame, text="选择/输入:", font=("Helvetica", 10)).pack(side="left")
        # 使用 Combobox 替代 Entry
        self.remark_combo = ttk.Combobox(
            remark_frame,
            values=self.remark_options,
            font=("Helvetica", self.remark_font_size),
            width=27,
            state="normal"  # 允许编辑
        )
        self.remark_combo.pack(side="left", padx=10, fill="x", expand=True)
        self.remark_combo.insert(0, "例如：高数、英语等")

        # 按钮区域
        button_frame = tk.Frame(self.root, padx=20, pady=10)
        button_frame.pack(fill="x")

        self.start_button = tk.Button(
            button_frame,
            text="开始",
            font=("Helvetica", 10, "bold"),
            bg="#27ae60",
            fg="white",
            width=8,
            height=1,
            command=self.toggle_timer
        )
        self.start_button.pack(side="left", padx=5)

        # 添加字体大小控制
        font_frame = tk.Frame(button_frame)
        font_frame.pack(side="left", padx=5)
        tk.Label(font_frame, text="字体:", font=("Helvetica", 10)).pack(side="left")
        self.font_size_var = tk.IntVar(value=self.remark_font_size)
        font_scale = tk.Scale(
            font_frame,
            from_=8,
            to=24,
            orient="horizontal",
            variable=self.font_size_var,
            command=lambda _: self.update_remark_font_size(),
            length=100
        )
        font_scale.pack(side="left")

        # 添加置顶按钮
        self.top_button = tk.Button(
            button_frame,
            text="置顶",
            font=("Helvetica", 10),
            bg="#9b59b6",
            fg="white",
            width=8,
            height=1,
            command=self.toggle_always_on_top
        )
        self.top_button.pack(side="right", padx=5)

        # 添加最小化按钮
        self.minimize_button = tk.Button(
            button_frame,
            text="最小化",
            font=("Helvetica", 10),
            bg="#95a5a6",
            fg="white",
            width=8,
            height=1,
            command=self.toggle_minimize
        )
        self.minimize_button.pack(side="right", padx=5)

        # 历史记录按钮
        self.history_button = tk.Button(
            button_frame,
            text="历史记录",
            font=("Helvetica", 10),
            bg="#3498db",
            fg="white",
            width=8,
            height=1,
            command=self.show_daily_summary
        )
        self.history_button.pack(side="right", padx=5)

        # 状态标签
        self.status_var = tk.StringVar(value="就绪")
        self.status_label = tk.Label(
            self.root,
            textvariable=self.status_var,
            font=("Helvetica", 10),
            fg="#7f8c8d",
            anchor="w",
            padx=20
        )
        self.status_label.pack(fill="x", pady=(0, 10))

    def update_remark_font_size(self):
        """更新备注输入框的字体大小"""
        new_size = self.font_size_var.get()
        self.remark_font_size = new_size
        self.remark_combo.config(font=("Helvetica", new_size))
        # 如果是最小化状态，检查字体大小是否过大
        if self.minimized:
            required_height = 150 + max(0, (new_size - 12) * 3)
            self.root.geometry(f"500x{int(required_height)}")

    def toggle_minimize(self):
        """切换窗口最小化状态"""
        if self.minimized:
            # 恢复正常窗口
            self.root.geometry("500x400")
            self.minimize_button.config(text="最小化")
            # 重新添加隐藏的组件
            self.history_button.pack(side="right", padx=5)
            self.status_label.pack(fill="x", pady=(0, 10))
            self.minimized = False
        else:
            # 计算最小化窗口高度 (基于当前字体大小)
            min_height = 150 + max(0, (self.remark_font_size - 12) * 3)
            # 最小化窗口（只显示时间、备注和按钮）
            self.root.geometry(f"500x{int(min_height)}")
            self.minimize_button.config(text="恢复")
            # 隐藏不需要的组件
            self.history_button.pack_forget()
            self.status_label.pack_forget()
            self.minimized = True

    def toggle_always_on_top(self):
        """切换窗口置顶状态"""
        self.always_on_top = not self.always_on_top
        self.root.attributes("-topmost", self.always_on_top)
        self.top_button.config(text="取消置顶" if self.always_on_top else "置顶")

    def toggle_timer(self):
        """切换开始/暂停状态"""
        if not self.running:
            # 检查备注是否为空
            remark = self.remark_combo.get().strip()
            if not remark or remark == "例如：高数、英语等":
                messagebox.showwarning("输入提示", "请选择或输入学习内容（如：高数）")
                return
            # 开始计时
            self.running = True
            self.start_time = time.time()
            self.start_button.config(text="暂停", bg="#e74c3c")
            self.status_var.set(f"计时中: {remark}")
            self.remark_combo.config(state="disabled")
        else:
            # 暂停计时
            self.running = False
            self.start_button.config(text="开始", bg="#27ae60")
            self.status_var.set("计时已暂停")
            self.remark_combo.config(state="normal")
            # 保存本次计时记录
            self.save_record()

    def save_record(self):
        """保存计时记录到历史文件"""
        remark = self.remark_combo.get().strip()
        end_time = time.time()
        duration = end_time - self.start_time
        start_str = time.strftime("%H:%M:%S", time.localtime(self.start_time))
        end_str = time.strftime("%H:%M:%S", time.localtime(end_time))
        date_str = time.strftime("%Y-%m-%d", time.localtime(self.start_time))
        with open(self.history_file, 'a', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow([
                date_str,
                start_str,
                end_str,
                f"{duration:.1f}",
                remark
            ])
        # 更新状态
        self.status_var.set(f"已保存: {remark} ({duration:.1f}秒)")

    def update_timer(self):
        """定期更新计时器显示"""
        if self.running:
            current_time = time.time()
            current_elapsed = (current_time - self.start_time)
            self.elapsed_time = self.load_today_total_time_value() + current_elapsed
            hours, rem = divmod(self.elapsed_time, 3600)
            minutes, seconds = divmod(rem, 60)
            time_str = "{:02d}:{:02d}:{:02d}".format(
                int(hours), int(minutes), int(seconds)
            )
            self.time_var.set(time_str)
        # 每100ms更新一次
        self.root.after(100, self.update_timer)

    def show_daily_summary(self):
        """显示每日学习汇总窗口（主界面）"""
        summary_window = tk.Toplevel(self.root)
        summary_window.title("每日学习汇总")
        summary_window.geometry("600x400")
        summary_window.transient(self.root)
        summary_window.grab_set()

        # 创建汇总树
        tree = ttk.Treeview(
            summary_window,
            columns=("date", "total_duration", "sessions"),
            show="headings"
        )
        tree.heading("date", text="日期")
        tree.heading("total_duration", text="总学习时间")
        tree.heading("sessions", text="学习次数")
        tree.column("date", width=150, anchor="center")
        tree.column("total_duration", width=180, anchor="center")
        tree.column("sessions", width=100, anchor="center")

        # 添加滚动条
        scrollbar = ttk.Scrollbar(summary_window, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
        tree.pack(fill="both", expand=True, padx=10, pady=10)

        # 计算每日汇总
        daily_summary = {}
        all_dates = set()  # 用于存储所有出现过的日期
        try:
            with open(self.history_file, 'r', encoding='utf-8') as f:
                reader = csv.reader(f)
                next(reader)  # 跳过标题行
                for row in reader:
                    if len(row) >= 5:
                        date = row[0]
                        duration = float(row[3])
                        all_dates.add(date)
                        if date in daily_summary:
                            daily_summary[date]["total"] += duration
                            daily_summary[date]["count"] += 1
                        else:
                            daily_summary[date] = {"total": duration, "count": 1}
        except Exception as e:
            messagebox.showerror("错误", f"计算汇总失败: {str(e)}")
            return

        # 按日期降序排序
        sorted_dates = sorted(daily_summary.keys(), reverse=True)

        # 添加到树中
        for date in sorted_dates:
            total_seconds = daily_summary[date]["total"]
            hours, rem = divmod(total_seconds, 3600)
            minutes, seconds = divmod(rem, 60)
            time_str = f"{int(hours)}小时{int(minutes)}分{int(seconds)}秒"
            tree.insert("", "end", values=(
                date,
                time_str,
                daily_summary[date]["count"]
            ), tags=(date,))

        # 添加双击事件
        def on_double_click(event):
            item = tree.selection()[0]
            selected_date = tree.item(item, "values")[0]
            self.show_daily_detail(selected_date, summary_window)

        tree.bind("<Double-1>", on_double_click)

        # +++ 新增：添加“总学习时长”按钮 +++
        total_summary_frame = tk.Frame(summary_window)
        total_summary_frame.pack(fill="x", padx=10, pady=5)
        tk.Button(
            total_summary_frame,
            text="总学习时长",
            bg="#e67e22",
            fg="white",
            font=("Helvetica", 10, "bold"),
            command=lambda: self.show_total_summary(summary_window)
        ).pack(side="right", padx=5)
        # +++ 结束新增 +++

        # 添加关闭按钮
        tk.Button(
            summary_window,
            text="关闭",
            command=summary_window.destroy,
            bg="#e74c3c",
            fg="white"
        ).pack(pady=10)

    def format_duration(self, seconds):
        """
        将秒数格式化为 xx min 或 xx h xx min 的形式
        :param seconds: 秒数
        :return: 格式化后的字符串
        """
        if seconds < 60:
            return f"{int(seconds)}s"  # 少于1分钟显示秒
        elif seconds < 3600:
            minutes = seconds // 60
            return f"{int(minutes)}min"
        else:
            hours = seconds // 3600
            minutes = (seconds % 3600) // 60
            if minutes > 0:
                return f"{int(hours)}h{int(minutes)}min"
            else:
                return f"{int(hours)}h"

    def show_daily_detail(self, target_date, parent_window):
        """显示指定日期的详细学习记录（按备注分类）"""
        detail_window = tk.Toplevel(parent_window)
        detail_window.title(f"{target_date} 学习详情")
        detail_window.geometry("600x350")
        detail_window.transient(parent_window)

        # 创建详细记录树
        tree = ttk.Treeview(
            detail_window,
            columns=("remark", "duration", "start", "end"),
            show="headings"
        )
        tree.heading("remark", text="学习内容")
        tree.heading("duration", text="学习时长")  # 修改列名
        tree.heading("start", text="开始时间")
        tree.heading("end", text="结束时间")
        tree.column("remark", width=150, anchor="center")
        tree.column("duration", width=100, anchor="center")
        tree.column("start", width=100, anchor="center")
        tree.column("end", width=100, anchor="center")

        # 添加滚动条
        scrollbar = ttk.Scrollbar(detail_window, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
        tree.pack(fill="both", expand=True, padx=10, pady=10)

        # 加载目标日期的详细数据
        try:
            with open(self.history_file, 'r', encoding='utf-8') as f:
                reader = csv.reader(f)
                next(reader)  # 跳过标题行
                for row in reader:
                    if len(row) >= 5 and row[0] == target_date:
                        duration_sec = float(row[3])
                        # 使用新的格式化函数
                        formatted_duration = self.format_duration(duration_sec)
                        tree.insert("", "end", values=(row[4], formatted_duration, row[1], row[2]))
        except Exception as e:
            messagebox.showerror("错误", f"加载详细记录失败: {str(e)}")
            return

        # 添加按备注汇总的按钮
        def show_remark_summary():
            remark_summary = {}
            for child in tree.get_children():
                values = tree.item(child, "values")
                remark = values[0]
                # 注意：values[1] 是格式化后的字符串，无法直接计算，需要重新从原始数据获取
                # 所以这里我们不使用 tree 的数据，而是重新读取文件
            try:
                with open(self.history_file, 'r', encoding='utf-8') as f:
                    reader = csv.reader(f)
                    next(reader)
                    for row in reader:
                        if len(row) >= 5 and row[0] == target_date:
                            remark = row[4]
                            duration = float(row[3])
                            remark_summary[remark] = remark_summary.get(remark, 0) + duration
            except Exception as e:
                messagebox.showerror("错误", f"汇总计算失败: {str(e)}")
                return

            summary_window = tk.Toplevel(detail_window)
            summary_window.title(f"{target_date} 内容汇总")
            summary_window.geometry("400x300")
            sum_tree = ttk.Treeview(
                summary_window,
                columns=("remark", "total_duration"),
                show="headings"
            )
            sum_tree.heading("remark", text="学习内容")
            sum_tree.heading("total_duration", text="总时长")
            sum_tree.column("remark", width=150, anchor="center")
            sum_tree.column("total_duration", width=150, anchor="center")
            scrollbar_sum = ttk.Scrollbar(summary_window, orient="vertical", command=sum_tree.yview)
            sum_tree.configure(yscrollcommand=scrollbar_sum.set)
            scrollbar_sum.pack(side="right", fill="y")
            sum_tree.pack(fill="both", expand=True, padx=10, pady=10)

            for remark, total_seconds in remark_summary.items():
                formatted_total = self.format_duration(total_seconds)
                sum_tree.insert("", "end", values=(remark, formatted_total))

        tk.Button(
            detail_window,
            text="按内容汇总",
            command=show_remark_summary,
            bg="#3498db",
            fg="white"
        ).pack(pady=5)

        # 添加关闭按钮
        tk.Button(
            detail_window,
            text="关闭",
            command=detail_window.destroy,
            bg="#e74c3c",
            fg="white"
        ).pack(pady=5)

    # +++ 新增方法：显示总学习时长和按备注汇总 +++
    def show_total_summary(self, parent_window):
        """显示所有历史记录的总学习时长和按备注的分类汇总"""
        total_window = tk.Toplevel(parent_window)
        total_window.title("总学习时长")
        total_window.geometry("600x400")
        total_window.transient(parent_window)

        # 创建Notebook（标签页）
        notebook = ttk.Notebook(total_window)
        notebook.pack(fill="both", expand=True, padx=10, pady=10)

        # --- 标签页1: 总时长 ---
        total_tab = tk.Frame(notebook)
        notebook.add(total_tab, text="总学习时间")

        # 读取所有记录并计算总时长
        total_seconds = 0.0
        try:
            with open(self.history_file, 'r', encoding='utf-8') as f:
                reader = csv.reader(f)
                next(reader)  # 跳过标题行
                for row in reader:
                    if len(row) >= 5:
                        total_seconds += float(row[3])
        except Exception as e:
            messagebox.showerror("错误", f"计算总时长失败: {str(e)}")
            total_seconds = 0.0

        # 使用统一的格式化函数
        time_str = self.format_duration(total_seconds)

        # 在标签页中显示
        tk.Label(
            total_tab,
            text="所有历史学习总时长:",
            font=("Helvetica", 14, "bold"),
            fg="#2c3e50"
        ).pack(pady=20)
        tk.Label(
            total_tab,
            text=time_str,
            font=("Helvetica", 20, "bold"),
            fg="#e74c3c"
        ).pack()

        # --- 标签页2: 按备注汇总 ---
        remark_tab = tk.Frame(notebook)
        notebook.add(remark_tab, text="按内容汇总")

        # 计算按备注的汇总
        remark_summary = {}
        try:
            with open(self.history_file, 'r', encoding='utf-8') as f:
                reader = csv.reader(f)
                next(reader)  # 跳过标题行
                for row in reader:
                    if len(row) >= 5:
                        remark = row[4]
                        duration = float(row[3])
                        remark_summary[remark] = remark_summary.get(remark, 0) + duration
        except Exception as e:
            messagebox.showerror("错误", f"计算按内容汇总失败: {str(e)}")
            return

        # 按总时长降序排序
        sorted_remarks = sorted(remark_summary.items(), key=lambda x: x[1], reverse=True)

        # 创建树形视图
        tree = ttk.Treeview(
            remark_tab,
            columns=("remark", "total_duration"),
            show="headings"
        )
        tree.heading("remark", text="学习内容")
        tree.heading("total_duration", text="总学习时间")
        tree.column("remark", width=200, anchor="center")
        tree.column("total_duration", width=200, anchor="center")

        # 添加滚动条
        scrollbar = ttk.Scrollbar(remark_tab, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
        tree.pack(fill="both", expand=True, padx=10, pady=10)

        # 添加数据
        for remark, total_sec in sorted_remarks:
            time_str = self.format_duration(total_sec)
            tree.insert("", "end", values=(remark, time_str))

    # +++ 结束新增 +++


if __name__ == "__main__":
    root = tk.Tk()
    app = StudyTimer(root)
    root.mainloop()