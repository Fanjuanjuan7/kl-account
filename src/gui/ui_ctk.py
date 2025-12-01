"""
CustomTkinter GUI for KL-zhanghao
使用CustomTkinter实现的现代化GUI界面
"""
import customtkinter as ctk
from pathlib import Path
import csv
import json
import threading
from typing import List, Dict, Any
from tkinter import filedialog, messagebox
import sys

from ..utils.logger import get_logger
from ..utils.config_store import load_config, save_config, reset_config
from ..services.account import register_accounts_batch


class KLZhanghaoApp(ctk.CTk):
    def __init__(self, runtime_dir: Path):
        super().__init__()
        
        self.runtime_dir = runtime_dir
        self.log = get_logger(__name__)
        self.cfg = load_config(runtime_dir)
        
        # 窗口配置
        self.title("KL-zhanghao 账号批量注册工具")
        self.geometry("1200x800")
        
        # 设置主题
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")
        
        # 创建UI
        self.create_widgets()
        self.load_config_to_ui()
        
    def create_widgets(self):
        """创建所有UI组件"""
        # 主容器
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)
        
        # 创建框架
        main_frame = ctk.CTkFrame(self)
        main_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        main_frame.grid_columnconfigure(0, weight=1)
        main_frame.grid_rowconfigure(4, weight=1)
        
        # 1. CSV文件选择区域
        csv_frame = ctk.CTkFrame(main_frame)
        csv_frame.grid(row=0, column=0, padx=10, pady=10, sticky="ew")
        csv_frame.grid_columnconfigure(1, weight=1)
        
        ctk.CTkLabel(csv_frame, text="CSV文件:").grid(row=0, column=0, padx=5, pady=5)
        self.csv_entry = ctk.CTkEntry(csv_frame, placeholder_text="选择CSV文件...")
        self.csv_entry.grid(row=0, column=1, padx=5, pady=5, sticky="ew")
        
        ctk.CTkButton(csv_frame, text="浏览", command=self.browse_csv, width=100).grid(row=0, column=2, padx=5, pady=5)
        ctk.CTkButton(csv_frame, text="加载CSV", command=self.load_csv, width=100).grid(row=0, column=3, padx=5, pady=5)
        
        # 状态标签
        self.status_label = ctk.CTkLabel(csv_frame, text="就绪", text_color="green")
        self.status_label.grid(row=1, column=0, columnspan=4, padx=5, pady=5)
        
        # 2. CSV预览表格
        table_frame = ctk.CTkFrame(main_frame)
        table_frame.grid(row=1, column=0, padx=10, pady=10, sticky="ew")
        table_frame.grid_columnconfigure(0, weight=1)
        
        ctk.CTkLabel(table_frame, text="CSV数据预览", font=("Arial", 14, "bold")).grid(row=0, column=0, padx=5, pady=5)
        
        # 使用文本框模拟表格
        self.table_text = ctk.CTkTextbox(table_frame, height=150)
        self.table_text.grid(row=1, column=0, padx=5, pady=5, sticky="ew")
        
        # 3. 配置参数区域
        config_frame = ctk.CTkFrame(main_frame)
        config_frame.grid(row=2, column=0, padx=10, pady=10, sticky="ew")
        config_frame.grid_columnconfigure(1, weight=1)
        config_frame.grid_columnconfigure(3, weight=1)
        
        # 比特浏览器接口
        ctk.CTkLabel(config_frame, text="比特浏览器接口:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.api_entry = ctk.CTkEntry(config_frame, placeholder_text="http://127.0.0.1:54345")
        self.api_entry.grid(row=0, column=1, padx=5, pady=5, sticky="ew")
        
        # 浏览器模式选择
        ctk.CTkLabel(config_frame, text="浏览器模式:").grid(row=0, column=2, padx=5, pady=5, sticky="w")
        self.browser_mode_var = ctk.StringVar(value="bitbrowser")
        self.browser_mode_combo = ctk.CTkComboBox(
            config_frame,
            values=["bitbrowser", "playwright"],
            variable=self.browser_mode_var,
            command=self.on_browser_mode_change,
            width=150
        )
        self.browser_mode_combo.grid(row=0, column=3, padx=5, pady=5, sticky="w")
        
        # 比特浏览器密码（替换groupId）
        ctk.CTkLabel(config_frame, text="比特浏览器密码:").grid(row=1, column=0, padx=5, pady=5, sticky="w")
        self.bitbrowser_password_entry = ctk.CTkEntry(config_frame, placeholder_text="删除窗口时需要（可选）", show="*")
        self.bitbrowser_password_entry.grid(row=1, column=1, padx=5, pady=5, sticky="ew")
        
        # 平台URL
        ctk.CTkLabel(config_frame, text="平台URL:").grid(row=1, column=2, padx=5, pady=5, sticky="w")
        self.url_entry = ctk.CTkEntry(config_frame, placeholder_text="https://klingai.com")
        self.url_entry.grid(row=1, column=3, padx=5, pady=5, sticky="ew")
        
        # 并发数
        ctk.CTkLabel(config_frame, text="并发数:").grid(row=2, column=0, padx=5, pady=5, sticky="w")
        self.concurrency_var = ctk.StringVar(value="3")
        self.concurrency_spinbox = ctk.CTkComboBox(
            config_frame, 
            values=[str(i) for i in range(1, 21)],
            variable=self.concurrency_var,
            width=100
        )
        self.concurrency_spinbox.grid(row=2, column=1, padx=5, pady=5, sticky="w")
        
        # 间隔时间
        ctk.CTkLabel(config_frame, text="间隔(ms):").grid(row=2, column=2, padx=5, pady=5, sticky="w")
        self.interval_var = ctk.StringVar(value="300")
        self.interval_spinbox = ctk.CTkComboBox(
            config_frame,
            values=[str(i*50) for i in range(0, 41)],
            variable=self.interval_var,
            width=100
        )
        self.interval_spinbox.grid(row=2, column=3, padx=5, pady=5, sticky="w")
        
        # 4. XPath配置区域
        xpath_frame = ctk.CTkFrame(main_frame)
        xpath_frame.grid(row=3, column=0, padx=10, pady=10, sticky="ew")
        xpath_frame.grid_columnconfigure(1, weight=1)
        
        # 启用自动化
        self.auto_var = ctk.BooleanVar(value=True)
        self.auto_checkbox = ctk.CTkCheckBox(xpath_frame, text="启用自动化注册（XPath）", variable=self.auto_var)
        self.auto_checkbox.grid(row=0, column=0, columnspan=4, padx=5, pady=5, sticky="w")
        
        # XPath文件
        ctk.CTkLabel(xpath_frame, text="XPath文件:").grid(row=1, column=0, padx=5, pady=5, sticky="w")
        self.xpath_entry = ctk.CTkEntry(xpath_frame, placeholder_text="选择XPath JSON文件...")
        self.xpath_entry.grid(row=1, column=1, padx=5, pady=5, sticky="ew")
        ctk.CTkButton(xpath_frame, text="浏览", command=self.browse_xpath, width=100).grid(row=1, column=2, padx=5, pady=5)
        
        # 5. 日志输出区域
        log_frame = ctk.CTkFrame(main_frame)
        log_frame.grid(row=4, column=0, padx=10, pady=10, sticky="nsew")
        log_frame.grid_columnconfigure(0, weight=1)
        log_frame.grid_rowconfigure(1, weight=1)
        
        ctk.CTkLabel(log_frame, text="运行日志", font=("Arial", 14, "bold")).grid(row=0, column=0, padx=5, pady=5)
        
        self.log_text = ctk.CTkTextbox(log_frame, height=200)
        self.log_text.grid(row=1, column=0, padx=5, pady=5, sticky="nsew")
        
        # 6. 按钮区域
        button_frame = ctk.CTkFrame(main_frame)
        button_frame.grid(row=5, column=0, padx=10, pady=10, sticky="ew")
        
        ctk.CTkButton(button_frame, text="开始注册", command=self.start_registration, 
                     fg_color="green", hover_color="darkgreen", width=150).pack(side="left", padx=5, pady=5)
        ctk.CTkButton(button_frame, text="保存参数", command=self.save_params, width=150).pack(side="left", padx=5, pady=5)
        ctk.CTkButton(button_frame, text="恢复默认", command=self.reset_params, width=150).pack(side="left", padx=5, pady=5)
        ctk.CTkButton(button_frame, text="退出", command=self.quit_app, 
                     fg_color="red", hover_color="darkred", width=150).pack(side="right", padx=5, pady=5)
    
    def browse_csv(self):
        """浏览CSV文件"""
        filename = filedialog.askopenfilename(
            title="选择CSV文件",
            filetypes=[("CSV文件", "*.csv"), ("所有文件", "*.*")]
        )
        if filename:
            self.csv_entry.delete(0, "end")
            self.csv_entry.insert(0, filename)
    
    def browse_xpath(self):
        """浏览XPath文件"""
        filename = filedialog.askopenfilename(
            title="选择XPath JSON文件",
            filetypes=[("JSON文件", "*.json"), ("所有文件", "*.*")]
        )
        if filename:
            self.xpath_entry.delete(0, "end")
            self.xpath_entry.insert(0, filename)
    
    def on_browser_mode_change(self, choice):
        """浏览器模式切换回调"""
        if choice == "playwright":
            # Playwright模式下禁用比特浏览器API输入
            self.api_entry.configure(state="disabled")
            self.bitbrowser_password_entry.configure(state="disabled")
            self.update_status("已切换到Playwright模式（本地浏览器+随机指纹）", "blue")
        else:
            # 比特浏览器模式
            self.api_entry.configure(state="normal")
            self.bitbrowser_password_entry.configure(state="normal")
            self.update_status("已切换到比特浏览器模式", "blue")
    
    def load_csv(self):
        """加载CSV文件"""
        csv_path = self.csv_entry.get()
        if not csv_path:
            self.update_status("请先选择CSV文件", "red")
            return
        
        try:
            p = Path(csv_path)
            if not p.exists():
                self.update_status("CSV文件不存在", "red")
                return
            
            rows = self.parse_csv_preview(p)
            if rows:
                # 检测表头
                candidates = ["email", "password", "host", "port", "code_url"]
                first_row = rows[0]
                is_header = any(str(cell).lower() in candidates for cell in first_row)
                data_rows = rows[1:] if (is_header and len(rows) > 1) else rows
                
                # 显示在表格中
                self.table_text.delete("1.0", "end")
                header = "邮箱\t密码\t接码地址\t代理IP\t端口\t用户名\t密码\n" + "-" * 100 + "\n"
                self.table_text.insert("1.0", header)
                
                for row in data_rows[:20]:  # 只显示前20行
                    row_text = "\t".join(str(cell) for cell in row[:7]) + "\n"
                    self.table_text.insert("end", row_text)
                
                self.update_status(f"已加载 {len(data_rows)} 行数据", "green")
            else:
                self.update_status("CSV为空", "red")
        except Exception as e:
            self.log.exception("Load CSV error")
            self.update_status(f"加载失败: {e}", "red")
    
    def parse_csv_preview(self, csv_path: Path) -> List[List[str]]:
        """解析CSV预览"""
        rows = []
        with csv_path.open("r", encoding="utf-8-sig", newline="") as f:
            sample = f.read(2048)
            f.seek(0)
            
            # 尝试自动检测CSV格式
            dialect = None
            try:
                detected_dialect = csv.Sniffer().sniff(sample)
                # 验证分隔符是否有效：必须是单字符且是常见分隔符
                valid_delimiters = [',', '\t', ';', '|']
                if (hasattr(detected_dialect, 'delimiter') and 
                    len(detected_dialect.delimiter) == 1 and
                    detected_dialect.delimiter in valid_delimiters):
                    dialect = detected_dialect
                    self.log.info(f"✅ 检测到CSV分隔符: '{detected_dialect.delimiter}'")
                else:
                    invalid_delim = getattr(detected_dialect, 'delimiter', 'unknown')
                    self.log.warning(f"⚠️ 检测到无效分隔符: '{invalid_delim}'，将尝试其他方式")
            except Exception as e:
                self.log.warning(f"⚠️ CSV格式检测失败: {e}，将使用默认格式")
            
            # 如果自动检测失败，尝试常见分隔符
            if dialect is None:
                for delim in [',', '\t', ';', '|']:
                    f.seek(0)
                    try:
                        test_reader = csv.reader(f, delimiter=delim)
                        first_row = next(test_reader)
                        if len(first_row) > 1:  # 至少有2列
                            f.seek(0)
                            dialect = csv.excel
                            dialect.delimiter = delim
                            self.log.info(f"✅ 使用分隔符: '{delim}'")
                            break
                    except Exception:
                        continue
            
            # 如果还是没找到，使用默认逗号
            if dialect is None:
                dialect = csv.excel
                self.log.info("⚠️ 使用默认逗号分隔符")
            
            f.seek(0)
            reader = csv.reader(f, dialect)
            for row in reader:
                rows.append(row)
        return rows
    
    def load_xpath_json(self, path: Path) -> Dict[str, Any]:
        """加载XPath JSON"""
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except Exception:
            return {}
    
    def start_registration(self):
        """开始注册"""
        csv_path = self.csv_entry.get()
        if not csv_path or not Path(csv_path).exists():
            self.update_status("请先选择并加载CSV文件", "red")
            messagebox.showerror("错误", "请先选择并加载CSV文件")
            return
        
        # 在新线程中运行注册流程
        thread = threading.Thread(target=self._run_registration, daemon=True)
        thread.start()
    
    def _run_registration(self):
        """执行注册流程（在后台线程）"""
        try:
            self.update_log("=" * 50 + "\n开始注册流程...\n" + "=" * 50 + "\n")
            
            csv_path = Path(self.csv_entry.get())
            auto = self.auto_var.get()
            
            # 获取XPath配置
            xjson = {}
            if auto:
                xpath_path = self.xpath_entry.get()
                if xpath_path and Path(xpath_path).exists():
                    xjson = self.load_xpath_json(Path(xpath_path))
                else:
                    self.update_log("⚠️ 警告：未指定XPath配置文件\n")
            
            # 执行批量注册
            browser_mode = self.browser_mode_var.get()
            
            # 根据浏览器模式决定是否传递bitbrowser_base_url
            if browser_mode == "playwright":
                # Playwright模式：不传bitbrowser_base_url，使用本地浏览器
                output = register_accounts_batch(
                    csv_path=csv_path,
                    runtime_dir=self.runtime_dir,
                    concurrency=int(self.concurrency_var.get()),
                    interval_ms=int(self.interval_var.get()),
                    bitbrowser_base_url=None,  # Playwright模式
                    platform_url=self.url_entry.get() or None,
                    group_id=None,
                    auto_xpaths=xjson,
                    dry_run=not auto or not bool(xjson),
                    browser_mode="playwright",  # 明确指定Playwright模式
                )
            else:
                # 比特浏览器模式
                output = register_accounts_batch(
                    csv_path=csv_path,
                    runtime_dir=self.runtime_dir,
                    concurrency=int(self.concurrency_var.get()),
                    interval_ms=int(self.interval_var.get()),
                    bitbrowser_base_url=self.api_entry.get() or None,
                    platform_url=self.url_entry.get() or None,
                    bitbrowser_password=self.bitbrowser_password_entry.get() or None,  # 比特浏览器密码
                    auto_xpaths=xjson,
                    dry_run=not auto or not bool(xjson),
                    browser_mode="bitbrowser",
                )
            
            self.update_log(output + "\n")
            self.update_status("注册流程完成", "green")
            
        except Exception as e:
            self.log.exception("Registration error")
            self.update_log(f"\n错误: {e}\n")
            self.update_status(f"注册失败: {e}", "red")
    
    def save_params(self):
        """保存参数"""
        try:
            cfg_update = {
                "csv_path": self.csv_entry.get(),
                "api_base": self.api_entry.get(),
                "platform_url": self.url_entry.get(),
                "bitbrowser_password": self.bitbrowser_password_entry.get(),  # 保存比特浏览器密码
                "concurrency": int(self.concurrency_var.get()),
                "interval_ms": int(self.interval_var.get()),
                "auto": self.auto_var.get(),
                "xpath_path": self.xpath_entry.get(),
                "browser_mode": self.browser_mode_var.get(),  # 保存浏览器模式
            }
            save_config(self.runtime_dir, cfg_update)
            self.update_status("参数已保存", "green")
            messagebox.showinfo("成功", "参数已保存")
        except Exception as e:
            self.log.exception("Save config error")
            self.update_status(f"保存失败: {e}", "red")
            messagebox.showerror("错误", f"保存失败: {e}")
    
    def reset_params(self):
        """恢复默认参数"""
        try:
            reset_config(self.runtime_dir)
            self.load_config_to_ui()
            self.update_status("已恢复默认参数", "green")
            messagebox.showinfo("成功", "已恢复默认参数")
        except Exception as e:
            self.log.exception("Reset config error")
            self.update_status(f"恢复失败: {e}", "red")
            messagebox.showerror("错误", f"恢复失败: {e}")
    
    def load_config_to_ui(self):
        """从配置文件加载到UI"""
        self.csv_entry.delete(0, "end")
        self.csv_entry.insert(0, self.cfg.get("csv_path", ""))
        
        self.api_entry.delete(0, "end")
        self.api_entry.insert(0, self.cfg.get("api_base", "http://127.0.0.1:54345"))
        
        self.url_entry.delete(0, "end")
        self.url_entry.insert(0, self.cfg.get("platform_url", "https://klingai.com"))
        
        self.bitbrowser_password_entry.delete(0, "end")
        self.bitbrowser_password_entry.insert(0, self.cfg.get("bitbrowser_password", ""))
        
        self.concurrency_var.set(str(self.cfg.get("concurrency", 3)))
        self.interval_var.set(str(self.cfg.get("interval_ms", 300)))
        
        self.auto_var.set(self.cfg.get("auto", True))
        
        self.xpath_entry.delete(0, "end")
        self.xpath_entry.insert(0, self.cfg.get("xpath_path", ""))
        
        # 加载浏览器模式
        browser_mode = self.cfg.get("browser_mode", "bitbrowser")
        self.browser_mode_var.set(browser_mode)
        # 触发一次模式切换回调
        self.on_browser_mode_change(browser_mode)
    
    def update_status(self, message: str, color: str = "white"):
        """更新状态标签"""
        self.status_label.configure(text=message, text_color=color)
    
    def update_log(self, message: str):
        """更新日志"""
        self.log_text.insert("end", message)
        self.log_text.see("end")
    
    def quit_app(self):
        """退出应用"""
        if messagebox.askokcancel("退出", "确定要退出吗？"):
            self.quit()
            self.destroy()


def launch(runtime_dir: Path):
    """启动CustomTkinter GUI"""
    app = KLZhanghaoApp(runtime_dir)
    app.mainloop()
