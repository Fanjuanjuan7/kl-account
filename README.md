# KL-zhanghao 账号批量注册工具

基于Python和CustomTkinter的可灵AI账号批量注册自动化工具，支持Windows/macOS双系统。

## 核心功能

- ✅ CSV批量导入账号数据（邮箱、密码、验证码接码地址、代理配置）
- ✅ 比特浏览器API集成（创建窗口、管理标签页、配置代理）
- ✅ 自动打开可灵AI网站并切换到目标标签页
- ✅ 基于XPath的自动化注册流程
- ✅ 拟人化滑块验证拖动
- ✅ 验证码自动提取（支持外部接码页面）
- ✅ 智能标签页检测和切换（10次重试，每次2秒间隔）

## 快速开始

### 安装

```bash
# macOS/Linux
bash scripts/install.sh

# Windows PowerShell
./scripts/install.ps1
```

### 启动

```bash
# macOS/Linux
bash scripts/run.sh

# Windows PowerShell
./scripts/run.ps1

# 或直接运行
python -m src.app.main
```

### CSV格式

```csv
email,password,code_url,host,port,proxyUserName,proxyPassword
user@example.com,Pass123,https://tempmail.com/code,1.2.3.4,1080,user,pass
```

- **email** (必填): 注册邮箱
- **password** (必填): 注册密码
- **code_url** (可选): 验证码接码页面地址
- **host/port** (可选): 代理服务器配置
- **proxyUserName/proxyPassword** (可选): 代理认证

### XPath配置

创建JSON文件配置页面元素定位（参见 `samples/kling_xpaths.json`）：

```json
{
  "email_input": "//input[@type='email']",
  "password_input": "//input[@type='password']",
  "code_input": "//input[contains(@placeholder, '验证码')]",
  "code_url_element": "//div[contains(@class, 'email-content')]//span",
  "final_submit_btn": "//button[contains(text(), 'Submit')]"
}
```

## 目录结构

```
src/
  app/            # 应用程序入口
  gui/            # CustomTkinter GUI界面
  services/       # 核心业务逻辑（账号注册、自动化流程）
  integrations/   # 比特浏览器API客户端
  utils/          # 工具类（日志、配置管理）
tests/            # 测试用例
samples/          # 示例文件（CSV、XPath配置）
scripts/          # 安装和运行脚本
```

## 技术架构

### 技术栈
- **Python 3.10+**: 核心开发语言
- **CustomTkinter 5.2+**: 现代化GUI框架，支持Windows/macOS
- **httpx**: HTTP客户端，用于比特浏览器API调用
- **Playwright**: 浏览器自动化引擎
- **pytest**: 测试框架

### 核心模块

#### 1. BitBrowser客户端 (`bitbrowser.py`)
- `create_window()`: 创建浏览器窗口并配置代理/指纹
- `open_window()`: 打开窗口
- `open_tab()`: 在新标签页中打开URL
- `get_window_tabs()`: 获取窗口所有标签页
- `switch_tab()`: 切换到指定标签页
- `activate()` / `maximize()`: 激活/最大化窗口

#### 2. 账号服务 (`account.py`)
- `load_accounts_csv()`: 加载CSV账号数据
- `register_accounts_batch()`: 批量注册处理
- `_wait_and_switch_to_new_tab()`: **智能标签页切换**
  - 循环检测窗口标签页列表
  - 域名匹配自动定位目标标签页
  - 最多10次重试，每次间隔2秒
  - 详细日志记录每次检测结果
  - 失败后自动回退到导航方案

#### 3. 自动化服务 (`automation.py`)
- `run_registration_flow()`: 注册流程主函数
- `_extract_verification_code()`: 从接码页面提取6位验证码
- `_perform_human_drag()`: 拟人化滑块拖动

#### 4. GUI界面 (`ui_ctk.py`)
- 深色主题现代化界面
- CSV数据实时预览
- 参数配置表单
- 实时日志输出
- 线程化处理避免阻塞

