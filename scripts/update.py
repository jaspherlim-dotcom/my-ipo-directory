"""每日自动更新流程（GitHub Actions 定时跑）。

1. 发现：用 Claude 网络搜索找新的 Bursa IPO 和新资料链接（需要 ANTHROPIC_API_KEY）。
2. 抓取：遵守 robots.txt，礼貌抓取每个原文链接。
3. 抽取：从原文抽事实，每项必须附原文引句，程序核对引句和数字。
4. 合并：只补空白字段；跟已有资料冲突的，记录到 conflicts 等人工处理，不会自动覆盖。
5. 解读：新公司或资料有变时，重写商业模式 9 宫格（人工 reviewed 过的不动）。
6. 写 changelog，交给 build.py 生成网站。

没有 API key 时：只重新检查已收录链接是否还能打开，然后照常建站。
"""
from __future__ import annotations

import datetime as dt
import hashlib
import json
import re
import sys
from pathlib import Path
from urllib.parse import urlparse

sys.path.insert(0, str(Path(__file__).parent))
import ai  # noqa: E402
import fetcher  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
IPO_DIR = ROOT / "data" / "ipos"
STATE = ROOT / "data" / "_state.json"
CHANGELOG = ROOT / "data" / "changelog.json"
CONFIG = json.loads((ROOT / "config.json").read_text(encoding="utf-8"))

TODAY = dt.date.today().isoformat()
NUMERIC = {"issue_price_rm", "new_shares", "ofs_shares", "proceeds_rm", "market_cap_rm", "enlarged_shares",
           "oversub_public", "applications", "first_day_open_rm", "first_day_close_rm", "yield_pct"}


def slugify(name: str) -> str:
    s = re.sub(r"\b(berhad|bhd|holdings?|group)\b", "", name.lower())
    return re.sub(r"[^a-z0-9]+", "-", s).strip("-") or "ipo"


def kind_of(url: str) -> str:
    host = urlparse(url).netloc.lower()
    for kind, hosts in CONFIG["source_kinds"].items():
        if any(host.endswith(h) for h in hosts):
            return kind
    return "news"


def load_all() -> dict[str, dict]:
    return {p.stem: json.loads(p.read_text(encoding="utf-8")) for p in IPO_DIR.glob("*.json")}


