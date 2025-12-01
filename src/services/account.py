from pathlib import Path
import csv
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List, Tuple, Optional, Dict, Any
from ..utils.logger import get_logger
from ..integrations.bitbrowser import BitBrowserClient
from .automation import run_registration_flow


def update_csv_status(csv_path: Path, email: str, status: str) -> bool:
    """
    更新CSV文件中指定邮箱的注册状态（第9列）
    
    参数：
        csv_path: CSV文件路径
        email: 邮箱地址
        status: 状态值（"成功" 或 "失败"）
    
    返回：
        更新成功返回True，否则返回False
    """
    log = get_logger(__name__)
    
    try:
        # 读取所有行
        rows = []
        with csv_path.open("r", encoding="utf-8-sig", newline='') as f:
            reader = csv.reader(f)
            rows = list(reader)
        
        if not rows:
            log.error("CSV文件为空")
            return False
        
        # 确定是否有标题行
        has_header = rows[0] and "email" in rows[0][0].lower()
        start_row = 1 if has_header else 0
        
        # 查找并更新对应行
        updated = False
        for i in range(start_row, len(rows)):
            row = rows[i]
            if len(row) >= 1 and row[0].strip() == email:
                # 扩展行到至少9列
                while len(row) < 9:
                    row.append("")
                # 更新第9列（索引8）
                row[8] = status
                rows[i] = row
                updated = True
                log.info(f"✅ 已更新 {email} 的状态为: {status}")
                break
        
        if not updated:
            log.warning(f"⚠️ 未找到邮箱 {email} 对应的行")
            return False
        
        # 写回文件
        with csv_path.open("w", encoding="utf-8-sig", newline='') as f:
            writer = csv.writer(f)
            writer.writerows(rows)
        
        log.info(f"✅ CSV文件已更新: {csv_path}")
        return True
        
    except Exception as e:
        log.error(f"❌ 更新CSV状态失败: {e}")
        import traceback
        log.error(traceback.format_exc())
        return False


def load_accounts_csv(csv_path: Path) -> List[Dict[str, Any]]:
    # 加载账号与代理（可选）列表
    # CSV格式：邮箱账号、邮箱密码、邮箱验证码接码地址、代理ip、代理端口、代理用户名、代理密码
    rows: List[Dict[str, Any]] = []
    with csv_path.open("r", encoding="utf-8-sig") as f:  # utf-8-sig自动处理BOM
        reader = csv.reader(f)
        for i, row in enumerate(reader):
            # 跳过标题行（检查第一列是否包含'email'字样）
            if i == 0 and row and "email" in row[0].lower():
                continue
            if len(row) >= 2:
                rec: Dict[str, Any] = {
                    "email": row[0].strip(),
                    "password": row[1].strip(),
                }
                # 第3列：邮箱验证码接码地址
                if len(row) >= 3 and row[2].strip():
                    rec["code_url"] = row[2].strip()
                # 第4-7列：代理信息（ip, port, username, password）
                if len(row) >= 5 and row[3].strip():
                    rec["host"] = row[3].strip()
                    port_str = str(row[4]).strip()
                    # 确保端口是数字
                    if port_str and port_str.isdigit():
                        rec["port"] = int(port_str)
                    else:
                        rec["port"] = None
                if len(row) >= 7:
                    rec["proxyUserName"] = row[5].strip() if row[5].strip() else None
                    rec["proxyPassword"] = row[6].strip() if row[6].strip() else None
                rows.append(rec)
    return rows


def mock_register(email: str, password: str) -> bool:
    # 示例：模拟注册动作，真实项目中接入目标站点的注册逻辑
    time.sleep(0.05)
    return ("@" in email) and (len(password) >= 6)