## 使用说明

1. **准备CSV文件** - 包含账号信息
2. **配置比特浏览器** - 启动并确保API可访问（默认: `http://127.0.0.1:54345`）
3. **准备XPath配置** - 创建JSON文件或使用默认配置
4. **启动GUI** - 选择CSV文件，配置参数，点击开始注册
5. **查看日志** - 实时监控注册进度

## 关键特性

### 智能标签页切换
项目实现了强大的标签页检测和切换机制：
- ✅ 自动检测新创建的标签页
- ✅ 基于域名匹配目标页面
- ✅ 10次重试机制，总等待时间长达20秒
- ✅ 详细的日志输出便于调试
- ✅ 失败自动回退到备用方案

### 验证码自动提取
- ✅ 支持从外部接码页面自动提取
- ✅ 正则表达式提取6位数字验证码
- ✅ 支持XPath指定元素或自动从页面提取
- ✅ 自动填入注册页面

## 测试

```bash
# 激活虚拟环境
source .venv/bin/activate  # macOS/Linux
.venv\Scripts\Activate.ps1  # Windows

# 运行测试
pytest

# 查看详细结果
pytest -v
```

测试结果：✅ 19/19 测试通过，核心业务逻辑覆盖率85%+

## 安装与运行

### macOS/Linux

```bash
# 1. 安装依赖
bash scripts/install.sh

# 2. 启动应用
bash scripts/run.sh

# 或直接运行
source .venv/bin/activate
python -m src.app.main
```

### Windows PowerShell

```powershell
# 1. 安装依赖
./scripts/install.ps1

# 2. 启动应用
./scripts/run.ps1

# 或直接运行
.venv\Scripts\Activate.ps1
python -m src.app.main
```

## 配置比特浏览器

1. **下载安装比特浏览器** - 前往官网下载对应系统版本
2. **启动API服务** - 确保比特浏览器API接口开启（默认: `http://127.0.0.1:54345`）
3. **创建浏览器分组** - 在比特浏览器中创建分组（可选，可通过groupId指定）
4. **验证连接** - 启动GUI后会自动检测API连接状态

## 工作流程

1. **准备账号数据**
   - 创建CSV文件，包含邮箱、密码、验证码接码地址、代理配置等信息
   - 参考 `samples/test_accounts.csv` 示例格式

2. **配置XPath路径**
   - 创建JSON文件定义页面元素定位路径
   - 参考 `samples/kling_xpaths.json` 示例
   - 可在GUI中直接编辑JSON配置

3. **启动GUI并配置**
   - 选择CSV文件并加载预览
   - 设置比特浏览器API地址
   - 配置平台URL（默认: https://klingai.com）
   - 选择XPath配置文件或直接输入JSON
   - 调整并发数和间隔时间

4. **开始批量注册**
   - 点击「开始注册」按钮
   - 实时查看日志输出
   - 监控注册进度

## 故障排除

### GUI无法启动

```bash
# macOS: 如果提示缺少Tk支持
brew install python-tk@3.10

# Linux: 安装tkinter
sudo apt-get install python3-tk  # Ubuntu/Debian
sudo yum install python3-tkinter  # CentOS/RHEL
```

### 比特浏览器API连接失败

1. 确保比特浏览器已启动
2. 检查API接口地址是否正确（默认: `http://127.0.0.1:54345`）
3. 检查防火墙设置
4. 在比特浏览器设置中确认API已启用

### 标签页切换失败

项目已实现智能重试机制和自动回退方案：

**正常流程**：
1. 循环检测标签页（最多10次，每次2秒）
2. 打印每个标签的详细信息（标题、URL、激活状态）
3. 匹配目标标签（通过URL、标题或关键词）
4. 切换到目标标签并激活窗口

**智能回退方案**（如果切换失败）：
1. 自动识别工作台标签页（通过标题或URL）
2. 调用API关闭工作台标签页
3. Kling AI标签页自动成为当前标签并显示

