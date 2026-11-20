"""读招股书 PDF → 抽事实（附页码与原文引句）→ 更新 data/ipos/<slug>.json → 重写 9 宫格。

用法：
  python scripts/ingest_prospectus.py prospectus/sca-solutions.pdf [--slug sca-solutions] [--url <Bursa 招股书链接>]
  python scripts/ingest_prospectus.py --all      # 处理 prospectus/ 里所有还没处理过的 PDF（GitHub Actions 用）

原则：
- 每个数字都要附“第几页 + 原文引句”，程序会核对引句真的在那一页（容许前后一页），对不上就丢掉。
- 招股书是官方文件：跟新闻冲突时以招股书为准，旧数字留在备注里。
- 招股书内容只摘录事实与页码，不把整份 PDF 放上网站。
"""
from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import re
import sys
from pathlib import Path
from typing import Literal, Optional

from pydantic import BaseModel, Field

sys.path.insert(0, str(Path(__file__).parent))
import ai  # noqa: E402
from update import IPO_DIR, NUMERIC, coerce, number_matches_evidence, slugify  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
PDF_DIR = ROOT / "prospectus"
STATE = ROOT / "data" / "_prospectus_state.json"
TODAY = dt.date.today().isoformat()

KEYWORDS = [
    "utilisation of proceeds", "price-to-earnings", "pe multiple", "shariah", "balloting", "closing date",
    "opening of the application", "listing on the ace market", "listing on the main market", "underwriter",
    "issuing house", "principal adviser", "revenue", "profit after tax", "pat margin", "gross profit",
    "bumiputera investors approved by miti", "market capitalisation", "enlarged share capital",
    "business overview", "principal activities", "major customers", "major suppliers", "risk factors",
    "dividend policy", "competitive strengths", "future plans",
]
MAX_PAGES = 140


# ---------- 读 PDF ----------

def read_pages(pdf: Path) -> list[str]:
    from pypdf import PdfReader

    return [(p.extract_text() or "") for p in PdfReader(str(pdf)).pages]


def pick_pages(pages: list[str]) -> list[int]:
    """前 45 页（封面、摘要、重要日期）+ 含关键词的页，最多 MAX_PAGES 页。"""
    chosen = list(range(min(45, len(pages))))
    scored = []
    for i, t in enumerate(pages):
        if i in chosen:
            continue
        low = t.lower()
        score = sum(low.count(k) for k in KEYWORDS)
        if score:
            scored.append((score, i))
    for _, i in sorted(scored, reverse=True):
        if len(chosen) >= MAX_PAGES:
            break
        chosen.append(i)
    return sorted(chosen)


def _norm(s: str) -> str:
    return re.sub(r"[^0-9a-z.%]+", "", s.lower())


def quote_on_page(quote: str, page: int, pages: list[str]) -> bool:
    q = _norm(quote)
    if len(q) < 6:
        return False
    for p in (page - 1, page, page - 2):  # 模型给的是 1 起算页码；容许前后一页
        if 0 <= p < len(pages) and q in _norm(pages[p]):
            return True
    return False


# ---------- AI 抽取 ----------

class PFact(BaseModel):
    key: Literal[
        "market", "issue_price_rm", "new_shares", "ofs_shares", "proceeds_rm", "market_cap_rm",
        "enlarged_shares", "prospectus_date", "app_open", "app_close", "ballot_date", "listing_date",
        "adviser", "issuing_house", "shariah", "miti_allocation", "pe_ratio", "stock_code",
    ]
    value: str = Field(description="数字用纯数字（RM 换成令吉整数，如 RM31.92 million -> 31920000；价钱 0.28）；日期 YYYY-MM-DD；文字用简体中文")
    page: int = Field(description="PDF 的第几页（从 1 开始数，以 <page n=...> 标签为准）")
    quote: str = Field(description="该页逐字复制的英文原句（10-200 字符）")


class PMoney(BaseModel):
    item: str = Field(description="简体中文")
    rm: float
    page: int
    quote: str


class PFin(BaseModel):
    label: str = Field(description="收入 / 毛利 / 税前盈利 / 税后盈利 等（简体中文）")
    period: str = Field(description="例如 FYE 2025、FPE 30 June 2026")
    rm: float
    page: int
    quote: str


