"""从后台（Supabase Storage）拿新上传的招股书 → 交给 ingest_prospectus 处理 → 回报状态。

GitHub Actions 每小时跑一次。没有待处理的就什么都不做（不花 API 钱）。
需要环境变量：SUPABASE_URL、SUPABASE_SERVICE_ROLE_KEY、ANTHROPIC_API_KEY。
PDF 只放在临时文件夹，处理完就删，不放进仓库、不放上网站。
"""
from __future__ import annotations

import datetime as dt
import json
import os
import sys
import tempfile
from pathlib import Path

import requests

sys.path.insert(0, str(Path(__file__).parent))
import ai  # noqa: E402
import ingest_prospectus as ip  # noqa: E402

URL = os.environ.get("SUPABASE_URL", "").rstrip("/")
KEY = os.environ.get("SUPABASE_SERVICE_ROLE_KEY", "")
H = {"apikey": KEY, "Authorization": f"Bearer {KEY}"}


def set_status(row_id: int, **fields) -> None:
    fields["processed_at"] = dt.datetime.now(dt.timezone.utc).isoformat()
    requests.patch(f"{URL}/rest/v1/prospectus_uploads?id=eq.{row_id}", headers={**H, "Content-Type": "application/json"},
                   data=json.dumps(fields), timeout=30).raise_for_status()


def main() -> int:
    if not (URL and KEY):
        print("没有设定 Supabase，跳过后台招股书。")
        return 0
    rows = requests.get(f"{URL}/rest/v1/prospectus_uploads?status=eq.pending&order=created_at&select=*",
                        headers=H, timeout=30)
    rows.raise_for_status()
    rows = rows.json()
    if not rows:
        print("后台没有新的招股书。")
        return 0
    if not ai.available():
        print("有新招股书，但没有 ANTHROPIC_API_KEY，先不处理。")
        return 0
    log: list[str] = []
    for row in rows:
        with tempfile.TemporaryDirectory() as tmp:
            pdf = Path(tmp) / "prospectus.pdf"  # 文件名不用来猜公司，改按招股书里的公司名
            try:
                r = requests.get(f"{URL}/storage/v1/object/prospectus/{row['path']}", headers=H, timeout=300)
                r.raise_for_status()
                pdf.write_bytes(r.content)
                before = len(log)
                slug = ip.ingest(pdf, row.get("slug"), row.get("bursa_url"), log)
                note = "；".join(log[before:])[:500]
                if slug:
                    set_status(row["id"], status="done", slug=slug, message=note)
                else:
                    set_status(row["id"], status="failed", message=note or "读不到内容")
            except Exception as e:  # 一份失败不影响其他
                log.append(f"{row.get('file_name')}: 处理失败 {e}")
                set_status(row["id"], status="failed", message=str(e)[:500])
    cl_p = ip.ROOT / "data" / "changelog.json"
    cl = json.loads(cl_p.read_text(encoding="utf-8")) if cl_p.exists() else []
    cl.insert(0, {"date": ip.TODAY, "changes": log})
    cl_p.write_text(json.dumps(cl[:200], ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print("\n".join(log))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