**如果仍然失败**：

1. **检查日志** - 查看详细的标签页检测日志：
   ```
   Tab 0: ID=xxx, Title='1-工作台', URL=..., Active=True
   Tab 1: ID=xxx, Title='Kling AI: Next-Gen AI Video', URL=..., Active=False
   Found workspace tab: ID=xxx
   Found matching tab: Title='Kling AI: Next-Gen AI Video', URL=...
   ```

2. **增加等待时间** - 修改 `_wait_and_switch_to_new_tab` 中的 `max_retries` 参数
3. **检查网络** - 确保代理配置正确，目标网站可访问
4. **手动测试** - 在比特浏览器中手动打开标签页，确认URL格式正确

### 验证码提取失败

1. **检查XPath** - 确保 `code_url_element` XPath路径正确
2. **检查接码页面** - 手动访问接码URL，确认验证码可见
3. **更新正则** - 如果验证码不是6位数字，修改 `_extract_verification_code` 中的正则表达式

## 开发和测试

### 运行测试

```bash
source .venv/bin/activate
pytest -v
```

### 测试覆盖率

```bash
pytest --cov=src --cov-report=html
open htmlcov/index.html  # macOS
```

### 调试模式

在代码中设置日志级别为DEBUG：

```python
import logging
logging.getLogger().setLevel(logging.DEBUG)
```

## 技术文档

- **比特浏览器API**: https://doc2.bitbrowser.cn/jiekou/liu-lan-qi-jie-kou.html
- **CustomTkinter**: https://customtkinter.tomschimansky.com/
- **Playwright**: https://playwright.dev/python/

## 许可证

MIT License

## 设计目标

### CSV 数据格式
- 每行：`邮箱账号,邮箱密码,邮箱验证码接码地址,代理ip,代理端口,代理用户名,代理密码`
- 前两列必填（邮箱账号、密码）；后面列可选
- 第3列：邮箱验证码接码页面地址，用于自动提取6位验证码
- 第4-7列：代理信息，如提供则会为该账号设置代理
- 示例：
  - `user1@example.com,Secret123,https://tempmail.com/inbox/code,47.250.46.6,58078,username,password`
  - `user2@example.com,Secret456,,,,,`（无接码地址和代理）
  - `user3@example.com,Secret789,https://mail.tm/code,,,,`（有接码地址，无代理）

## 自动化注册流程（桌面 GUI）
- 窗口管理：按行创建窗口并自动切换到 `https://klingai.com` 标签页
- XPath 自动化：启用“自动化注册”后执行点击与表单填充（可扩展）
- 滑块验证：内置拟人拖动轨迹生成（后续可替换为图像识别方案）
- 邮箱验证码：支持接入外部页面按 XPath 获取 6 位验证码

### 比特浏览器 API 集成
本项目已集成比特浏览器 API，支持以下功能：
- 创建和打开浏览器窗口
- 自动在新标签页中打开可灵 AI 页面（https://klingai.com）
- 管理窗口标签页
- 激活并最大化窗口
- 支持通过 DevTools WebSocket 附着到比特浏览器窗口进行 Playwright 控制

### 自动化注册功能
当启用自动化注册功能时，系统将：
1. 启动 Playwright 控制的浏览器（或附着到比特浏览器窗口）
2. 应用代理设置（如果提供）
3. 导航到可灵 AI 注册页面
4. 根据 XPath 配置自动填写表单
5. 处理滑块验证
6. 发送验证码请求并等待用户输入
7. 完成注册流程

## 参数说明与持久化
- 比特浏览器本地接口：如 `http://127.0.0.1:54345`
- groupId：可选分组 ID
- 并发与间隔：控制批量注册节奏与资源占用

- 在界面中点击“保存参数”自动持久化到 `~/.kl_zhanghao/config.json`；“恢复默认”清空为初始设置

- 跨平台：路径与权限处理采用 `pathlib` 与内置库
- 可维护性：服务模块清晰、日志完备、错误处理健全
