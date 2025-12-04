from pathlib import Path
import csv
from typing import List, Dict, Any


def read_csv_rows(csv_path: Path) -> List[List[str]]:
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
            rows.append([str(c).strip() for c in row])
    return rows


def parse_accounts_csv(csv_path: Path) -> List[Dict[str, Any]]:
    rows = read_csv_rows(csv_path)
    out: List[Dict[str, Any]] = []
    if not rows:
        return out
    # 判断首行是否表头
    header_candidates = {"email", "password", "host", "port", "proxyusername", "proxypassword"}
    start_idx = 0
    first = [c.lower() for c in rows[0]]
    if any(c in header_candidates for c in first):
        start_idx = 1
    for row in rows[start_idx:]:
        if len(row) < 2:
            continue
        rec: Dict[str, Any] = {
            "email": row[0],
            "password": row[1],
        }
        if len(row) >= 4:
            rec["host"] = row[2]
            rec["port"] = int(row[3]) if row[3] else None
        if len(row) >= 6:
            rec["proxyUserName"] = row[4]
            rec["proxyPassword"] = row[5]
        out.append(rec)
    return out