class PRisk(BaseModel):
    title: str
    detail: str = Field(description="简体中文，一两句白话")
    page: int


class Prospectus(BaseModel):
    company_name: str
    business_zh: str = Field(description="简体中文：做什么、怎样赚钱、主要客户与市场、地点。只写招股书写的。")
    business_page: int
    facts: list[PFact]
    use_of_proceeds: list[PMoney]
    financials: list[PFin] = Field(description="最近 3 个财政年及最新财政期的收入、毛利、税后盈利")
    risks: list[PRisk] = Field(description="招股书风险因素中最重要的 5-8 项")


PROMPT = """下面是一份马来西亚 Bursa IPO 招股书的部分页面（每页用 <page n=…> 标示页码）。
请只抽取**明确写出**的资料，不推算、不补常识。每个数字附上页码和该页的逐字英文原句。
重点：发行价、新股与献售股数、募资额与用途、IPO 市值与扩大后股本、重要日期（开放/截止认购、抽签、上市）、
主要顾问、发行行（Issuing House）、伊斯兰合规（Shariah）、MITI 土著配额、IPO 价对应的市盈率（PE），
以及最近几个财政年的收入、毛利、税后盈利。

{pages}"""


def extract(pages: list[str]) -> Prospectus | None:
    chosen = pick_pages(pages)
    text = "\n".join(f"<page n={i + 1}>\n{pages[i][:6000]}\n</page>" for i in chosen)
    client = ai._client()
    with client.messages.stream(
        model=ai.MODEL, max_tokens=32000,
        messages=[{"role": "user", "content": PROMPT.format(pages=text)}],
        output_format=Prospectus,
    ) as stream:
        resp = stream.get_final_message()
    if resp.stop_reason == "refusal":
        return None
    out = getattr(resp, "parsed_output", None)
    if out is None:  # 旧版 SDK：自己解析
        raw = "".join(b.text for b in resp.content if getattr(b, "type", "") == "text")
        out = Prospectus.model_validate_json(raw)
    return out


# ---------- 合并 ----------

def merge(rec: dict, p: Prospectus, pages: list[str], sid: str, log: list[str]) -> None:
    dropped = 0
    for f in p.facts:
        val = coerce(f.key, f.value)
        if val is None or not quote_on_page(f.quote, f.page, pages):
            dropped += 1
            continue
        if f.key in NUMERIC and not number_matches_evidence(val, f.quote):
            dropped += 1
            continue
        new = {"v": val, "src": [sid], "page": f.page, "evidence": f.quote}
        cur = rec["facts"].get(f.key)
        if cur and cur.get("v") != val:
            new["note"] = f"招股书数字；新闻/其他来源原写 {cur.get('v')}"
            log.append(f"{rec['name']}: {f.key} 以招股书为准 {cur.get('v')} → {val}")
        elif cur:
            new["src"] = list(dict.fromkeys([sid] + cur.get("src", [])))
            if cur.get("note"):
                new["note"] = cur["note"]
        rec["facts"][f.key] = new

    # 业务描述是摘要，不做逐字核对，但附页码
    rec["facts"]["business"] = {"v": p.business_zh, "src": [sid], "page": p.business_page}

    uop = [u for u in p.use_of_proceeds if quote_on_page(u.quote, u.page, pages)]
    if uop:
        rec["use_of_proceeds"] = [{"item": u.item, "rm": u.rm, "src": [sid], "page": u.page} for u in uop]
    fins = [x for x in p.financials if quote_on_page(x.quote, x.page, pages) and number_matches_evidence(x.rm, x.quote)]
    if fins:
        rec["financials"] = [{"label": x.label, "period": x.period, "rm": x.rm, "src": [sid], "page": x.page} for x in fins]
    rec["prospectus_risks"] = [{"title": r.title, "detail": r.detail, "page": r.page} for r in p.risks]
    dropped += (len(p.use_of_proceeds) - len(uop)) + (len(p.financials) - len(fins))
    log.append(f"{rec['name']}: 招股书收录 {len(p.facts) + len(p.use_of_proceeds) + len(p.financials) - dropped} 项，核对不到原文而丢弃 {dropped} 项")


