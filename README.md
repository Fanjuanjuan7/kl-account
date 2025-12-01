# KL-zhanghao - 可灵AI账号批量注册工具

基于Python和CustomTkinter的可灵AI（KlingAI）账号批量注册自动化工具，支持比特浏览器和Playwright双模式，完美兼容Windows和macOS系统。

## ✨ 核心功能

- ✅ **双浏览器模式**：支持比特浏览器（防关联）和Playwright（本地浏览器+随机指纹）
- ✅ **批量注册**：CSV文件批量导入账号，支持并发执行（可配置1-20并发）
- ✅ **智能滑块验证**：基于图像识别的滑块验证，最多10次重试，自动刷新验证码
- ✅ **验证码自动提取**：支持外部接码页面，自动提取6位验证码并填写
- ✅ **代理支持**：支持SOCKS5代理（比特浏览器模式）
- ✅ **状态追踪**：自动记录注册结果到CSV第9列（成功/失败）
- ✅ **失败清理**：注册失败自动删除比特浏览器窗口
- ✅ **现代化GUI**：CustomTkinter深色主题界面，实时日志输出

## 🚀 快速开始

### 系统要求

- **操作系统**：Windows 10/11 或 macOS 10.15+
- **Python版本**：3.10 或更高
- **浏览器**：
  - 比特浏览器模式：需安装[比特浏览器](https://www.bitbrowser.cn/)
  - Playwright模式：自动安装Chromium

### 一键安装

#### macOS / Linux

```bash
# 克隆项目
git clone https://github.com/Fanjuanjuan7/kl-account.git
cd kl-account

# 运行安装脚本（自动创建虚拟环境并安装依赖）
bash scripts/install.sh
```

#### Windows PowerShell

```powershell
# 克隆项目
git clone https://github.com/Fanjuanjuan7/kl-account.git
cd kl-account

# 运行安装脚本（以管理员身份运行PowerShell）
./scripts/install.ps1
```

### 一键启动

#### 🎯 双击启动（最简单）

**macOS用户**：
- 双击 `启动KL-zhanghao.command` 文件
- 或在终端运行：`./start.sh`

**Windows用户**：
- 双击 `启动KL-zhanghao.bat` 文件
- 或在PowerShell运行：`./start.ps1`

**首次运行**会自动安装依赖（需要几分钟），之后直接启动GUI。

**创建桌面快捷方式**：
- macOS：右键点击 `.command` 文件 → "制作替身" → 拖到桌面或Dock
- Windows：右键点击 `.bat` 文件 → "发送到" → "桌面快捷方式"

#### 📝 其他启动方式

**macOS / Linux**：
```bash
# 方式1：使用启动脚本
bash start.sh

# 方式2：使用scripts目录脚本
bash scripts/run.sh
```

**Windows PowerShell**：
```powershell
# 方式1：使用启动脚本
./start.ps1

# 方式2：使用scripts目录脚本
./scripts/run.ps1
```

#### 手动启动（可选）

```bash
# macOS/Linux
source .venv/bin/activate
python -m src.app.main

# Windows
.venv\Scripts\Activate.ps1
python -m src.app.main
```

## 📋 使用指南

### 1. 准备CSV文件

创建包含账号信息的CSV文件（参考 `samples/kl-mail.csv`）：

```csv
email,password,code_url,host,port,proxyUserName,proxyPassword,,
user1@outlook.com,Password123,https://mail-tool.com/code1,,,,,
user2@gmail.com,Password456,https://mail-tool.com/code2,1.2.3.4,1080,user,pass,,
```

**列说明**：

| 列位置 | 字段名 | 是否必填 | 说明 |
|--------|--------|----------|------|
| 第1列 | email | ✅ 必填 | 注册邮箱地址 |
| 第2列 | password | ✅ 必填 | 注册密码 |
| 第3列 | code_url | ✅ 必填 | 验证码接码页面地址 |
| 第4列 | host | ⭕ 可选 | 代理IP地址 |
| 第5列 | port | ⭕ 可选 | 代理端口 |
| 第6列 | proxyUserName | ⭕ 可选 | 代理用户名 |
| 第7列 | proxyPassword | ⭕ 可选 | 代理密码 |
| 第8列 | - | 空列 | 保留列 |
| 第9列 | status | 自动 | 注册状态（成功/失败） |

**注意**：
- 第9列由程序自动填写，无需手动填写
- 代理仅在比特浏览器模式下生效
- Playwright模式不支持SOCKS5认证代理

### 2. 配置XPath文件

创建XPath配置文件（参考 `samples/kling_xpaths.json`）：

```json
{
  "email_input": "//input[@placeholder='Email']",
  "password_input": "//input[@placeholder='Password']",
  "code_input": "//*[@style='font-size: 28px; border-radius: 8px; background-color: #efefef; color: black; font-weight: 600; text-align: center; padding: 12px 24px; border: solid 1px black;']",
  "code_url_element": "//*[@placeholder='Verification Code']",
  "next_btn": "//*[@class='inner' and text()='Next']",
  "slider_xpath": "//*[@class='btn-icon']",
  "slider_iframe": "//iframe[contains(@src, 'captcha')]",
  "final_submit_btn": "//*[@class='inner' and text()='Sign Up']"
}
```

### 3. 启动并配置GUI

#### 比特浏览器模式

1. **启动比特浏览器**，确保API服务开启（默认：`http://127.0.0.1:54345`）
2. **启动本工具**：`bash scripts/run.sh`（macOS）或 `./scripts/run.ps1`（Windows）
3. **GUI配置**：
   - 选择CSV文件
   - 选择XPath JSON文件
   - 浏览器模式：选择 **bitbrowser**
   - 比特浏览器接口：`http://127.0.0.1:54345`
   - 比特浏览器密码：如果设置了密码，在此输入（用于删除失败窗口）
   - 并发数：建议3-5
   - 间隔时间：300ms
   - ✅ 勾选"启用自动化注册（XPath）"
4. **点击"开始注册"**

#### Playwright模式（无需比特浏览器）

1. **启动本工具**：`bash scripts/run.sh`（macOS）或 `./scripts/run.ps1`（Windows）
2. **GUI配置**：
   - 选择CSV文件
   - 选择XPath JSON文件
   - 浏览器模式：选择 **playwright**
   - 并发数：建议1-3（本地模式资源占用较高）
   - 间隔时间：300ms
   - ✅ 勾选"启用自动化注册（XPath）"
3. **点击"开始注册"**

### 4. 监控注册进度

- **日志输出**：GUI底部实时显示注册日志
- **CSV状态**：注册完成后，CSV第9列自动更新为"成功"或"失败"
- **浏览器窗口**：
  - 比特浏览器模式：成功的窗口保留，失败的自动删除
  - Playwright模式：每次注册完成后自动关闭

## 🔧 功能详解

### 滑块验证机制

1. **图像识别**：使用OpenCV模板匹配自动定位缺口位置
2. **相对坐标**：计算拼图块到缺口的相对距离
3. **拟人轨迹**：模拟加速→减速→抖动的真实拖动
4. **智能重试**：
   - 最多10次尝试
   - 每次失败等待5秒让验证码自动刷新
   - 不刷新整个页面，保持注册进度

### 并发执行机制

- **线程池**：使用`ThreadPoolExecutor`实现真正的并发
- **资源管理**：每个线程独立创建浏览器窗口
- **失败处理**：异常或失败时自动删除窗口，释放资源
- **状态同步**：实时更新CSV文件状态

### 验证码处理流程

1. 滑块验证成功后，自动打开验证码接码页面（新标签页）
2. 使用XPath提取6位数字验证码
3. 自动切换回注册页面
4. 填写验证码并提交

## 📁 项目结构

```
kl-account/
├── 启动KL-zhanghao.command  # macOS双击启动文件
├── 启动KL-zhanghao.bat      # Windows双击启动文件
├── start.sh                 # macOS/Linux主启动脚本
├── start.ps1                # Windows主启动脚本
├── 一键启动指南.md         # 详细启动说明文档
├── scripts/                 # 安装和运行脚本
│   ├── install.sh          # macOS/Linux 安装脚本
│   ├── install.ps1         # Windows 安装脚本
│   ├── run.sh              # macOS/Linux 运行脚本
│   └── run.ps1             # Windows 运行脚本
├── src/
│   ├── app/                # 应用入口
│   │   └── main.py         # 主程序
│   ├── gui/                # GUI界面
│   │   └── ui_ctk.py       # CustomTkinter界面
│   ├── services/           # 核心服务
│   │   ├── account.py      # 账号批量处理
│   │   └── automation.py   # 自动化注册流程
│   ├── integrations/       # 第三方集成
│   │   └── bitbrowser.py   # 比特浏览器API客户端
│   └── utils/              # 工具模块
│       ├── logger.py       # 日志管理
│       └── config_store.py # 配置管理
├── samples/                # 示例文件
│   ├── kl-mail.csv         # CSV示例
│   └── kling_xpaths.json   # XPath配置示例
├── requirements.txt        # Python依赖
├── .gitignore
└── README.md
```

## 🛠️ 技术栈

- **语言**：Python 3.10+
- **GUI框架**：CustomTkinter 5.2+
- **浏览器自动化**：Playwright（Sync API）
- **图像识别**：OpenCV + Pillow + NumPy
- **HTTP客户端**：httpx
- **比特浏览器集成**：比特浏览器API

## ❓ 常见问题

### 1. 安装失败

**Windows PowerShell执行策略错误**：
```powershell
# 以管理员身份运行PowerShell
Set-ExecutionPolicy RemoteSigned -Scope CurrentUser
```

**macOS/Linux权限错误**：
```bash
chmod +x scripts/install.sh
chmod +x scripts/run.sh
```

### 2. 比特浏览器连接失败

- 确认比特浏览器已启动
- 检查API接口地址：默认 `http://127.0.0.1:54345`
- 查看比特浏览器设置中是否开启了API服务

### 3. 滑块验证总是失败

- 检查网络连接，确保验证码图片能够下载
- 查看日志中的图像识别结果
- 如果置信度过低（<0.5），可能是图片质量问题
- 10次重试后仍失败，可能需要手动完成验证

### 4. CSV加载失败

- 确保CSV使用UTF-8编码
- 支持的分隔符：`,`（逗号）、`\t`（制表符）、`;`（分号）、`|`（竖线）
- 检查CSV文件是否有特殊字符或格式错误

### 5. Playwright模式闪退

- 不要使用需要认证的SOCKS5代理
- 确保已安装Chromium：`python -m playwright install chromium`
- 降低并发数到1-2

## 📊 性能建议

### 并发配置

| 模式 | 推荐并发数 | 说明 |
|------|-----------|------|
| 比特浏览器模式 | 3-5 | 取决于机器性能和网络 |
| Playwright模式 | 1-3 | 资源占用较高 |

### 资源占用

- **内存**：每个浏览器实例约500MB-1GB
- **CPU**：图像识别时CPU占用较高
- **网络**：取决于并发数和代理速度

## 🔐 安全与隐私

- ✅ 所有数据仅在本地处理
- ✅ 不上传任何用户信息
- ✅ 密码在GUI中使用遮罩显示
- ✅ 配置文件存储在用户目录 `~/.kl_zhanghao/`
- ⚠️ 请妥善保管CSV文件中的账号密码

## 📝 更新日志

### v2.0.0 (2025-12-01)

- ✅ 新增Playwright模式，无需比特浏览器
- ✅ 实现真正的并发执行（线程池）
- ✅ 滑块验证重试次数增加到10次
- ✅ 自动删除失败的浏览器窗口
- ✅ CSV状态自动记录（第9列）
- ✅ GUI密码字段替换GroupId
- ✅ 图像识别优化，提高验证成功率
- ✅ 移除二次重试机制，避免重复处理
- ✅ 跨平台CSV解析增强

## 📄 许可证

MIT License

## 🤝 贡献

欢迎提交Issue和Pull Request！

---

**⚠️ 免责声明**：本工具仅供学习和研究使用，请遵守相关法律法规和网站服务条款。