def save(rec: dict) -> None:
    (IPO_DIR / f"{rec['slug']}.json").write_text(json.dumps(rec, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def coerce(key: str, value: str):
    if key in NUMERIC:
        try:
            return float(value.replace(",", "")) if "." in value else int(value.replace(",", ""))
        except ValueError:
            return None
    if key.endswith("_date") or key in {"app_open", "app_close"}:
        return value if re.fullmatch(r"\d{4}-\d{2}-\d{2}", value) else None
    return value


def number_matches_evidence(value, evidence: str) -> bool:
    """数字的前几位有效数字必须出现在引句里，例如 31920000 ↔ “RM31.92mil”。"""
    digits = re.sub(r"\D", "", f"{value}").lstrip("0").rstrip("0") or "0"
    ev = re.sub(r"\D", "", evidence)
    return digits[:3] in ev


def add_source(rec: dict, url: str, title: str | None) -> str:
    for sid, s in rec["sources"].items():
        if s["url"] == url:
            return sid
    sid = f"s{len(rec['sources']) + 1}"
    rec["sources"][sid] = {"title": title or url, "publisher": urlparse(url).netloc.replace("www.", ""),
                           "kind": kind_of(url), "date": None, "url": url, "accessed": TODAY}
    return sid


def merge_facts(rec: dict, sid: str, extraction, log: list) -> bool:
    changed = False
    for f in extraction.facts:
        val = coerce(f.key, f.value)
        if val is None or (f.key in NUMERIC and not number_matches_evidence(val, f.evidence)):
            continue
        cur = rec["facts"].get(f.key)
        if cur is None:
            rec["facts"][f.key] = {"v": val, "src": [sid], "auto": True, "evidence": f.evidence}
            log.append(f"{rec['name']}: 新增 {f.key} = {val}")
            changed = True
        elif cur["v"] == val:
            if sid not in cur["src"]:
                cur["src"].append(sid)  # 多一个来源佐证
                changed = True
        else:
            conflict = {"key": f.key, "existing": cur["v"], "new": val, "src": sid, "evidence": f.evidence, "found": TODAY}
            rec.setdefault("conflicts", [])
            if not any(c["key"] == f.key and c["new"] == val for c in rec["conflicts"]):
                rec["conflicts"].append(conflict)
                log.append(f"{rec['name']}: ⚠ {f.key} 资料冲突（现有 {cur['v']}，新来源 {val}），待人工核实")
                changed = True
    return changed


def main() -> int:
    state = json.loads(STATE.read_text(encoding="utf-8")) if STATE.exists() else {"seen": {}}
    records = load_all()
    log: list[str] = []

    if not ai.available():
        print("没有 ANTHROPIC_API_KEY：跳过发现和抽取，只检查链接。")
        for rec in records.values():
            for s in rec["sources"].values():
                if s["url"] not in state["seen"]:
                    state["seen"][s["url"]] = {"status": "seeded", "checked": TODAY}
    else:
        known = [r["name"] for r in records.values()]
        candidates = ai.discover(TODAY, known)
        print(f"发现 {len(candidates)} 个候选")
        by_name = {r["name"].lower(): r for r in records.values()}
        for c in candidates:
            name = (c.get("name") or "").strip()
            if not name:
                continue
            rec = by_name.get(name.lower()) or records.get(slugify(name))
            for url in c.get("urls", [])[:4]:
                if url in state["seen"]:
                    continue
                html, status = fetcher.fetch(url)
                state["seen"][url] = {"status": status, "checked": TODAY}
                if html is None:
                    print(f"  跳过 {url}: {status}")
                    continue
                text = fetcher.html_to_text(html)
                state["seen"][url]["sha1"] = hashlib.sha1(text.encode()).hexdigest()
                ex = ai.extract(url, text)
                if ex is None or not ex.is_bursa_ipo or not ex.facts:
                    continue
                if rec is None:
                    slug = slugify(name)
                    rec = {"slug": slug, "name": name, "name_zh": name.replace(" Berhad", "").replace(" Bhd", ""),
                           "stock_code": None, "facts": {}, "use_of_proceeds": [], "financials": [],
                           "sources": {}, "auto_created": TODAY,
                           "todo_official": "自动收录，资料待人工核实；请补上 Bursa 公告与招股书链接。"}
                    records[slug] = rec
                    by_name[name.lower()] = rec
                    log.append(f"新收录：{name}")
                title_m = re.search(r"<title>(.*?)</title>", html, re.S | re.I)
                sid = add_source(rec, url, title_m.group(1).strip() if title_m else None)
                if merge_facts(rec, sid, ex, log):
                    rec["_dirty"] = True

        for rec in records.values():
            a = rec.get("analysis") or {}
            dirty = rec.pop("_dirty", False)
            if not a.get("reviewed") and (dirty or not a):
                result = ai.analyse(rec)
                if result:
                    d = result.model_dump()
                    rec["one_liner"] = d.pop("one_liner")
                    rec["sector_zh"] = d.pop("sector_zh")
                    rec["analysis"] = {"generated_by": "ai", "model": ai.MODEL, "generated_at": TODAY,
                                       "reviewed": False, "based_on": list(rec["sources"].keys()), **d}
                    log.append(f"{rec['name']}: 已更新商业模式解读")
            save(rec)

    STATE.write_text(json.dumps(state, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    if log:
        cl = json.loads(CHANGELOG.read_text(encoding="utf-8")) if CHANGELOG.exists() else []
        cl.insert(0, {"date": TODAY, "changes": log})
        CHANGELOG.write_text(json.dumps(cl[:200], ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print("\n".join(log) or "没有变更")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