def match_existing(key: str) -> str | None:
    """公司名对现有资料：完全一样最好；否则第一个字相同、且一边的字全包含在另一边（YES Group ↔ Yes Group Management）。"""
    want = key.split("-")
    loose = []
    for f in IPO_DIR.glob("*.json"):
        name_key = slugify(json.loads(f.read_text(encoding="utf-8")).get("name", ""))
        if key in (f.stem, name_key):
            return f.stem
        for k in (f.stem, name_key):
            have = k.split("-")
            if have[0] == want[0] and (set(have) <= set(want) or set(want) <= set(have)):
                loose.append(f.stem)
                break
    return loose[0] if len(loose) == 1 else None  # 多过一个可能就不猜


def ingest(pdf: Path, slug: str | None, url: str | None, log: list[str]) -> str | None:
    pages = read_pages(pdf)
    if sum(len(t) for t in pages) < 2000:
        log.append(f"{pdf.name}: 读不到文字（可能是扫描图片版 PDF），跳过")
        return None
    p = extract(pages)
    if p is None:
        log.append(f"{pdf.name}: AI 无法处理，跳过")
        return None
    if not slug:  # 先按公司名找现有资料，找不到才开新的
        key = slugify(p.company_name)
        slug = match_existing(key)
        if slug:
            log.append(f"{p.company_name}: 对应到现有资料 {slug}")
        slug = slug or (slugify(pdf.stem) if pdf.stem != "prospectus" else key)
    path = IPO_DIR / f"{slug}.json"
    rec = json.loads(path.read_text(encoding="utf-8")) if path.exists() else {
        "slug": slug, "name": p.company_name, "name_zh": p.company_name.replace(" Berhad", "").replace(" Bhd", ""),
        "stock_code": None, "facts": {}, "use_of_proceeds": [], "financials": [], "sources": {}}
    sid = next((k for k, s in rec["sources"].items() if s.get("kind") == "prospectus"), f"s{len(rec['sources']) + 1}")
    rec["sources"][sid] = {"title": f"{p.company_name} 招股书（Prospectus）", "publisher": "公司招股书",
                           "kind": "prospectus", "date": None, "url": url or "", "accessed": TODAY}
    merge(rec, p, pages, sid, log)
    rec["todo_official"] = None if url else "招股书资料已收录；请补上 Bursa 招股书链接，方便读者核对。"

    if ai.available() and not (rec.get("analysis") or {}).get("reviewed"):
        a = ai.analyse(rec)
        if a:
            d = a.model_dump()
            rec["one_liner"], rec["sector_zh"] = d.pop("one_liner"), d.pop("sector_zh")
            rec["analysis"] = {"generated_by": "ai", "model": ai.MODEL, "generated_at": TODAY, "reviewed": False,
                               "based_on": list(rec["sources"].keys()), **d}
            log.append(f"{rec['name']}: 已用招股书资料重写 9 宫格")
    path.write_text(json.dumps(rec, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return slug


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("pdf", nargs="?")
    ap.add_argument("--slug")
    ap.add_argument("--url")
    ap.add_argument("--all", action="store_true")
    a = ap.parse_args()
    if not ai.available():
        print("需要 ANTHROPIC_API_KEY 才能读招股书。")
        return 0 if a.all else 1
    state = json.loads(STATE.read_text(encoding="utf-8")) if STATE.exists() else {}
    log: list[str] = []
    if a.all:
        links = json.loads((PDF_DIR / "links.json").read_text(encoding="utf-8")) if (PDF_DIR / "links.json").exists() else {}
        for pdf in sorted(PDF_DIR.glob("*.pdf")):
            h = hashlib.sha1(pdf.read_bytes()).hexdigest()
            if state.get(pdf.name) == h:
                continue
            if ingest(pdf, None, links.get(pdf.stem), log):
                state[pdf.name] = h
    else:
        ingest(Path(a.pdf), a.slug, a.url, log)
    STATE.write_text(json.dumps(state, indent=1) + "\n", encoding="utf-8")
    if log:
        cl_p = ROOT / "data" / "changelog.json"
        cl = json.loads(cl_p.read_text(encoding="utf-8")) if cl_p.exists() else []
        cl.insert(0, {"date": TODAY, "changes": log})
        cl_p.write_text(json.dumps(cl[:200], ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print("\n".join(log) or "没有新的招股书")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