def _wait_and_switch_to_new_tab(
    client: "BitBrowserClient",
    window_id: str,
    target_url: str,
    max_retries: int = 10,
    retry_interval: float = 2.0,
    log = None
) -> bool:
    """
    等待新标签页创建完成并切换到包含目标URL的标签页
    
    参数：
        client: 比特浏览器客户端
        window_id: 窗口ID
        target_url: 目标URL（用于匹配标签页）
        max_retries: 最大重试次数
        retry_interval: 每次重试的间隔时间（秒）
        log: 日志对象
    
    返回：
        成功切换返回True，否则返回False
    """
    import re
    
    if log is None:
        log = get_logger(__name__)
    
    # 提取目标URL的域名部分用于匹配
    target_domain = re.sub(r'https?://(www\.)?', '', target_url).split('/')[0]
    log.info(f"Looking for tab with domain: {target_domain}")
    
    workspace_tab_id = None  # 保存工作台标签页ID
    
    for attempt in range(max_retries):
        try:
            log.info(f"Attempt {attempt + 1}/{max_retries} to find and switch to new tab")
            
            # 获取当前窗口的所有标签页
            tabs_response = client.get_window_tabs(window_id)
            
            if not tabs_response.get("success"):
                log.warning(f"Failed to get tabs: {tabs_response.get('msg')}")
                time.sleep(retry_interval)
                continue
            
            tabs_data = tabs_response.get("data", {})
            tabs = tabs_data.get("tabs", [])
            
            log.info(f"Found {len(tabs)} tabs in window")
            
            # 打印所有标签页的详细信息
            for i, tab in enumerate(tabs):
                tab_url = tab.get("url", "")
                tab_id = tab.get("id", "")
                tab_title = tab.get("title", "")
                is_active = tab.get("active", False)
                log.info(f"Tab {i}: ID={tab_id}, Title='{tab_title}', URL={tab_url}, Active={is_active}")
                
                # 记录工作台标签页
                if "工作台" in tab_title or "console.bitbrowser" in tab_url:
                    workspace_tab_id = tab_id
                    log.info(f"Found workspace tab: ID={tab_id}")
            
            # 查找包含目标域名的标签页
            target_tab = None
            for tab in tabs:
                tab_url = tab.get("url", "")
                tab_title = tab.get("title", "")
                
                # 检查URL或标题是否包含目标域名/关键词
                if (target_domain in tab_url or 
                    "klingai" in tab_url.lower() or 
                    "kling" in tab_title.lower()):
                    target_tab = tab
                    log.info(f"Found matching tab: Title='{tab_title}', URL={tab_url}")
                    break
            
            if target_tab:
                tab_id = target_tab.get("id")
                if tab_id:
                    # 切换到目标标签页
                    log.info(f"Switching to tab: {tab_id}")
                    switch_result = client.switch_tab(window_id, tab_id)
                    log.info(f"Switch tab result: {switch_result}")
                    
                    # 再次等待确保切换完成
                    time.sleep(1)
                    
                    # 激活窗口确保用户可见
                    try:
                        client.activate(window_id)
                        log.info("Window activated")
                    except Exception as e:
                        log.warning(f"Failed to activate window: {e}")
                    
                    log.info(f"Successfully switched to target tab!")
                    return True
            else:
                log.warning(f"Target tab not found yet, waiting...")
                time.sleep(retry_interval)
                
        except Exception as e:
            log.error(f"Error in attempt {attempt + 1}: {e}")
            time.sleep(retry_interval)
    
    # 如果所有重试失败，尝试关闭工作台标签页
    if workspace_tab_id:
        try:
            log.info(f"Failed to switch tab after {max_retries} attempts")
            log.info(f"Trying fallback: closing workspace tab (ID={workspace_tab_id})...")
            
            close_result = client.close_tab(window_id, workspace_tab_id)
            log.info(f"Close workspace tab result: {close_result}")
            
            # 等待标签页关闭
            time.sleep(2)
            
            # 激活窗口，Kling AI标签应该自动显示
            try:
                client.activate(window_id)
                log.info("Window activated after closing workspace tab")
            except Exception as e:
                log.warning(f"Failed to activate window: {e}")
            
            log.info("Workspace tab closed, Kling AI tab should now be visible")
            return True
            
        except Exception as e:
            log.error(f"Failed to close workspace tab: {e}")
    
    log.error(f"Failed to switch to new tab after all attempts")
    return False


