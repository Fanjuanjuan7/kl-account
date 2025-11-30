from pathlib import Path
from typing import Dict, Any, Optional
import time
import random
from playwright.sync_api import sync_playwright, Page, BrowserContext
from ..utils.logger import get_logger


def _generate_random_fingerprint() -> Dict[str, Any]:
    """
    生成随机浏览器指纹
    返回适用于Playwright new_context()的参数
    支持Windows和Mac平台
    """
    import platform
    import random
    
    # 常见用户代理
    user_agents_win = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:120.0) Gecko/20100101 Firefox/120.0",
    ]
    
    user_agents_mac = [
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Safari/605.1.15",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Safari/605.1.15",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:121.0) Gecko/20100101 Firefox/121.0",
    ]
    
    # 根据操作系统选择UA
    system = platform.system()
    if system == "Windows":
        user_agents = user_agents_win
    else:  # Mac 和 Linux
        user_agents = user_agents_mac
    
    # 屏幕分辨率
    screen_sizes = [
        {"width": 1920, "height": 1080},
        {"width": 1366, "height": 768},
        {"width": 1536, "height": 864},
        {"width": 1440, "height": 900},
        {"width": 2560, "height": 1440},
    ]
    
    # 时区
    timezones = [
        "America/New_York",
        "America/Chicago",
        "America/Los_Angeles",
        "Europe/London",
        "Europe/Paris",
        "Asia/Tokyo",
        "Asia/Shanghai",
        "Asia/Hong_Kong",
    ]
    
    # 语言
    locales = ["en-US", "en-GB", "zh-CN", "ja-JP", "de-DE", "fr-FR"]
    
    screen = random.choice(screen_sizes)
    
    fingerprint = {
        "user_agent": random.choice(user_agents),
        "viewport": {
            "width": screen["width"],
            "height": screen["height"] - random.randint(0, 100)  # 减去任务栏高度
        },
        "screen": screen,
        "timezone_id": random.choice(timezones),
        "locale": random.choice(locales),
        "color_scheme": random.choice(["light", "dark", "no-preference"]),
        "device_scale_factor": random.choice([1, 1.25, 1.5, 2]),
    }
    
    return fingerprint


def _human_drag_track(distance: int) -> Dict[str, Any]:
    # 生成拟人拖动轨迹：初始加速，末端减速，带抖动
    steps = []
    pos = 0
    v = 0
    while pos < distance:
        a = random.uniform(2, 5)
        v += a
        move = max(1, int(v))
        pos += move
        steps.append(move)
        if pos > distance * 0.6:
            v -= random.uniform(1, 3)
        if pos > distance:
            steps.append(distance - (pos - move))
            break
    # 微调与抖动
    for _ in range(random.randint(2, 4)):
        steps.append(random.choice([1, -1]))
    return {"steps": steps}


def _perform_human_drag(page: Page, slider_xpath: str, container_xpath: Optional[str] = None) -> bool:
    """
    执行拟人化滑块拖动
    
    参数：
        page: Playwright页面对象
        slider_xpath: 滑块元素的XPath
        container_xpath: 滑块容器的XPath（用于计算拖动距离）
    
    返回：
        成功返回True，否则返回False
    """
    log = get_logger(__name__)
    try:
        log.info(f"Looking for slider with XPath: {slider_xpath}")
        
        # 等待滑块出现
        slider = page.wait_for_selector(f"xpath={slider_xpath}", timeout=10000)
        if not slider:
            log.warning("Slider not found")
            return False
        
        log.info("Slider found, getting bounding box")
        box = slider.bounding_box()
        if not box:
            log.warning("Failed to get slider bounding box")
            return False
        
        # 计算拖动距离
        distance = 300  # 默认距离
        
        # 如果有容器XPath，尝试根据容器宽度计算
        if container_xpath:
            try:
                container = page.wait_for_selector(f"xpath={container_xpath}", timeout=5000)
                if container:
                    container_box = container.bounding_box()
                    if container_box:
                        # 拖动距离 = 容器宽度 - 滑块宽度 - 20px缓冲
                        distance = int(container_box["width"] - box["width"] - 20)
                        log.info(f"Calculated drag distance from container: {distance}px")
            except Exception as e:
                log.warning(f"Failed to calculate distance from container: {e}")
        
        # 起始位置
        start_x = box["x"] + box["width"] / 2
        start_y = box["y"] + box["height"] / 2
        
        log.info(f"Starting drag from ({start_x}, {start_y}) with distance {distance}px")
        
        # 生成拟人化轨迹
        track = _human_drag_track(distance)
        steps = track["steps"]
        
        # 开始拖动
        page.mouse.move(start_x, start_y)
        time.sleep(random.uniform(0.1, 0.3))  # 模拟人类思考
        page.mouse.down()
        time.sleep(random.uniform(0.05, 0.15))  # 按下后稍等
        
        current_x = start_x
        for i, step in enumerate(steps):
            current_x += step
            # 添加微小的垂直抖动
            jitter_y = start_y + random.randint(-2, 2)
            page.mouse.move(current_x, jitter_y)
            # 模拟人类拖动的时间间隔
            time.sleep(random.uniform(0.008, 0.025))
        
        # 释放鼠标前稍等
        time.sleep(random.uniform(0.1, 0.2))
        page.mouse.up()
        
        log.info("Slider drag completed successfully")
        
        # 等待验证结果
        time.sleep(2)
        return True
        
    except Exception as e:
        log.error(f"Slider drag failed: {e}")
        try:
            # 尝试截图便于调试
            page.screenshot(path="slider_error.png")
            log.info("Screenshot saved to slider_error.png")
        except Exception:
            pass
        return False


def _extract_verification_code(page: Page, code_xpath: str, max_wait: int = 30) -> Optional[str]:
    """
    从邮箱接码页面提取验证码
    参数：
        page: Playwright页面对象
        code_xpath: 验证码元素的XPath
        max_wait: 最大等待时间（秒）
    返回：
        6位验证码字符串，如果提取失败则返回None
    """
    import re
    log = get_logger(__name__)
    
    try:
        # 等待验证码元素出现
        log.info(f"Waiting for verification code element: {code_xpath}")
        loc = page.locator(f"xpath={code_xpath}")
        loc.wait_for(state="visible", timeout=max_wait * 1000)
        
        # 获取文本内容
        code_text = loc.inner_text()
        log.info(f"Extracted text: {code_text}")
        
        # 使用正则表达式提取6位数字
        match = re.search(r'\b\d{6}\b', code_text)
        if match:
            code = match.group(0)
            log.info(f"Successfully extracted verification code: {code}")
            return code
        else:
            log.warning(f"No 6-digit code found in text: {code_text}")
            return None
    except Exception as e:
        log.error(f"Failed to extract verification code: {e}")
        return None


