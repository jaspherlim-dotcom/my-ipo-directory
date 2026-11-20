"""把 data/ipos/*.json 生成静态网站到 dist/。"""
from __future__ import annotations

import datetime as dt
import json
import shutil
from pathlib import Path

from jinja2 import Environment, FileSystemLoader, select_autoescape

ROOT = Path(__file__).resolve().parent.parent
DIST = ROOT / "dist"
CONFIG = json.loads((ROOT / "config.json").read_text(encoding="utf-8"))
TODAY = dt.date.today()

FACT_LABELS = {
    "market": "上市市场", "issue_price_rm": "发行价", "market_cap_rm": "IPO 市值", "proceeds_rm": "募资额",
    "new_shares": "新股数量", "ofs_shares": "献售旧股", "enlarged_shares": "扩大后股本",
    "oversub_public": "公众超额认购", "applications": "申请份数", "prospectus_date": "招股书发布",
    "app_open": "开放认购", "app_close": "截止认购", "ballot_date": "抽签日期", "listing_date": "上市日期",
    "first_day_open_rm": "首日开盘价", "first_day_close_rm": "首日收盘价", "yield_pct": "预测收益率",
    "adviser": "主要顾问", "stock_code": "股票代号", "shariah": "伊斯兰合规",
    "issuing_house": "发行行", "miti_allocation": "MITI 土著配额", "pe_ratio": "市盈率（IPO 价）",
}
KEY_ORDER = ["issue_price_rm", "market_cap_rm", "proceeds_rm", "oversub_public", "listing_date",
             "first_day_open_rm", "first_day_close_rm", "yield_pct", "pe_ratio", "shariah", "miti_allocation", "new_shares", "ofs_shares",
             "enlarged_shares", "applications", "issuing_house", "adviser"]
TIMELINE_KEYS = ["prospectus_date", "app_open", "app_close", "ballot_date", "listing_date"]
MARKET_ZH = {"Main": "主板", "ACE": "创业板 ACE", "LEAP": "LEAP 板"}
KIND_ZH = {"official": "官方", "news": "新闻", "press_release": "公司新闻稿", "aggregator": "第三方整理", "prospectus": "招股书"}
BASIS_ZH = {"fact": "事实", "inference": "推论", "unknown": "资料不足"}
BMC_ZH = {
    "key_partners": ("关键伙伴", "谁在帮它？"), "key_activities": ("关键活动", "它每天在忙什么？"),
    "key_resources": ("关键资源", "它靠什么家当？"), "value_propositions": ("价值主张", "客户为什么选它？"),
    "customer_relationships": ("客户关系", "怎样留住客户？"), "channels": ("渠道", "怎样接触客户？"),
    "customer_segments": ("客户群", "卖给谁？"), "cost_structure": ("成本结构", "钱花在哪？"),
    "revenue_streams": ("收入来源", "钱从哪来？"),
}


def ringgit(v) -> str:
    if v is None:
        return "—"
    v = float(v)
    if v >= 1e8:
        return f"RM{v / 1e8 + 1e-9:,.2f}".rstrip("0").rstrip(".") + " 亿"
    if v >= 1e6:
        return f"RM{v / 1e6:,.2f}".rstrip("0").rstrip(".") + " 百万"
    return f"RM{v:,.0f}"


def fmt_fact(key: str, v) -> str:
    if v is None:
        return "—"
    if key in {"issue_price_rm", "first_day_open_rm", "first_day_close_rm"}:
        return f"RM{float(v):.2f}"
    if key in {"market_cap_rm", "proceeds_rm"}:
        return ringgit(v)
    if key in {"new_shares", "ofs_shares", "enlarged_shares"}:
        return f"{float(v) / 1e6:,.2f} 百万股"
    if key == "applications":
        return f"{int(v):,} 份"
    if key == "oversub_public":
        return f"{float(v):g} 倍"
    if key == "yield_pct":
        return f"{float(v):g}%"
    if key == "market":
        return MARKET_ZH.get(v, v)
    if key.endswith("_date") or key in {"app_open", "app_close"}:
        d = dt.date.fromisoformat(v)
        return f"{d.year}年{d.month}月{d.day}日"
    return str(v)


def fv(rec: dict, key: str):
    f = rec["facts"].get(key)
    return f["v"] if f else None


def status_of(rec: dict) -> tuple[str, str]:
    ld, ao, ac = fv(rec, "listing_date"), fv(rec, "app_open"), fv(rec, "app_close")
    today = TODAY.isoformat()
    if ld and ld <= today:
        return "listed", "已上市"
    if ao and ac and ao <= today <= ac:
        return "open", "认购中"
    return "upcoming", "即将上市"