def register_accounts_batch(
    csv_path: Path,
    runtime_dir: Path,
    concurrency: int = 3,
    interval_ms: int = 300,
    bitbrowser_base_url: Optional[str] = None,
    platform_url: Optional[str] = None,
    group_id: Optional[str] = None,
    auto_xpaths: Optional[Dict[str, str]] = None,
    dry_run: bool = False,  # 默认改为False，启用真实自动化
    browser_mode: str = "bitbrowser",  # 浏览器模式: bitbrowser 或 playwright
) -> str:
    log = get_logger(__name__)
    rows = load_accounts_csv(csv_path)

    # Playwright模式：直接执行自动化，不需要比特浏览器客户端
    if browser_mode == "playwright":
        log.info(f"🎭 Playwright模式 - 将使用本地浏览器 + 随机指纹")
        ok, fail = 0, 0
        outputs: List[str] = []
        
        log.info(f"Starting batch registration for {len(rows)} accounts")
        
        for idx, rec in enumerate(rows, 1):
            email = rec.get("email")
            password = rec.get("password")
            code_url = rec.get("code_url")
            host = rec.get("host")
            port = rec.get("port")
            puser = rec.get("proxyUserName")
            ppass = rec.get("proxyPassword")
            
            log.info(f"\n{'='*60}")
            log.info(f"Processing account {idx}/{len(rows)}: {email}")
            log.info(f"{'='*60}")
            
            try:
                # 直接调用自动化流程，不需要比特浏览器
                auto_ok = run_registration_flow(
                    email=email,
                    password=password,
                    runtime_dir=runtime_dir,
                    xpaths=auto_xpaths or {},
                    proxy={
                        "host": host,
                        "port": port,
                        "username": puser,
                        "password": ppass,
                    },
                    platform_url=platform_url or "https://klingai.com",
                    code_url=code_url,
                    attach_ws=None,  # Playwright模式不需要WebSocket
                    dry_run=dry_run,
                    browser_mode="playwright",
                )
                
                if auto_ok:
                    ok += 1
                    success_msg = f"SUCCESS {idx}/{len(rows)}: {email}"
                    outputs.append(success_msg)
                    log.info(f"✅ {success_msg}")
                    
                    # 更新CSV状态为"成功"
                    update_csv_status(csv_path, email, "成功")
                else:
                    fail += 1
                    fail_msg = f"FAIL {idx}/{len(rows)}: {email} - automation failed"
                    outputs.append(fail_msg)
                    log.error(f"❌ {fail_msg}")
                    
                    # 更新CSV状态为"失败"
                    update_csv_status(csv_path, email, "失败")
            except Exception as e:
                fail += 1
                outputs.append(f"ERROR {idx}/{len(rows)}: {email}: {e}")
                log.error(f"ERROR processing {email}: {e}")
                
                # 更新CSV状态为"失败"
                update_csv_status(csv_path, email, "失败")
            
            time.sleep(interval_ms / 1000.0)
        
        # 最终统计
        summary = f"\n{'='*60}\nBatch Registration Complete\n{'='*60}\nTotal: {len(rows)} | Success: {ok} | Failed: {fail}\n{'='*60}"
        log.info(summary)
        return "\n".join(outputs + [summary])

    # 比特浏览器模式：需要比特浏览器客户端
    if not bitbrowser_base_url:
        # 如果没有比特浏览器URL且不是Playwright模式，使用mock注册
        ok, fail = 0, 0
        outputs: List[str] = []
        with ThreadPoolExecutor(max_workers=max(1, concurrency)) as ex:
            futures = {}
            for rec in rows:
                email = rec.get("email")
                password = rec.get("password")
                fut = ex.submit(mock_register, email, password)
                futures[fut] = email
                time.sleep(interval_ms / 1000.0)
            for fut in as_completed(futures):
                email = futures[fut]
                try:
                    if fut.result():
                        ok += 1
                        outputs.append(f"SUCCESS {email}")
                    else:
                        fail += 1
                        outputs.append(f"FAIL {email}")
                except Exception as e:
                    fail += 1
                    outputs.append(f"ERROR {email}: {e}")
        summary = f"done. success={ok}, fail={fail}"
        log.info(summary)
        return "\n".join(outputs + [summary])

    client = BitBrowserClient(bitbrowser_base_url)
    ok, fail = 0, 0
    outputs: List[str] = []
    
    log.info(f"Starting batch registration for {len(rows)} accounts")
    
    for idx, rec in enumerate(rows, 1):
        email = rec.get("email")
        password = rec.get("password")
        code_url = rec.get("code_url")  # 邮箱验证码接码地址
        
        log.info(f"\n{'='*60}")
        log.info(f"Processing account {idx}/{len(rows)}: {email}")
        log.info(f"{'='*60}")
        payload: Dict[str, Any] = {
            "groupId": group_id or "",
            "userName": email,
            "password": password,
            "url": platform_url or "https://klingai.com",  # 使用klingai.com而不是app.klingai.com
            "proxyMethod": 2,
            "browserFingerPrint": {},
        }
        # 依据 CSV 每账号代理信息设置代理：默认 socks5
        host = rec.get("host")
        port = rec.get("port")
        puser = rec.get("proxyUserName")
        ppass = rec.get("proxyPassword")
        if host and port:
            payload.update({
                "proxyType": "socks5",
                "host": host,
                "port": int(port),
            })
            if puser:
                payload["proxyUserName"] = puser
            if ppass:
                payload["proxyPassword"] = ppass
        try:
            r = client.create_window(payload)
            if r.get("success"):
                data = r.get("data", {})
                wid = data.get("id") or ""
                try:
                    if wid:
                        # 打开比特浏览器窗口
                        open_result = client.open_window(wid)
                        log.info(f"Window opened for {email}: {open_result}")
                        
                        # 等待窗口完全打开
                        log.info("Waiting for window to fully initialize...")
                        time.sleep(5)  # 增加等待时间让窗口充分加载
                        
                        # 注：比特浏览器API可能不支持maximize/activate等方法，跳过这些操作
                except Exception as e:
                    # 记录错误但继续执行
                    log.warning(f"Failed to setup browser window for {email}: {e}")
                    pass
                # 自动化注册流程
                # 获取 DevTools WebSocket（用于Playwright附着）
                ws = None
                try:
                    log.info(f"Getting DevTools WebSocket for window {wid}...")
                    # 比特浏览器API返回WebSocket地址的方式可能是在open_window的返回值中
                    if open_result.get("success"):
                        ws_data = open_result.get("data", {})
                        ws = ws_data.get("ws") or ws_data.get("webSocketDebuggerUrl")
                        if ws:
                            log.info(f"✅ Got WebSocket from open_window: {ws}")
                        else:
                            log.info(f"Open window data: {ws_data}")
                            # 如果没有ws，尝试直接构造WebSocket URL
                            # 比特浏览器通常使用: ws://127.0.0.1:port/devtools/browser/{wid}
                            if "http" in ws_data.get("http", ""):
                                http_url = ws_data.get("http")
                                # 从httpURL提取端口
                                import re
                                port_match = re.search(r':(\d+)', http_url)
                                if port_match:
                                    port = port_match.group(1)
                                    ws = f"ws://127.0.0.1:{port}/devtools/browser"
                                    log.info(f"✅ Constructed WebSocket: {ws}")
                    
                    if not ws:
                        log.warning("⚠️ No WebSocket available, will launch new browser")
                        
                except Exception as e:
                    log.error(f"Failed to get WebSocket: {e}")
                    import traceback
                    log.error(traceback.format_exc())
                    ws = None

                auto_ok = run_registration_flow(
                    email=email,
                    password=password,
                    runtime_dir=runtime_dir,
                    xpaths=auto_xpaths or {},
                    proxy={
                        "host": host,
                        "port": port,
                        "username": puser,
                        "password": ppass,
                    },
                    platform_url=platform_url or "https://klingai.com",
                    code_url=code_url,
                    attach_ws=ws,
                    dry_run=dry_run,
                    browser_mode=browser_mode,  # 传递浏览器模式
                )
                
                if auto_ok:
                    ok += 1
                    success_msg = f"SUCCESS {idx}/{len(rows)}: {email}"
                    outputs.append(success_msg)
                    log.info(f"\u2705 {success_msg}")
                else:
                    fail += 1
                    fail_msg = f"FAIL {idx}/{len(rows)}: {email} - automation failed"
                    outputs.append(fail_msg)
                    log.error(f"\u274c {fail_msg}")
            else:
                fail += 1
                outputs.append(f"FAIL {email}: {r.get('msg')}")
                
                # 更新CSV状态为"失败"
                update_csv_status(csv_path, email, "失败")
        except Exception as e:
            fail += 1
            outputs.append(f"ERROR {email}: {e}")
            
            # 更新CSV状态为"失败"
            update_csv_status(csv_path, email, "失败")
        time.sleep(interval_ms / 1000.0)
    
    # 最终统计
    summary = f"\n{'='*60}\nBatch Registration Complete\n{'='*60}\nTotal: {len(rows)} | Success: {ok} | Failed: {fail}\n{'='*60}"
    log.info(summary)
    return "\n".join(outputs + [summary])
