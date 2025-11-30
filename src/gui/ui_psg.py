import PySimpleGUI as sg
from pathlib import Path
import csv
import json
from typing import List, Dict, Any

from ..utils.logger import get_logger
from ..utils.config_store import load_config, save_config, reset_config
from ..services.account import register_accounts_batch


def parse_csv_preview(csv_path: Path) -> List[List[str]]:
    rows: List[List[str]] = []
    with csv_path.open("r", encoding="utf-8-sig", newline="") as f:
        sample = f.read(2048)
        f.seek(0)
        try:
            dialect = csv.Sniffer().sniff(sample)
        except Exception:
            dialect = csv.excel
        reader = csv.reader(f, dialect)
        for row in reader:
            rows.append(row)
    return rows


def load_xpath_json(path: Path) -> Dict[str, Any]:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}


def launch(runtime_dir: Path):
    log = get_logger(__name__)
    cfg = load_config(runtime_dir)

    sg.theme("DarkGrey13")

    table = sg.Table(values=[], headings=["email", "password", "code_url", "proxy_ip", "proxy_port", "proxy_user", "proxy_pass"],
                     auto_size_columns=True, justification='left', expand_x=True, expand_y=True, key='-TABLE-')

    layout = [
        [sg.Text("CSV 文件"), sg.Input(default_text=cfg.get("csv_path", ""), key='-CSV-', expand_x=True), sg.FileBrowse(file_types=(("CSV", "*.csv"),))],
        [sg.Button("加载CSV", key='-LOAD-'), sg.Text("状态:", size=(6,1)), sg.Text("就绪", key='-STATUS-', size=(40,1))],
        [table],
        [sg.Text("比特浏览器接口"), sg.Input(default_text=cfg.get("api_base"), key='-API-', expand_x=True)],
        [sg.Text("平台URL"), sg.Input(default_text=cfg.get("platform_url"), key='-URL-', expand_x=True)],
        [sg.Text("groupId"), sg.Input(default_text=cfg.get("group_id"), key='-GROUP-', expand_x=True)],
        [sg.Text("并发"), sg.Spin([i for i in range(1, 21)], initial_value=cfg.get("concurrency", 3), key='-CONC-'),
         sg.Text("间隔(ms)"), sg.Spin([i*50 for i in range(0, 41)], initial_value=cfg.get("interval_ms", 300), key='-INTERVAL-')],
        [sg.Checkbox("启用自动化注册（XPath）", default=cfg.get("auto", True), key='-AUTO-')],
        [sg.Text("XPath JSON 文件"), sg.Input(default_text=cfg.get("xpath_path", ""), key='-XJSON-', expand_x=True), sg.FileBrowse(file_types=(("JSON", "*.json"),))],
        [sg.Checkbox("高级：直接输入 XPath JSON", default=False, key='-ADV-')],
        [sg.Multiline(size=(80,8), key='-XJSON_TEXT-', expand_x=True, expand_y=False)],
        [sg.Multiline(size=(80,8), key='-LOG-', expand_x=True, expand_y=True)],
        [sg.Button("开始注册", key='-RUN-'), sg.Button("保存参数", key='-SAVE-'), sg.Button("恢复默认", key='-RESET-'), sg.Button("退出", key='-EXIT-')]
    ]

    win = sg.Window("KL-zhanghao GUI", layout, resizable=True)

    while True:
        event, values = win.read()
        if event in (sg.WIN_CLOSED, '-EXIT-'):
            break
        try:
            if event == '-LOAD-':
                p = Path(values['-CSV-'])
                if not p.exists():
                    win['-STATUS-'].update("CSV 文件不存在")
                    continue
                preview = parse_csv_preview(p)
                if preview:
                    # 如果首行不是表头（仅一行或不含典型字段），则整体视为数据行
                    candidates = ["email", "password", "host", "port"]
                    first_row = preview[0]
                    is_header = any(str(cell).lower() in candidates for cell in first_row)
                    data_rows = preview[1:] if (is_header and len(preview) > 1) else preview
                    win['-TABLE-'].update(values=data_rows)
                    win['-STATUS-'].update(f"已加载 {len(data_rows)} 行")
                else:
                    win['-STATUS-'].update("CSV 为空")

            if event == '-SAVE-':
                cfg_update = {
                    "csv_path": values['-CSV-'],
                    "api_base": values['-API-'],
                    "platform_url": values['-URL-'],
                    "group_id": values['-GROUP-'],
                    "concurrency": int(values['-CONC-']),
                    "interval_ms": int(values['-INTERVAL-']),
                    "auto": bool(values['-AUTO-']),
                    "xpath_path": values['-XJSON-'],
                }
                save_config(runtime_dir, cfg_update)
                win['-STATUS-'].update("参数已保存")

            if event == '-RESET-':
                reset_config(runtime_dir)
                for k,v in load_config(runtime_dir).items():
                    if k == 'csv_path': win['-CSV-'].update(v)
                    if k == 'api_base': win['-API-'].update(v)
                    if k == 'platform_url': win['-URL-'].update(v)
                    if k == 'group_id': win['-GROUP-'].update(v)
                    if k == 'concurrency': win['-CONC-'].update(v)
                    if k == 'interval_ms': win['-INTERVAL-'].update(v)
                    if k == 'auto': win['-AUTO-'].update(v)
                    if k == 'xpath_path': win['-XJSON-'].update(v)
                win['-STATUS-'].update("已恢复默认")

            if event == '-RUN-':
                csv_path = Path(values['-CSV-'])
                if not csv_path.exists():
                    win['-STATUS-'].update("请先选择并加载 CSV")
                    continue
                auto = bool(values['-AUTO-'])
                adv = bool(values['-ADV-'])
                xjson_text = values['-XJSON_TEXT-'] or ""
                xpath_path = Path(values['-XJSON-']) if values['-XJSON-'] else None
                if auto and adv and xjson_text.strip():
                    try:
                        xjson = json.loads(xjson_text)
                    except Exception:
                        xjson = {}
                else:
                    xjson = load_xpath_json(xpath_path) if (xpath_path and xpath_path.exists() and auto) else {}

                out = register_accounts_batch(
                    csv_path=csv_path,
                    runtime_dir=runtime_dir,
                    concurrency=int(values['-CONC-']),
                    interval_ms=int(values['-INTERVAL-']),
                    bitbrowser_base_url=values['-API-'] or None,
                    platform_url=values['-URL-'] or None,
                    group_id=values['-GROUP-'] or None,
                    auto_xpaths=xjson,
                    dry_run=not auto or not bool(xjson),
                )
                win['-LOG-'].update(out)
        except Exception as e:
            log.exception("GUI error")
            win['-STATUS-'].update(f"错误: {e}")

    win.close()
