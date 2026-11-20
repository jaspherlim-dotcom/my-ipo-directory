"""把 premium_out/*.html（会员内容）上传到 Supabase premium_pages 表。

需要环境变量：SUPABASE_URL、SUPABASE_SERVICE_ROLE_KEY（只放在 GitHub Secrets，绝不放进网页）。
"""
from __future__ import annotations

import os
import sys
from pathlib import Path

import requests

ROOT = Path(__file__).resolve().parent.parent


def main() -> int:
    url, key = os.environ.get("SUPABASE_URL"), os.environ.get("SUPABASE_SERVICE_ROLE_KEY")
    if not url or not key:
        print("没有设定 SUPABASE_URL / SUPABASE_SERVICE_ROLE_KEY，跳过上传会员内容。")
        return 0
    rows = [{"slug": p.stem, "html": p.read_text(encoding="utf-8")} for p in sorted((ROOT / "premium_out").glob("*.html"))]
    if not rows:
        print("没有会员内容。")
        return 0
    r = requests.post(
        f"{url.rstrip('/')}/rest/v1/premium_pages",
        json=rows,
        headers={"apikey": key, "Authorization": f"Bearer {key}", "Content-Type": "application/json",
                 "Prefer": "resolution=merge-duplicates,return=minimal"},
        timeout=60,
    )
    if r.status_code >= 300:
        print(f"上传失败 {r.status_code}: {r.text[:500]}")
        return 1
    print(f"已上传 {len(rows)} 篇会员内容")
    return 0


if __name__ == "__main__":
    sys.exit(main())
