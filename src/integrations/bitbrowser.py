from typing import Any, Dict, Optional
import httpx


class BitBrowserClient:
    def __init__(self, base_url: str, timeout: float = 60.0):
        """
        初始化比特浏览器客户端
        
        参数：
            base_url: 比特浏览器API地址
            timeout: 请求超时时间（秒），默认60秒
        """
        self.base = base_url.rstrip("/")
        # 增加超时时间到60秒，避免打开窗口时超时
        # 增加重试机制和连接池配置
        self._client = httpx.Client(
            timeout=httpx.Timeout(timeout, connect=30.0, read=30.0, write=30.0, pool=5.0),
            limits=httpx.Limits(max_keepalive_connections=10, max_connections=20),
            # 禁用代理
        )

    def post(self, path: str, json: Dict[str, Any]) -> Dict[str, Any]:
        # 增加重试机制
        max_retries = 3
        for attempt in range(max_retries):
            try:
                r = self._client.post(f"{self.base}{path}", json=json)
                r.raise_for_status()
                return r.json()
            except Exception as e:
                # 记录网络错误详情
                import logging
                log = logging.getLogger(__name__)
                if attempt < max_retries - 1:
                    log.warning(f"⚠️ 网络请求失败 {path} (尝试 {attempt + 1}/{max_retries}): {e}")
                    import time
                    time.sleep(2 ** attempt)  # 指数退避
                    continue
                else:
                    log.error(f"❌ 网络请求失败 {path}: {e}")
                    # 重新抛出异常让上层处理
                    raise

    def post_variants(self, paths: list, json: Dict[str, Any]) -> Dict[str, Any]:
        last_err = None
        for p in paths:
            try:
                return self.post(p, json)
            except Exception as e:
                last_err = e
                import logging
                logging.getLogger(__name__).warning(f"endpoint_try_fail path={p}: {e}")
                continue
        if last_err:
            raise last_err
        return {}

    def get(self, path: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        # 增加重试机制
        max_retries = 3
        for attempt in range(max_retries):
            try:
                r = self._client.get(f"{self.base}{path}", params=params)
                r.raise_for_status()
                return r.json()
            except Exception as e:
                # 记录网络错误详情
                import logging
                log = logging.getLogger(__name__)
                if attempt < max_retries - 1:
                    log.warning(f"⚠️ 网络请求失败 {path} (尝试 {attempt + 1}/{max_retries}): {e}")
                    import time
                    time.sleep(2 ** attempt)  # 指数退避
                    continue
                else:
                    log.error(f"❌ 网络请求失败 {path}: {e}")
                    # 重新抛出异常让上层处理
                    raise

    def get_variants(self, paths: list, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        last_err = None
        for p in paths:
            try:
                return self.get(p, params)
            except Exception as e:
                last_err = e
                import logging
                logging.getLogger(__name__).warning(f"endpoint_try_fail path={p}: {e}")
                continue
        if last_err:
            raise last_err
        return {}

    def health(self) -> Dict[str, Any]:
        return self.post("/health", {})

    def create_window(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        return self.post("/browser/update", payload)

    def open_window(self, window_id: str) -> Dict[str, Any]:
        return self.post("/browser/open", {"id": window_id})

    def close_window(self, window_id: str) -> Dict[str, Any]:
        return self.post("/browser/close", {"id": window_id})
    
    def delete_window(self, window_id: str, password: Optional[str] = None) -> Dict[str, Any]:
        """
        删除窗口（永久删除）
        
        参数：
            window_id: 窗口ID
            password: 比特浏览器密码（如果需要）
        """
        payload = {"id": window_id}
        if password:
            payload["password"] = password
        return self.post("/browser/delete", payload)

    def list_windows(self) -> Dict[str, Any]:
        return self.get("/browser/list")

    def switch_tab(self, window_id: str, tab_id: str) -> Dict[str, Any]:
        return self.post_variants([
            "/browser/switchTab",
            "/browser/switch-tab",
            "/browser/tab/switch",
        ], {"id": window_id, "tabId": tab_id})

    def get_window_tabs(self, window_id: str) -> Dict[str, Any]:
        return self.post_variants([
            "/browser/getTabs",
            "/browser/tabs",
            "/browser/tab/list",
        ], {"id": window_id})

    def navigate_to(self, window_id: str, url: str) -> Dict[str, Any]:
        return self.post_variants([
            "/browser/navigate",
            "/browser/tab/navigate",
            "/browser/url",
        ], {"id": window_id, "url": url})

    def close_tab(self, window_id: str, tab_id: str) -> Dict[str, Any]:
        """关闭指定标签页"""
        return self.post_variants([
            "/browser/closeTab",
            "/browser/close-tab",
            "/browser/tab/close",
        ], {"id": window_id, "tabId": tab_id})

    def open_tab(self, window_id: str, url: str) -> Dict[str, Any]:
        """在新标签页中打开URL"""
        return self.post_variants([
            "/browser/openTab",
            "/browser/open-tab",
            "/browser/tab/open",
        ], {"id": window_id, "url": url})

    def activate(self, window_id: str) -> Dict[str, Any]:
        """激活窗口并确保显示在前台"""
        # 注意：/browser/activate 端点不存在，使用最大化代替
        try:
            result = self.maximize(window_id)  # 使用最大化确保窗口显示
            return result
        except Exception as e:
            import logging
            log = logging.getLogger(__name__)
            log.error(f"❌ 激活窗口失败 {window_id}: {e}")
            raise

    def maximize(self, window_id: str) -> Dict[str, Any]:
        """最大化窗口"""
        return self.post("/browser/maximize", {"id": window_id})

    def devtools(self, window_id: str) -> Dict[str, Any]:
        """获取DevTools WebSocket地址"""
        return self.post("/browser/devtools", {"id": window_id})

    def list_groups(self, page: int = 0, page_size: int = 100) -> Dict[str, Any]:
        """获取分组列表，增加重试机制"""
        max_retries = 3
        for attempt in range(max_retries):
            try:
                return self.post("/group/list", {"page": page, "pageSize": page_size})
            except Exception as e:
                import logging
                log = logging.getLogger(__name__)
                if attempt < max_retries - 1:
                    log.warning(f"⚠️ 获取分组列表失败 (尝试 {attempt + 1}/{max_retries}): {e}")
                    import time
                    time.sleep(2 ** attempt)  # 指数退避
                    continue
                else:
                    log.error(f"❌ 获取分组列表最终失败: {e}")
                    raise

    def add_group(self, group_name: str, sort_num: int = 0) -> Dict[str, Any]:
        """添加分组，增加重试机制"""
        max_retries = 3
        for attempt in range(max_retries):
            try:
                return self.post("/group/add", {"groupName": group_name, "sortNum": sort_num})
            except Exception as e:
                import logging
                log = logging.getLogger(__name__)
                if attempt < max_retries - 1:
                    log.warning(f"⚠️ 创建分组失败 (尝试 {attempt + 1}/{max_retries}): {e}")
                    import time
                    time.sleep(2 ** attempt)  # 指数退避
                    continue
                else:
                    log.error(f"❌ 创建分组最终失败: {e}")
                    raise

    def get_or_create_group(self, group_name: str) -> Optional[str]:
        """获取或创建分组，返回分组ID"""
        import logging
        log = logging.getLogger(__name__)
        
        try:
            log.info(f"🔍 开始查找分组: '{group_name}'")
            
            # 获取所有分组
            result = self.list_groups()
            log.debug(f"📊 分组列表API响应: {result}")
            
            if not result.get("success"):
                log.error(f"❌ 获取分组列表失败: {result.get('msg', '未知错误')}")
                return None
            
            data = result.get("data", {})
            groups = data.get("list", [])
            log.info(f"📋 当前共有 {len(groups)} 个分组")
            
            # 显示所有分组信息（用于调试）
            log.debug(f"📋 分组列表详情:")
            found_group_id = None  # 用于存储找到的分组ID
            for i, group in enumerate(groups):
                group_name_display = group.get("groupName", "")
                group_id_display = group.get("id", "")
                # 显示分组的详细信息用于调试
                group_details = {k: v for k, v in group.items() if k not in ['id', 'groupName']}
                log.debug(f"   [{i+1}] '{group_name_display}' (ID: {group_id_display}) Details: {group_details}")
                
                # 立即检查是否匹配
                clean_existing = ''.join(group_name_display.split())
                clean_target = ''.join(group_name.split())
                log.debug(f"   🔍 立即匹配检查: '{clean_existing}' vs '{clean_target}'")
                
                if clean_existing.lower() == clean_target.lower():
                    log.info(f"✅ 立即匹配成功: '{group_name}' (原始名称: '{group_name_display}', ID: {group_id_display})")
                    found_group_id = group_id_display
            
            # 如果立即找到了匹配的分组，直接返回
            if found_group_id:
                return found_group_id
            
            # 查找匹配的分组
            for group in groups:
                existing_name = group.get("groupName", "")
                group_id = group.get("id")
                log.debug(f"🔍 检查分组: '{existing_name}' (ID: {group_id})")
                
                # 增强匹配逻辑：去除所有空白字符后比较
                clean_existing = ''.join(existing_name.split())
                clean_target = ''.join(group_name.split())
                
                log.debug(f"🔍 匹配检查: '{clean_existing}' vs '{clean_target}' (原始: '{existing_name}' vs '{group_name}')")
                
                # 如果匹配失败，记录详细对比信息
                if clean_existing.lower() != clean_target.lower():
                    # 显示字符级别的差异
                    log.debug(f"   字符串长度: {len(clean_existing)} vs {len(clean_target)}")
                    if len(clean_existing) == len(clean_target):
                        # 检查每个字符
                        for i, (c1, c2) in enumerate(zip(clean_existing.lower(), clean_target.lower())):
                            if c1 != c2:
                                log.debug(f"   字符差异位置 {i}: '{c1}' vs '{c2}' (Unicode: {ord(c1)} vs {ord(c2)})")
                                break
                
                if clean_existing.lower() == clean_target.lower():
                    log.info(f"✅ 找到匹配的分组: '{group_name}' (原始名称: '{existing_name}', ID: {group_id})")
                    return group_id
            
            # 未找到，创建新分组
            log.info(f"🆕 未找到分组 '{group_name}'，尝试创建...")
            add_result = self.add_group(group_name)
            log.debug(f"📊 创建分组API响应: {add_result}")
            
            if not add_result.get("success"):
                error_msg = add_result.get('msg', '未知错误')
                log.error(f"❌ 创建分组失败: {error_msg}")
                
                # 特殊处理：如果是因为名称已存在导致创建失败
                if "已被使用" in error_msg or "already" in error_msg.lower() or "exists" in error_msg.lower():
                    log.warning(f"⚠️ API报告分组已存在但未在列表中找到，尝试使用随机后缀重试...")
                    
                    # 生成带时间戳的分组名
                    import time
                    timestamp = int(time.time())
                    fallback_group_name = f"{group_name}_{timestamp}"
                    log.info(f"🔄 尝试创建后备分组: '{fallback_group_name}'")
                    
                    fallback_result = self.add_group(fallback_group_name)
                    if fallback_result.get("success"):
                        fallback_data = fallback_result.get("data", {})
                        fallback_group_id = None
                        if isinstance(fallback_data, dict):
                            fallback_group_id = fallback_data.get("id")
                        elif isinstance(fallback_data, str):
                            fallback_group_id = fallback_data
                        
                        if fallback_group_id:
                            log.info(f"✅ 后备分组创建成功: '{fallback_group_name}' (ID: {fallback_group_id})")
                            return fallback_group_id
                        else:
                            log.error(f"❌ 后备分组创建成功但未获取到ID: {fallback_data}")
                    else:
                        log.error(f"❌ 后备分组创建失败: {fallback_result.get('msg', '未知错误')}")
                
                # 如果是因为名称已存在导致创建失败，重新查询分组列表
                if "已被使用" in error_msg or "already" in error_msg.lower() or "exists" in error_msg.lower():
                    log.info(f"🔄 分组名称已存在，重新获取分组列表...")
                    
                    # 重新获取分组列表
                    retry_result = self.list_groups()
                    if retry_result.get("success"):
                        retry_data = retry_result.get("data", {})
                        retry_groups = retry_data.get("list", [])
                        
                        # 显示所有分组信息（用于调试）
                        log.info(f"📋 重新查询得到 {len(retry_groups)} 个分组")
                        log.debug(f"📋 重新查询分组列表详情:")
                        for i, group in enumerate(retry_groups):
                            group_name_display = group.get("groupName", "")
                            group_id_display = group.get("id", "")
                            # 显示分组的详细信息用于调试
                            group_details = {k: v for k, v in group.items() if k not in ['id', 'groupName']}
                            log.debug(f"   [{i+1}] '{group_name_display}' (ID: {group_id_display}) Details: {group_details}")
                        
                        # 再次查找匹配的分组
                        for group in retry_groups:
                            existing_name = group.get("groupName", "")
                            group_id = group.get("id")
                            
                            # 增强匹配逻辑：去除所有空白字符后比较
                            clean_existing = ''.join(existing_name.split())
                            clean_target = ''.join(group_name.split())
                            
                            log.debug(f"🔍 重试匹配检查: '{clean_existing}' vs '{clean_target}' (原始: '{existing_name}' vs '{group_name}')")
                            
                            # 如果匹配失败，记录详细对比信息
                            if clean_existing.lower() != clean_target.lower():
                                # 显示字符级别的差异
                                log.debug(f"   字符串长度: {len(clean_existing)} vs {len(clean_target)}")
                                if len(clean_existing) == len(clean_target):
                                    # 检查每个字符
                                    for i, (c1, c2) in enumerate(zip(clean_existing.lower(), clean_target.lower())):
                                        if c1 != c2:
                                            log.debug(f"   字符差异位置 {i}: '{c1}' vs '{c2}' (Unicode: {ord(c1)} vs {ord(c2)})")
                                            break
                            
                            if clean_existing.lower() == clean_target.lower():
                                log.info(f"✅ 重新查询找到匹配的分组: '{group_name}' (原始名称: '{existing_name}', ID: {group_id})")
                                return group_id
                        
                        log.error(f"❌ 重新查询仍未找到分组: {group_name} (原始错误: {error_msg})")
                        log.error(f"📋 重新查询的分组列表: {retry_groups}")
                        
                        # 兜底策略：如果API说分组已存在，但查询不到，尝试模糊匹配
                        if "已被使用" in error_msg or "already" in error_msg.lower() or "exists" in error_msg.lower():
                            log.warning("🔄 启用兜底策略：尝试模糊匹配现有分组...")
                            for group in retry_groups:
                                existing_name = group.get("groupName", "")
                                group_id = group.get("id")
                                
                                # 更宽松的匹配：只要包含目标名称就匹配
                                if group_name.lower() in existing_name.lower() or existing_name.lower() in group_name.lower():
                                    log.warning(f"⚠️ 兜底匹配成功: '{group_name}' 匹配到 '{existing_name}' (ID: {group_id})")
                                    return group_id
                            
                            log.error("❌ 兜底策略也未找到匹配分组")
                    else:
                        log.error(f"❌ 重新获取分组列表失败: {retry_result.get('msg', '未知错误')}")
                
                return None
            
            # 尝试多种可能的数据结构
            add_data = add_result.get("data", {})
            new_group_id = None
            
            # 情况1: data.id
            if isinstance(add_data, dict):
                new_group_id = add_data.get("id")
            # 情况2: data 直接是字符串ID
            elif isinstance(add_data, str):
                new_group_id = add_data
            
            if new_group_id:
                log.info(f"✅ 成功创建分组: '{group_name}' (ID: {new_group_id})")
                return new_group_id
            else:
                log.error(f"❌ 创建分组成功但未获取到ID，响应数据: {add_data}")
                return None
                
        except Exception as e:
            log.error(f"❌ 分组操作异常: {e}")
            import traceback
            log.error(traceback.format_exc())
            return None
