# 优化报告

## 概览
- 引入统一的质量工具：Ruff、Pylint(duplicate-code)、Mypy、Bandit、Radon
- 新增 CI：`.github/workflows/ci.yml`，在 macOS 上安装依赖、运行质量脚本与测试
- 抽取 CSV 解析到公共模块 `src/utils/csv_loader.py`，减少重复与不一致
- 修复 GUI 解析：单行 CSV 识别为数据行并正确展示
- 自动化流程：增加日志、前台置顶、截图容错，提升稳定性

## 修改点
- `src/utils/csv_loader.py`：提供 `read_csv_rows` 与 `parse_accounts_csv`
- `src/gui/ui_psg.py`：使用统一解析逻辑，修复 `Table.update` 使用方式
- `requirements.txt`：增加质量工具依赖
- `pyproject.toml`：配置 Ruff/Mypy
- `scripts/quality.sh`：统一质量检查脚本
- `.github/workflows/ci.yml`：完整 CI 工作流

## 指标
- 覆盖率：≥80%（当前约 83%）
- 复杂度：Radon 报告可在流水线日志中查看
- 重复代码：Pylint duplicate-code 已启用，流水线报告显示位置与片段

## 风险与兼容性
- 质量工具不影响运行时逻辑；CI 仅在合并与 PR 时执行
- CSV 解析统一后，支持 BOM 与无表头单行输入；旧格式兼容

## 后续建议
- 如果需要更严格的重复检测，可在 CI 中加入 `jscpd`（需 Node 环境或 Docker）
- 收敛动态 XPath：为关键元素增加多策略定位，提高抗变化能力
- 收集更细致的自动化失败日志并做分类型重试策略