def enrich(rec: dict) -> dict:
    rec["status"], rec["status_zh"] = status_of(rec)
    src_ids = list(rec["sources"].keys())
    rec["src_index"] = {sid: i + 1 for i, sid in enumerate(src_ids)}
    rec["key_facts"] = [(k, FACT_LABELS[k], fmt_fact(k, rec["facts"][k]["v"]), rec["facts"][k])
                        for k in KEY_ORDER if k in rec["facts"]]
    rec["timeline"] = sorted(
        [(rec["facts"][k]["v"], FACT_LABELS[k], fmt_fact(k, rec["facts"][k]["v"]), rec["facts"][k]) for k in TIMELINE_KEYS if k in rec["facts"]],
        key=lambda t: t[0])
    total = sum(u["rm"] for u in rec.get("use_of_proceeds", [])) or 1
    for u in rec.get("use_of_proceeds", []):
        u["pct"] = round(u["rm"] / total * 100, 1)
        u["rm_fmt"] = ringgit(u["rm"])
    ip, op = fv(rec, "issue_price_rm"), fv(rec, "first_day_open_rm")
    rec["first_day_pct"] = round((op - ip) / ip * 100, 2) if ip and op else None
    kinds = {s["kind"] for s in rec["sources"].values()}
    rec["has_official"] = "official" in kinds or "prospectus" in kinds
    return rec


def main() -> None:
    env = Environment(loader=FileSystemLoader(ROOT / "templates"), autoescape=select_autoescape(["html"]))
    env.globals.update(LABELS=FACT_LABELS, cfg=CONFIG, MARKET_ZH=MARKET_ZH, KIND_ZH=KIND_ZH, BASIS_ZH=BASIS_ZH, BMC_ZH=BMC_ZH,
                       built=TODAY.isoformat(), fmt_fact=fmt_fact, fv=fv, ringgit=ringgit)
    recs = [enrich(json.loads(p.read_text(encoding="utf-8"))) for p in sorted((ROOT / "data" / "ipos").glob("*.json"))]
    order = {"open": 0, "upcoming": 1, "listed": 2}
    def sort_key(r):
        ld = int((fv(r, "listing_date") or "9999-12-31").replace("-", ""))
        return (order[r["status"]], -ld if r["status"] == "listed" else ld)

    recs.sort(key=sort_key)

    # 会员制：列表最前面 free_count 家免费，其余锁起来（完整内容只上传到会员后台，不放进公开网站）
    m = CONFIG.get("membership", {})
    free_slugs = set(m.get("free_slugs") or [r["slug"] for r in recs[: m.get("free_count", 4)]]) if m.get("enabled") else {r["slug"] for r in recs}
    for r in recs:
        r["locked"] = r["slug"] not in free_slugs

    changelog_p = ROOT / "data" / "changelog.json"
    changelog = json.loads(changelog_p.read_text(encoding="utf-8")) if changelog_p.exists() else []

    if DIST.exists():
        shutil.rmtree(DIST)
    (DIST / "ipo").mkdir(parents=True)
    shutil.copytree(ROOT / "static", DIST / "static")

    counts = {k: sum(1 for r in recs if r["status"] == k) for k in order}
    (DIST / "index.html").write_text(env.get_template("index.html").render(recs=recs, counts=counts, depth=""), encoding="utf-8")
    (DIST / "about.html").write_text(env.get_template("about.html").render(changelog=changelog, depth=""), encoding="utf-8")
    for name in ("login", "account", "membership"):
        (DIST / f"{name}.html").write_text(env.get_template(f"{name}.html").render(depth=""), encoding="utf-8")
    (DIST / "admin.html").write_text(env.get_template("admin.html").render(records=sorted(recs, key=lambda r: r["name"]), depth=""), encoding="utf-8")
    PREMIUM = ROOT / "premium_out"
    if PREMIUM.exists():
        shutil.rmtree(PREMIUM)
    PREMIUM.mkdir()
    body = env.get_template("_ipo_body.html")
    for r in recs:
        (DIST / "ipo" / f"{r['slug']}.html").write_text(env.get_template("ipo.html").render(r=r, depth="../"), encoding="utf-8")
        if r["locked"]:
            (PREMIUM / f"{r['slug']}.html").write_text(body.render(r=r, depth="../"), encoding="utf-8")
    (DIST / "data.json").write_text(json.dumps([{k: r[k] for k in ("slug", "name", "facts", "sources")} for r in recs if not r["locked"]], ensure_ascii=False), encoding="utf-8")
    (DIST / ".nojekyll").write_text("")
    print(f"已生成 {len(recs)} 家 IPO 页面（免费 {len(recs) - sum(r['locked'] for r in recs)} 家，会员 {sum(r['locked'] for r in recs)} 家）→ {DIST}")


if __name__ == "__main__":
    main()
