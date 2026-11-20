"""把人工/AI 整理好的事实 JSON（来源用 URL 标示）导入 data/ipos/。

用法：python scripts/import_facts.py facts.json
输入：[{"name":..., "facts": {key: {"v":..., "src":[url], "note":...}}, "use_of_proceeds": [...],
        "financials": [...], "quotes": [...], "source_meta": {url: {title, publisher, date}}}]
已存在的公司只补空白字段，不覆盖。
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from update import IPO_DIR, TODAY, kind_of, slugify  # noqa: E402


def main(path: str) -> None:
    items = json.loads(Path(path).read_text(encoding="utf-8"))
    for it in items:
        slug = it.get("slug") or slugify(it["name"])
        p = IPO_DIR / f"{slug}.json"
        rec = json.loads(p.read_text(encoding="utf-8")) if p.exists() else {
            "slug": slug, "name": it["name"],
            "name_zh": it.get("name_zh") or it["name"].replace(" Berhad", "").replace(" Bhd", ""),
            "stock_code": None, "facts": {}, "use_of_proceeds": [], "financials": [], "sources": {},
            "todo_official": "待补：Bursa 上市公告与招股书链接。"}
        url2sid = {s["url"]: sid for sid, s in rec["sources"].items()}

        def sid_for(url: str) -> str:
            if url not in url2sid:
                sid = f"s{len(rec['sources']) + 1}"
                meta = it.get("source_meta", {}).get(url, {})
                rec["sources"][sid] = {"title": meta.get("title", url), "publisher": meta.get("publisher", ""),
                                       "kind": kind_of(url), "date": meta.get("date"), "url": url, "accessed": TODAY}
                url2sid[url] = sid
            return url2sid[url]

        def conv(srcs):
            return [sid_for(u) for u in (srcs if isinstance(srcs, list) else [srcs])]

        for k, f in it.get("facts", {}).items():
            if k not in rec["facts"] and f.get("v") is not None:
                f = dict(f)
                f["src"] = conv(f.get("src", []))
                rec["facts"][k] = f
        for listkey in ("use_of_proceeds", "financials", "allocation"):
            if it.get(listkey) and not rec.get(listkey):
                rec[listkey] = [dict(x, src=conv(x["src"])) for x in it[listkey]]
        if it.get("quotes") and not rec.get("quotes"):
            rec["quotes"] = [dict(q, src=conv(q["src"])[0]) for q in it["quotes"]]
        for extra in ("name_zh", "sector_zh", "one_liner", "analysis", "todo_official"):
            if it.get(extra):
                rec[extra] = it[extra]
        p.write_text(json.dumps(rec, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print("✓", slug)


if __name__ == "__main__":
    main(sys.argv[1])