def run_registration_flow(
    email: str,
    password: str,
    runtime_dir: Path,
    xpaths: Dict[str, str],
    proxy: Optional[Dict[str, Any]] = None,
    platform_url: Optional[str] = None,
    code_url: Optional[str] = None,
    attach_ws: Optional[str] = None,
    dry_run: bool = False,
    browser_mode: str = "bitbrowser",  # 浏览器模式
) -> bool:
    # 占位实现：后续接入 Playwright 与页面操作
    # 当前版本：在 dry_run=True 时仅返回成功，便于流程调试与批处理联通
    if dry_run:
        time.sleep(0.05)
        return True
    
    log = get_logger(__name__)
    try:
        with sync_playwright() as p:
            # 启动浏览器
            browser = None
            page = None
            context = None
            
            # 如果有attach_ws，尝试附着到比特浏览器
            if attach_ws:
                try:
                    log.info(f"Attempting to attach to BitBrowser via WebSocket: {attach_ws}")
                    browser = p.chromium.connect_over_cdp(attach_ws)
                    log.info("Successfully connected to BitBrowser")
                    
                    # 使用已有上下文与页面
                    contexts = browser.contexts
                    if contexts:
                        context = contexts[0]
                        log.info(f"Found {len(context.pages)} pages in context")
                        
                        # 详细列出所有页面
                        for idx, p_page in enumerate(context.pages):
                            page_url = p_page.url
                            page_title = p_page.title()
                            log.info(f"  Page {idx}: Title='{page_title}', URL={page_url}")
                        
                        # 查找Kling AI标签页（优先匹配）
                        for p_page in context.pages:
                            page_url = p_page.url
                            page_title = p_page.title()
                            if "klingai" in page_url.lower() or "kling" in page_title.lower():
                                page = p_page
                                log.info(f"✅ Found Kling AI page: Title='{page_title}', URL={page_url}")
                                break
                        
                        # 如果没找到Kling AI页面，使用最后一个页面（通常是最新打开的）
                        if not page and context.pages:
                            page = context.pages[-1]
                            page_url = page.url
                            page_title = page.title()
                            log.info(f"Using last page: Title='{page_title}', URL={page_url}")
                            
                            # 如果当前页面不是Kling AI，导航到Kling AI
                            if "klingai" not in page.url.lower() and "kling" not in page_title.lower():
                                target_url = platform_url or "https://klingai.com"
                                log.info(f"Current page is not Kling AI, navigating to: {target_url}")
                                try:
                                    page.goto(target_url, timeout=30000, wait_until="domcontentloaded")
                                    log.info(f"Successfully navigated to {target_url}")
                                    # 等待页面加载完成
                                    page.wait_for_load_state("networkidle", timeout=30000)
                                    log.info("Page loaded successfully")
                                except Exception as nav_error:
                                    log.error(f"Failed to navigate: {nav_error}")
                                    # 如果导航失败，至少等待DOM加载
                                    try:
                                        page.wait_for_load_state("domcontentloaded", timeout=10000)
                                    except:
                                        pass
                    
                    if page:
                        log.info("✅ Successfully attached to BitBrowser page")
                    else:
                        log.warning("No suitable page found, will create new browser")
                        browser = None
                        
                except Exception as e:
                    log.error(f"Failed to attach to BitBrowser: {e}")
                    import traceback
                    log.error(traceback.format_exc())
                    browser = None
            
            # 如果没有附着成功，创建新浏览器
            if not browser:
                log.info("Launching new browser instance")
                
                # 准备上下文配置
                context_options = {}
                
                # Playwright模式：应用随机指纹
                if browser_mode == "playwright":
                    fingerprint = _generate_random_fingerprint()
                    context_options.update(fingerprint)
                    log.info(f"🔍 Playwright模式 - 随机指纹已应用")
                    log.info(f"  UA: {fingerprint['user_agent'][:50]}...")
                    log.info(f"  Viewport: {fingerprint['viewport']['width']}x{fingerprint['viewport']['height']}")
                    log.info(f"  Timezone: {fingerprint['timezone_id']}")
                    log.info(f"  Locale: {fingerprint['locale']}")
                
                # 准备代理配置
                # 注意：Playwright的Chromium不支持SOCKS5代理的用户名密码认证
                # 解决方案：优先尝试HTTP代理，如果不可用再跳过
                if proxy and proxy.get("host") and proxy.get("port"):
                    has_auth = proxy.get("username") and proxy.get("password")
                    proxy_host = proxy['host']
                    proxy_port = proxy['port']
                    
                    if has_auth:
                        # 有认证信息：尝试HTTP代理（Playwright支持HTTP代理认证）
                        log.info("🔑 Proxy with authentication detected")
                        log.info("💡 Attempting to use HTTP proxy (Playwright supports HTTP auth)")
                        
                        try:
                            proxy_config = {
                                "server": f"http://{proxy_host}:{proxy_port}",
                                "username": proxy.get("username"),
                                "password": proxy.get("password")
                            }
                            context_options["proxy"] = proxy_config
                            log.info(f"✅ Using HTTP proxy with auth: {proxy_host}:{proxy_port}")
                            log.info(f"   Username: {proxy.get('username')}")
                        except Exception as proxy_err:
                            log.warning(f"⚠️ HTTP proxy setup failed: {proxy_err}")
                            log.warning("🔄 Falling back to direct connection")
                    else:
                        # 无认证：使用SOCKS5
                        proxy_config = {
                            "server": f"socks5://{proxy_host}:{proxy_port}",
                        }
                        context_options["proxy"] = proxy_config
                        log.info(f"✅ Using SOCKS5 proxy (no auth): {proxy_host}:{proxy_port}")
                else:
                    log.info("🌐 No proxy configured, using direct connection")
                
                try:
                    browser = p.chromium.launch(
                        headless=False,
                        args=[
                            '--start-maximized',  # 窗口最大化
                            '--disable-blink-features=AutomationControlled',  # 隐藏自动化特征
                        ]
                    )
                    context = browser.new_context(
                        **context_options,
                        no_viewport=True  # 使用浏览器窗口大小而不是固定视口
                    )
                    page = context.new_page()
                    log.info("✅ 浏览器启动成功（最大化窗口）")
                except Exception as launch_err:
                    # 如果代理启动失败，尝试不用代理重试
                    if "proxy" in context_options:
                        log.error(f"❌ 使用代理启动浏览器失败: {launch_err}")
                        log.warning("🔄 不使用代理重试...")
                        context_options.pop("proxy", None)
                        browser = p.chromium.launch(
                            headless=False,
                            args=['--start-maximized', '--disable-blink-features=AutomationControlled']
                        )
                        context = browser.new_context(**context_options, no_viewport=True)
                        page = context.new_page()
                        log.info("✅ 浏览器启动成功（无代理）")
                    else:
                        raise
                
                # 导航到注册页面并置前
                target_url = platform_url or "https://klingai.com"
                log.info(f"🌍 Navigating to {target_url}")
                
                try:
                    # 使用更长的超时时间，并使用domcontentloaded等待策略
                    page.goto(target_url, timeout=60000, wait_until="domcontentloaded")
                    log.info("✅ Page navigation started, waiting for content...")
                    
                    # 尝试等待networkidle，但不强制
                    try:
                        page.wait_for_load_state("networkidle", timeout=30000)
                        log.info("✅ Page fully loaded (networkidle)")
                    except Exception as load_err:
                        log.warning(f"⚠️ Network idle timeout, but page content may be ready: {load_err}")
                        # 等待domcontentloaded就够了
                        try:
                            page.wait_for_load_state("domcontentloaded", timeout=10000)
                            log.info("✅ Page content loaded (domcontentloaded)")
                        except Exception:
                            log.warning("⚠️ DOM content load timeout, continuing anyway...")
                
                except Exception as nav_err:
                    log.error(f"❌ Page navigation failed: {nav_err}")
                    # 如果是代理问题，尝试不用代理重试
                    if "proxy" in context_options:
                        log.warning("🔄 Retrying without proxy due to navigation failure...")
                        
                        # 关闭当前浏览器
                        try:
                            browser.close()
                        except Exception:
                            pass
                        
                        # 移除代理配置
                        context_options.pop("proxy", None)
                        
                        # 重新启动浏览器
                        browser = p.chromium.launch(
                            headless=False,
                            args=['--start-maximized', '--disable-blink-features=AutomationControlled']
                        )
                        context = browser.new_context(**context_options, no_viewport=True)
                        page = context.new_page()
                        log.info("✅ 浏览器重启成功（无代理）")
                        
                        # 再次尝试访问
                        try:
                            page.goto(target_url, timeout=60000, wait_until="domcontentloaded")
                            log.info("✅ Page loaded successfully (without proxy)")
                            try:
                                page.wait_for_load_state("networkidle", timeout=20000)
                            except Exception:
                                pass
                        except Exception as retry_err:
                            log.error(f"❌ Failed to load page even without proxy: {retry_err}")
                            raise
                    else:
                        raise
            try:
                page.bring_to_front()
                log.info("置于顶层：将页面带到前台")
            except Exception as e:
                log.warning(f"置于顶层失败: {e}")
            
            # 等待页面完全加载并稳定
            log.info("⏰ 等待页面完全加载...")
            time.sleep(3)  # 给页面更多时间加载和渲染
            
            # 记录当前页面状态
            try:
                current_url = page.url
                current_title = page.title()
                log.info(f"🌐 当前页面: 标题='{current_title}', URL={current_url}")
            except Exception as e:
                log.warning(f"获取页面信息失败: {e}")
            
            # 获取实际窗口大小并记录
            try:
                viewport_size = page.viewport_size
                if viewport_size:
                    log.info(f"📐 当前视口大小: {viewport_size['width']}x{viewport_size['height']}")
                else:
                    log.info("📐 使用浏览器窗口大小（no_viewport=True）")
                    # 尝试通过JavaScript获取窗口大小
                    try:
                        window_size = page.evaluate('''
                            () => ({
                                width: window.innerWidth,
                                height: window.innerHeight,
                                outerWidth: window.outerWidth,
                                outerHeight: window.outerHeight
                            })
                        ''')
                        log.info(f"📐 浏览器窗口内部尺寸: {window_size['width']}x{window_size['height']}")
                        log.info(f"📐 浏览器窗口外部尺寸: {window_size['outerWidth']}x{window_size['outerHeight']}")
                    except Exception as js_err:
                        log.warning(f"获取窗口尺寸失败: {js_err}")
            except Exception as e:
                log.warning(f"获取视口信息失败: {e}")
            
            # 监听控制台日志
            try:
                page.on("console", lambda msg: log.info(f"浏览器控制台 {msg.type}: {msg.text}"))
            except Exception as e:
                log.warning(f"设置控制台监听失败: {e}")
            
            # 截图保存当前页面状态
            try:
                screenshot_path = runtime_dir / f"page_initial_{int(time.time()*1000)}.png"
                page.screenshot(path=str(screenshot_path), full_page=True)
                log.info(f"📸 初始截图已保存: {screenshot_path}")
            except Exception as e:
                log.warning(f"截图保存失败: {e}")
            
            # 通用安全操作封装
            def element_exists(xpath: str, timeout_ms: int = 10000) -> bool:
                """检查元素是否存在 - 使用轮询机制，默认10秒超时"""
                import time
                start_time = time.time()
                poll_interval = 0.3  # 每300毫秒检查一次
                
                log.info(f"🔍 轮询查找元素 (超时={timeout_ms}ms): {xpath[:80]}...")
                
                while (time.time() - start_time) * 1000 < timeout_ms:
                    try:
                        loc = page.locator(f"xpath={xpath}")
                        # 检查元素是否存在于DOM中
                        count = loc.count()
                        if count > 0:
                            elapsed = int((time.time() - start_time) * 1000)
                            log.info(f"✅ 元素找到！耗时 {elapsed}ms: {xpath[:80]}...")
                            return True
                    except Exception as e:
                        pass  # 继续轮询
                    
                    # 每次轮询显示进度
                    elapsed = int((time.time() - start_time) * 1000)
                    if elapsed % 2000 < poll_interval * 1000:  # 每2秒记录一次
                        log.info(f"⏳ 还在等待... ({elapsed}ms / {timeout_ms}ms)")
                    
                    time.sleep(poll_interval)
                
                # 超时
                elapsed = int((time.time() - start_time) * 1000)
                log.warning(f"⚠️ 元素未找到，超时 {elapsed}ms: {xpath[:80]}...")
                return False
            
            def safe_click(xpath: Optional[str], timeout_ms: int = 10000, required: bool = False) -> bool:
                """必选/可选点击操作"""
                if not xpath:
                    log.warning("未提供XPath，跳过点击")
                    return True
                
                # 先检查元素是否存在（使用轮询机制，默认10秒）
                if not element_exists(xpath, timeout_ms=timeout_ms):
                    if required:
                        log.error(f"❌ 必需元素未找到: {xpath[:80]}...")
                        try:
                            fp = runtime_dir / f"shot_element_not_found_{int(time.time()*1000)}.png"
                            page.screenshot(path=str(fp))
                            log.info(f"📸 截图已保存: {fp}")
                        except Exception:
                            pass
                        return False
                    else:
                        log.info(f"ℹ️ 可选元素未找到，跳过: {xpath[:80]}...")
                        return True
                
                # 元素存在，等待可见并可交互
                try:
                    log.info(f"👆 准备点击: {xpath[:80]}...")
                    loc = page.locator(f"xpath={xpath}")
                    
                    # 等待元素可见
                    log.info(f"⏳ 等待元素可见...")
                    loc.wait_for(state="visible", timeout=timeout_ms)
                    
                    # 滚动到元素位置
                    try:
                        loc.scroll_into_view_if_needed(timeout=3000)
                        log.info(f"✅ 已滚动到元素位置")
                    except Exception as scroll_err:
                        log.warning(f"⚠️ 滚动失败: {scroll_err}")
                    
                    # 尝试正常点击
                    try:
                        loc.click(timeout=5000)
                        log.info(f"✅ 点击成功: {xpath[:80]}...")
                        return True
                    except Exception as click_err:
                        # 如果被遮挡，尝试强制点击
                        if "intercepts pointer events" in str(click_err) or "not clickable" in str(click_err):
                            log.warning(f"⚠️ 元素被遮挡，尝试强制点击...")
                            try:
                                # 使用JavaScript强制点击
                                page.evaluate(f'''
                                    (xpath) => {{
                                        const element = document.evaluate(xpath, document, null, XPathResult.FIRST_ORDERED_NODE_TYPE, null).singleNodeValue;
                                        if (element) {{
                                            element.click();
                                            return true;
                                        }}
                                        return false;
                                    }}
                                ''', xpath)
                                log.info(f"✅ JavaScript强制点击成功: {xpath[:80]}...")
                                return True
                            except Exception as force_err:
                                log.warning(f"⚠️ 强制点击也失败: {force_err}")
                                raise click_err
                        else:
                            raise
                    
                except Exception as e:
                    if required:
                        log.error(f"❌ 必需元素点击失败 {xpath[:80]}...: {e}")
                        try:
                            fp = runtime_dir / f"shot_click_fail_{int(time.time()*1000)}.png"
                            page.screenshot(path=str(fp))
                            log.info(f"📸 截图已保存: {fp}")
                        except Exception:
                            pass
                        return False
                    else:
                        log.warning(f"⚠️ 可选元素点击失败 {xpath[:80]}...: {e}")
                        return True  # 可选元素不存在也返回true

            def safe_fill(xpath: Optional[str], text: str, timeout_ms: int = 10000, required: bool = True) -> bool:
                """必选/可选填写操作"""
                if not xpath:
                    log.warning("未提供XPath，跳过填写")
                    return True if not required else False
                
                # 扩展的元素查找 - 尝试处理XPath不完全匹配的情况
                xpaths_to_try = [xpath]
                
                # 如果是邮箱输入框，添加更丰的匹配
                if 'email' in xpath.lower() or 'Email' in xpath:
                    xpaths_to_try.extend([
                        "//*[contains(@placeholder, 'mail')]",
                        "//input[@type='email']",
                        "//input[contains(@class, 'email')]",
                        "//input[contains(@name, 'email')]",
                    ])
                
                # 正序逐一尝试稍些对松的XPath
                for try_xpath in xpaths_to_try:
                    # 先检查元素是否存在（使用轮询机制，默认10秒）
                    if not element_exists(try_xpath, timeout_ms=timeout_ms):
                        continue  # 继续下一个
                    
                    # 元素存在，等待可见、可编辑并填写
                    try:
                        masked_text = text[:3] + '***' if len(text) > 3 else '***'
                        log.info(f"✏️ 准备填写: {try_xpath[:80]}... (隐藏值: {masked_text})")
                        loc = page.locator(f"xpath={try_xpath}")
                        
                        # 等待元素可见
                        log.info(f"⏳ 等待输入框可见...")
                        loc.wait_for(state="visible", timeout=timeout_ms)
                        
                        # 滚动到元素位置
                        try:
                            loc.scroll_into_view_if_needed(timeout=3000)
                            log.info(f"✅ 输入框已滚动到视图内")
                        except Exception as scroll_err:
                            log.warning(f"⚠️ 滚动失败: {scroll_err}")
                        
                        # 点击聚焦后填写
                        try:
                            loc.click(timeout=3000)  # 先点击聚焦
                            log.info(f"✅ 输入框已聚焦")
                        except Exception:
                            pass  # 点击失败不影响填写
                        
                        # 清空后填写
                        loc.fill(text, timeout=5000)
                        log.info(f"✅ 填写成功: {try_xpath[:80]}...")
                        
                        # 验证填写是否成功
                        try:
                            filled_value = loc.input_value(timeout=2000)
                            if filled_value == text:
                                log.info(f"✅ 验证成功: 输入值匹配")
                            else:
                                log.warning(f"⚠️ 输入值不匹配: 预期长度 {len(text)}, 实际长度 {len(filled_value)}")
                        except Exception as verify_err:
                            log.warning(f"⚠️ 验证输入值失败: {verify_err}")
                        
                        return True
                    except Exception as e:
                        log.warning(f"⚠️ XPath '{try_xpath[:60]}' 填写失败: {e}")
                        continue  # 继续下一个
                
                # 所有XPath都失败
                if required:
                    log.error(f"❌ 必需输入框未找到: {xpath[:80]}...")
                    try:
                        fp = runtime_dir / f"shot_input_not_found_{int(time.time()*1000)}.png"
                        page.screenshot(path=str(fp), full_page=True)
                        log.info(f"📸 截图已保存: {fp}")
                    except Exception:
                        pass
                    return False
                else:
                    log.info(f"ℹ️ 可选输入框未找到，跳过: {xpath[:80]}...")
                    return True

            # ... existing code ...

            # 步骤1: 关闭弹窗（如存在）
            log.info("\n" + "="*60)
            log.info("Step 1: Closing popup (if exists)")
            log.info("="*60)
            
            close_popup = xpaths.get("close_popup")
            if close_popup and element_exists(close_popup, timeout_ms=2000):
                log.info(f"🔍 找到弹窗关闭按钮，尝试关闭...")
                safe_click(close_popup, timeout_ms=5000, required=False)
                time.sleep(2)  # 等待弹窗关闭动画完成
            else:
                log.info("ℹ️ 没有检测到弹窗")
            
            # 初始化变量
            login_entry_found = False
            
            # 步骤2: 点击Sign In按钮

            # 初始点击路径 - 可选
            log.info("\n" + "="*60)
            log.info("步骤2: 点击 Sign In 按钮（如果存在）")
            log.info("="*60)
            signin_btn = xpaths.get("signin_btn")
            if signin_btn and not login_entry_found:
                # 等待一下确保弹窗关闭完成
                time.sleep(2)
                if safe_click(signin_btn, timeout_ms=10000, required=False):
                    log.info("✅ Sign In 按钮已点击，等待响应...")
                    time.sleep(3)  # 等待页面响应
                    
                    # 确认点击是否生效（截图验证）
                    try:
                        screenshot_after_signin = runtime_dir / f"after_signin_{int(time.time()*1000)}.png"
                        page.screenshot(path=str(screenshot_after_signin), full_page=True)
                        log.info(f"📸 Sign In后截图: {screenshot_after_signin}")
                    except Exception:
                        pass
            elif login_entry_found:
                log.info("ℹ️ 已通过其他方式进入登录流程，跳过 Sign In 按钮")
            else:
                log.warning("⚠️ XPath配置中未定义 signin_btn")
            
            log.info("\n" + "="*60)
            log.info("步骤3: 选择邮箱登录方式 (signin_with_email)")
            log.info("="*60)
            # 按照kling_xpaths.json配置顺序，第3步应该是signin_with_email
            signin_with_email = xpaths.get("signin_with_email")
            email_login_clicked = False
            if signin_with_email:
                time.sleep(2)
                if safe_click(signin_with_email, timeout_ms=10000, required=False):
                    log.info("✅ 邮箱登录选项已点击，等待表单加载...")
                    time.sleep(5)  # 增加等待时间到5秒，确保表单完全渲染
                    email_login_clicked = True
                    
                    # 滚动页面确保表单在视口内
                    try:
                        page.evaluate("window.scrollTo(0, 300)")
                        log.info("✅ 页面已滚动，确保表单可见")
                        time.sleep(1)
                    except Exception as scroll_err:
                        log.warning(f"⚠️ 滚动失败: {scroll_err}")
                    
                    # 确认点击是否生效
                    try:
                        screenshot_after_email = runtime_dir / f"after_email_option_{int(time.time()*1000)}.png"
                        page.screenshot(path=str(screenshot_after_email), full_page=True)
                        log.info(f"📸 邮箱选项后截图: {screenshot_after_email}")
                    except Exception:
                        pass
                else:
                    log.warning("⚠️ 邮箱登录选项未找到或点击失败")
            else:
                log.warning("⚠️ XPath配置中未定义邮箱登录选项")
            
            log.info("\n" + "="*60)
            log.info("步骤4: 点击注册链接 (Sign up for free)")
            log.info("="*60)
            # 按照kling_xpaths.json配置顺序，第4步应该是Sign up for free
            signup_link = xpaths.get("Sign up for free")
            signup_clicked = False
            
            if signup_link:
                time.sleep(2)
                # 尝试点击注册链接
                if safe_click(signup_link, timeout_ms=15000, required=False):
                    log.info("✅ 注册链接点击命令执行成功")
                    time.sleep(3)  # 等待3秒
                    
                    # 验证点击是否生效：检查是否出现注册表单
                    log.info("🔍 验证是否出现邮箱输入表单...")
                    
                    # 检查是否有邮箱输入框
                    email_input_xpath = xpaths.get("Enter Email Address")
                    if email_input_xpath and element_exists(email_input_xpath, timeout_ms=5000):
                        log.info("✅ 邮箱输入表单已出现！（检测到邮箱输入框）")
                        signup_clicked = True
                    else:
                        log.warning("⚠️ 邮箱输入表单未出现")
                    
                    # 等待额外时间让表单完全渲染
                    time.sleep(2)
                    
                    # 滚动页面到顶部，确保表单在视口内
                    try:
                        page.evaluate("window.scrollTo(0, 0)")
                        log.info("✅ 页面已滚动到顶部")
                        time.sleep(1)
                    except Exception as scroll_err:
                        log.warning(f"⚠️ 滚动失败: {scroll_err}")
                    
                    # 确认点击是否生效
                    try:
                        screenshot_after_signup = runtime_dir / f"after_signup_{int(time.time()*1000)}.png"
                        page.screenshot(path=str(screenshot_after_signup), full_page=True)
                        log.info(f"📸 注册后截图: {screenshot_after_signup}")
                    except Exception:
                        pass
                else:
                    log.warning("⚠️ 注册链接未找到或点击失败")
            else:
                log.warning("⚠️ XPath配置中未定义注册链接")
            
            # 如果步骤3和4都未能顺利进行，记录警告但继续流程
            if not email_login_clicked and not signup_clicked:
                log.warning("⚠️ 邮箱登录和注册流程均未成功进行，将尝试继续...")

            # 填入邮箱与密码
            log.info("\n" + "="*60)
            log.info("步骤5: 填写邮箱和密码")
            log.info("="*60)
            
            # 修复：使用正确的键名匹配XPath配置文件
            email_input = xpaths.get("Enter Email Address")  # 注意：键名带空格
            log.info(f"🔍 开始填写邮箱 (XPath: {email_input[:60]}...)")
            if email_input and safe_fill(email_input, email, timeout_ms=15000, required=True):  # 增加超时到15秒
                time.sleep(1)
            else:
                log.error("❌ 邮箱输入框填写失败，无法继续")
                return False
            
            password_input = xpaths.get("password_input")
            if password_input and safe_fill(password_input, password, timeout_ms=15000, required=True):
                time.sleep(1)
            else:
                log.error("❌ 密码输入框填写失败，无法继续")
                return False
            
            # Confirm Password 也需要使用正确的键名
            confirm_input = xpaths.get("Confirm Password")  # 注意：键名带空格
            if confirm_input:
                if safe_fill(confirm_input, password, timeout_ms=15000, required=False):
                    time.sleep(1)
            else:
                log.info("ℹ️ 无确认密码字段，跳过")

            log.info("\n" + "="*60)
            log.info("Step 6: Clicking Next button")
            log.info("="*60)
            next_btn = xpaths.get("next_btn")
            if next_btn:
                if safe_click(next_btn, timeout_ms=10000, required=True):
                    log.info("✅ Next button clicked, waiting for next step...")
                    time.sleep(3)  # 等待页面加载滑块验证或验证码输入
                else:
                    log.error("❌ Failed to click Next button, cannot continue")
                    return False
            else:
                log.error("❌ No next_btn XPath defined, cannot continue")
                return False
            
            # 处理滑块验证（如果有）
            log.info("\n" + "="*60)
            log.info("Step 7: Solving slider CAPTCHA (if exists)")
            log.info("="*60)
            
            slider_iframe_xpath = xpaths.get("slider_iframe")
            slider_xpath = xpaths.get("slider_handle")
            slider_container_xpath = xpaths.get("slider_container")
            
            slider_solved = False  # 标记滑块是否解决
            
            if slider_xpath:
                log.info("🎯 检测到滑块配置，尝试解决...")
                
                # 如果滑块在iframe中，先切换到iframe
                if slider_iframe_xpath and element_exists(slider_iframe_xpath, timeout_ms=10000):
                    try:
                        log.info(f"🔍 检测到iframe: {slider_iframe_xpath[:60]}")
                        
                        # 等待iframe加载（使用Locator）
                        iframe_locator = page.locator(f"xpath={slider_iframe_xpath}").first
                        iframe_locator.wait_for(state="attached", timeout=15000)
                        log.info("✅ iframe元素已加载")
                        
                        # 🔴 关键修改：使用原生 Frame API 而不是 frame_locator
                        # 等待iframe内容加载
                        log.info("⏳ 等待iframe内容初始化...")
                        time.sleep(3)  # 给iframe一些时间来设置URL
                        
                        # 获取所有 frame 对象
                        all_frames = page.frames
                        log.info(f"📋 当前页面总共有 {len(all_frames)} 个 frame")
                        
                        # 查找包含 'captcha' 的 iframe（通过URL或name）
                        slider_frame = None
                        
                        # 方法1: 通过 frame.url 查找
                        for frame in all_frames:
                            frame_url = frame.url
                            if frame_url and 'captcha' in frame_url.lower():
                                slider_frame = frame
                                log.info(f"✅ 找到滑块iframe (通过URL): {frame_url[:80]}")
                                break
                        
                        # 方法2: 如果通过URL找不到，尝试通过iframe元素的src属性
                        if not slider_frame:
                            log.info("🔍 通过URL未找到，尝试通过元素属性查找...")
                            try:
                                # 获取iframe元素的src属性
                                iframe_src = iframe_locator.get_attribute('src', timeout=5000)
                                log.info(f"📝 iframe src属性: {iframe_src[:100] if iframe_src else 'None'}")
                                
                                # 再次获取frames（可能已经加载完成）
                                time.sleep(2)
                                all_frames = page.frames
                                log.info(f"📋 重新获取，当前页面总共有 {len(all_frames)} 个 frame")
                                
                                # 尝试通过URL匹配或者索引匹配
                                for idx, frame in enumerate(all_frames):
                                    frame_url = frame.url
                                    log.info(f"  Frame {idx}: URL='{frame_url[:100] if frame_url else '(empty)'}'")
                                    
                                    # 如果URL包含captcha
                                    if frame_url and 'captcha' in frame_url.lower():
                                        slider_frame = frame
                                        log.info(f"✅ 找到滑块iframe (延迟加载): Frame {idx}")
                                        break
                                    
                                    # 如果URL为空但src属性包含captcha，使用最后一个非主页面的frame
                                    if not frame_url and idx > 0:  # 跳过主frame
                                        # 这可能是还在加载的captcha iframe
                                        slider_frame = frame
                                        log.info(f"⚠️ 使用URL为空的Frame {idx} (可能是captcha iframe)")
                                        # 不break，继续查找更确定的
                                        
                            except Exception as attr_err:
                                log.warning(f"⚠️ 获取iframe属性失败: {attr_err}")
                        
                        if not slider_frame:
                            log.error("❌ 未找到captcha iframe")
                            log.info("📋 最终所有 frame URLs:")
                            for idx, frame in enumerate(all_frames):
                                log.info(f"  Frame {idx}: {frame.url[:100] if frame.url else '(empty)'}")
                            raise Exception("Captcha iframe not found")
                        
                        # 等待iframe内容加载
                        log.info("⏳ 等待iframe内容完全加载...")
                        try:
                            slider_frame.wait_for_load_state("domcontentloaded", timeout=15000)
                            log.info("✅ iframe DOM 已加载")
                        except Exception as load_err:
                            log.warning(f"⚠️ iframe load_state 超时，继续尝试: {load_err}")
                        
                        time.sleep(3)  # 额外等待让 JavaScript 执行完
                        
                        # 尝试多个可能的滑块 XPath 和 CSS 选择器
                        slider_selectors = [
                            {"type": "xpath", "value": slider_xpath, "desc": "配置的 XPath"},
                            {"type": "xpath", "value": "//i[@class='btn-icon']", "desc": "i 标签 + class"},
                            {"type": "xpath", "value": "//*[contains(@class, 'btn-icon')]", "desc": "含有 btn-icon class"},
                            {"type": "xpath", "value": "//div[@class='slider-btn']/i", "desc": "通过父元素"},
                            {"type": "xpath", "value": "//div[contains(@class, 'slider-btn')]//i", "desc": "模糊父元素"},
                            {"type": "css", "value": ".btn-icon", "desc": "CSS class"},
                            {"type": "css", "value": "i.btn-icon", "desc": "CSS i.btn-icon"},
                            {"type": "css", "value": ".slider-btn i", "desc": "CSS 父元素"},
                        ]
                        
                        slider_found = False
                        for selector in slider_selectors:
                            try:
                                sel_type = selector["type"]
                                sel_value = selector["value"]
                                sel_desc = selector["desc"]
                                
                                log.info(f"🔍 尝试 {sel_type.upper()}: {sel_value} ({sel_desc})")
                                
                                # 使用 frame 的 locator 方法
                                if sel_type == "xpath":
                                    slider_in_iframe = slider_frame.locator(f"xpath={sel_value}").first
                                else:  # css
                                    slider_in_iframe = slider_frame.locator(sel_value).first
                                
                                # 等待元素可见
                                slider_in_iframe.wait_for(state="visible", timeout=8000)
                                log.info(f"✅ 使用 {sel_type.upper()} 找到滑块: {sel_value}")
                                slider_found = True
                                
                                # 获取滑块位置
                                box = slider_in_iframe.bounding_box()
                                if box:
                                    log.info(f"📍 滑块位置: x={box['x']:.0f}, y={box['y']:.0f}, width={box['width']:.0f}, height={box['height']:.0f}")
                                    
                                    # 计算拖动距离（默认300px）
                                    distance = 300
                                    
                                    # 尝试根据容器计算距离
                                    try:
                                        container_in_iframe = slider_frame.locator(f"xpath={slider_container_xpath}").first
                                        container_box = container_in_iframe.bounding_box(timeout=3000)
                                        if container_box:
                                            distance = int(container_box["width"] - box["width"] - 20)
                                            log.info(f"📏 根据容器计算拖动距离: {distance}px")
                                    except Exception as calc_err:
                                        log.warning(f"⚠️ 无法计算距离，使用默认值300px: {calc_err}")
                                    
                                    # 执行拖动
                                    start_x = box["x"] + box["width"] / 2
                                    start_y = box["y"] + box["height"] / 2
                                    end_x = start_x + distance
                                    
                                    log.info(f"👉 开始拖动: ({start_x:.0f}, {start_y:.0f}) -> ({end_x:.0f}, {start_y:.0f}) [距离: {distance}px]")
                                    
                                    # 生成拟人轨迹
                                    track = _human_drag_track(distance)
                                    steps = track["steps"]
                                    
                                    # 使用主页面的mouse，因为坐标是相对于整个页面的
                                    page.mouse.move(start_x, start_y)
                                    time.sleep(random.uniform(0.2, 0.4))
                                    page.mouse.down()
                                    time.sleep(random.uniform(0.1, 0.2))
                                    
                                    current_x = start_x
                                    for step in steps:
                                        current_x += step
                                        jitter_y = start_y + random.randint(-2, 2)
                                        page.mouse.move(current_x, jitter_y)
                                        time.sleep(random.uniform(0.015, 0.035))
                                    
                                    time.sleep(random.uniform(0.2, 0.3))
                                    page.mouse.up()
                                    
                                    log.info("✅ 滑块拖动完成")
                                    time.sleep(5)  # 等待验证结果
                                    
                                    # 验证是否成功：检查验证码输入框是否出现
                                    code_input_xpath = xpaths.get("code_url_element")
                                    if code_input_xpath and element_exists(code_input_xpath, timeout_ms=5000):
                                        log.info("✅✅ 滑块验证成功！验证码输入框已出现")
                                        slider_solved = True
                                    else:
                                        log.warning("⚠️ 滑块拖动完成，但验证码输入框未出现")
                                        log.info("🔄 尝试重新拖动...")
                                        # 不设置 slider_solved = True，继续尝试下一个选择器
                                        continue
                                    
                                    break  # 找到滑块并验证成功后跳出循环
                                else:
                                    log.error("❌ 无法获取滑块位置")
                                    
                            except Exception as slider_err:
                                log.warning(f"⚠️ {selector['type'].upper()} '{selector['value']}' 查找失败: {slider_err}")
                                continue
                        
                        if not slider_found:
                            log.error("❌ 所有选择器都失败了")
                            # 保存调试截图
                            try:
                                debug_shot = runtime_dir / f"slider_not_found_{int(time.time()*1000)}.png"
                                page.screenshot(path=str(debug_shot))
                                log.info(f"📸 调试截图已保存: {debug_shot}")
                            except Exception:
                                pass
                            
                    except Exception as iframe_err:
                        log.error(f"❌ iframe处理失败: {iframe_err}")
                        import traceback
                        log.error(traceback.format_exc())
                else:
                    # 滑块不在iframe中，直接操作
                    log.info("🔍 滑块不在iframe中，直接操作...")
                    slider_success = _perform_human_drag(
                        page, 
                        slider_xpath, 
                        slider_container_xpath
                    )
                    if slider_success:
                        log.info("✅ 滑块验证成功")
                        slider_solved = True
                    else:
                        log.warning("⚠️ 滑块验证失败")
            else:
                log.info("ℹ️ 未配置滑块XPath，跳过")
                slider_solved = True  # 没有滑块配置，认为不需要验证
            
            # 🔴 关键：如果滑块没有解决，必须停止流程
            if not slider_solved:
                log.error("❌❌ 滑块验证失败，无法继续注册流程（因为邮箱收不到验证码）")
                log.error("💡 建议：检查滑块 XPath 配置，或手动完成滑块验证后重试")
                raise Exception("Slider CAPTCHA verification failed - cannot proceed without it")
            
            # 验证码阶段：集成邮件接码功能
            # code_input: 接码页面中验证码元素的XPath（用于提取验证码）
            # code_url_element: Kling AI页面中验证码输入框的XPath（用于填写验证码）
            code_extract_xpath = xpaths.get("code_input")  # 从接码页提取
            code_input_xpath = xpaths.get("code_url_element")  # 在Kling AI页填写
            
            log.info("\n" + "="*60)
            log.info("Step 8: Processing verification code")
            log.info("="*60)
            
            if code_extract_xpath and code_input_xpath and code_url:
                log.info(f"📧 Processing verification code from: {code_url}")
                
                # 等待电子邮件到达（给服务器一些时间）
                log.info("⏳ Waiting 10 seconds for email to arrive...")
                time.sleep(10)
                
                # 打开新标签页访问接码地址
                log.info("🌐 Opening new tab for verification code page...")
                code_page = context.new_page()
                
                try:
                    log.info(f"🔗 Navigating to code URL: {code_url}")
                    code_page.goto(code_url, timeout=60000, wait_until="domcontentloaded")
                    
                    # 等待页面加载
                    try:
                        code_page.wait_for_load_state("networkidle", timeout=20000)
                        log.info("✅ Code page fully loaded")
                    except Exception:
                        log.warning("⚠️ Network idle timeout, but continuing...")
                        time.sleep(3)  # 等待一下让页面稳定
                    
                    # 保存接码页面截图
                    try:
                        code_screenshot = runtime_dir / f"code_page_{int(time.time()*1000)}.png"
                        code_page.screenshot(path=str(code_screenshot))
                        log.info(f"📸 Code page screenshot saved: {code_screenshot}")
                    except Exception as ss_err:
                        log.warning(f"⚠️ Failed to save code page screenshot: {ss_err}")
                    
                    # 提取验证码
                    verification_code = None
                    log.info(f"🔍 Extracting verification code using XPath: {code_extract_xpath[:80]}...")
                    
                    try:
                        # 尝试多次提取验证码
                        for attempt in range(3):
                            log.info(f"🔍 Attempt {attempt + 1}/3: Looking for verification code...")
                            
                            try:
                                # 检查元素是否存在
                                code_loc = code_page.locator(f"xpath={code_extract_xpath}")
                                code_loc.wait_for(state="attached", timeout=10000)
                                
                                # 提取文本
                                code_text = code_loc.inner_text(timeout=5000)
                                log.info(f"📝 Extracted text from element: '{code_text}'")
                                
                                # 从文本中提取6位数字
                                import re
                                match = re.search(r'\b\d{6}\b', code_text)
                                if match:
                                    verification_code = match.group(0)
                                    log.info(f"✅ Verification code extracted: {verification_code}")
                                    break
                                else:
                                    log.warning(f"⚠️ No 6-digit code found in text: '{code_text}'")
                                    # 尝试直接使用文本（去除空格）
                                    clean_text = code_text.strip().replace(' ', '').replace('\n', '')
                                    if clean_text.isdigit() and len(clean_text) == 6:
                                        verification_code = clean_text
                                        log.info(f"✅ Verification code extracted (cleaned): {verification_code}")
                                        break
                                    
                            except Exception as extract_err:
                                log.warning(f"⚠️ Attempt {attempt + 1} failed: {extract_err}")
                                if attempt < 2:
                                    log.info("⏳ Waiting 5 seconds before retry...")
                                    time.sleep(5)
                        
                        # 如果仍未提取到，尝试从整个页面提取
                        if not verification_code:
                            log.warning("⚠️ XPath extraction failed, trying to extract from page body...")
                            try:
                                page_text = code_page.inner_text("body", timeout=5000)
                                match = re.search(r'\b\d{6}\b', page_text)
                                if match:
                                    verification_code = match.group(0)
                                    log.info(f"✅ Verification code extracted from page body: {verification_code}")
                                else:
                                    log.error("❌ No 6-digit verification code found in page body")
                            except Exception as body_err:
                                log.error(f"❌ Failed to extract from page body: {body_err}")
                    
                    except Exception as extract_err:
                        log.error(f"❌ Error extracting verification code: {extract_err}")
                        import traceback
                        log.error(traceback.format_exc())
                    
                    # 关闭接码页面，切换回注册页面
                    log.info("🔙 Closing code page and switching back to registration page...")
                    code_page.close()
                    page.bring_to_front()
                    log.info("✅ Switched back to registration page")
                    
                    # 等待页面切换
                    time.sleep(2)
                    
                    # 填入验证码
                    if verification_code:
                        log.info(f"✏️ Filling verification code: {verification_code}")
                        log.info(f"🎯 Target input XPath: {code_input_xpath[:80]}...")
                        
                        fill_success = safe_fill(code_input_xpath, verification_code, timeout_ms=10000, required=True)
                        
                        if fill_success:
                            log.info("✅ Verification code filled successfully")
                            
                            # 等待一下让系统处理
                            time.sleep(2)
                            
                            # 点击提交按钮
                            final_submit_btn = xpaths.get("final_submit_btn")
                            if final_submit_btn:
                                log.info(f"👆 Clicking final submit button: {final_submit_btn[:80]}...")
                                submit_success = safe_click(final_submit_btn, timeout_ms=10000, required=True)
                                
                                if submit_success:
                                    log.info("✅ Final submit button clicked successfully")
                                    # 等待注册完成
                                    log.info("⏳ Waiting for registration to complete...")
                                    time.sleep(5)
                                else:
                                    log.error("❌ Failed to click final submit button")
                                    return False
                            else:
                                log.error("❌ No final_submit_btn XPath specified")
                                return False
                        else:
                            log.error("❌ Failed to fill verification code")
                            return False
                    else:
                        log.error("❌ Failed to extract verification code")
                        return False
                        
                except Exception as e:
                    log.error(f"❌ Error processing verification code: {e}")
                    import traceback
                    log.error(traceback.format_exc())
                    try:
                        code_page.close()
                    except Exception:
                        pass
                    return False
            elif code_input_xpath:
                # 如果没有code_url，但有code_input，则等待用户手动输入
                log.info("⚠️ No code_url provided, waiting for manual input")
                final_submit_btn = xpaths.get("final_submit_btn")
                if final_submit_btn:
                    # 等待30秒让用户手动输入
                    log.info("⏳ Waiting 30 seconds for manual code input...")
                    log.info("👉 Please manually input verification code in the browser")
                    time.sleep(30)
            else:
                log.warning("⚠️ No verification code XPath configured, skipping verification")
            
            try:
                fp = runtime_dir / f"shot_done_{int(time.time()*1000)}.png"
                page.screenshot(path=str(fp))
                log.info(f"🎉 Registration completed! Final screenshot saved: {fp}")
            except Exception:
                pass
            
            # 不立即关闭浏览器，给用户时间查看结果
            log.info("⏸️ Keeping browser open for 30 seconds to review results...")
            log.info("🔍 You can manually close the browser or wait for auto-close")
            time.sleep(30)  # 等待30秒让用户查看结果
            
            # Playwright模式：温和关闭浏览器
            if browser_mode == "playwright":
                try:
                    log.info("🔒 Closing browser gracefully...")
                    if page:
                        page.close()
                    if context:
                        context.close()
                    if browser:
                        browser.close()
                    log.info("✅ Browser closed successfully")
                except Exception as close_err:
                    log.warning(f"Browser close error (can be ignored): {close_err}")
            else:
                # 比特浏览器模式：不关闭浏览器，由用户手动关闭
                log.info("👁️ BitBrowser mode: browser will remain open")
            
        return True
    except Exception as e:
        log.error(f"❌ Automation error: {e}")
        import traceback
        log.error(traceback.format_exc())
        
        # 尝试保存错误截图（检查浏览器和page是否还存在）
        try:
            # 检查page对象是否还有效
            if 'page' in locals() and page is not None:
                # 检查page是否还未关闭
                try:
                    # 尝试获取当前URL来验证page是否有效
                    _ = page.url
                    fp = runtime_dir / f"shot_error_{int(time.time()*1000)}.png"
                    fp.parent.mkdir(parents=True, exist_ok=True)
                    page.screenshot(path=str(fp))
                    log.info(f"📸 Error screenshot saved: {fp}")
                except Exception as page_err:
                    log.warning(f"⚠️ Page is no longer accessible for screenshot: {page_err}")
            else:
                log.warning("⚠️ No page object available for error screenshot")
        except Exception as screenshot_err:
            log.warning(f"⚠️ Failed to save error screenshot: {screenshot_err}")
        
        # 即使出错也要给用户时间查看浏览器状态
        log.info("⏸️ Error occurred. Keeping browser open for 30 seconds for debugging...")
        time.sleep(30)
        
        # 温和关闭浏览器
        if browser_mode == "playwright":
            try:
                if 'browser' in locals() and browser is not None:
                    log.info("🔒 Closing browser after error...")
                    browser.close()
                    log.info("✅ Browser closed")
            except Exception as close_err:
                log.warning(f"⚠️ Browser close error (can be ignored): {close_err}")
        
        return False