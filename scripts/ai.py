"""Claude 相关：发现新 IPO、从原文抽取事实（带原文引句）、生成商业模式解读。

原则：
- 事实只从抓回来的原文里抽，而且每个数字必须附上一段“原文引句”，
  程序会检查引句真的出现在原文里，对不上就丢掉（防止 AI 编数字）。
- 商业模式 9 宫格只能用已核对的事实做依据，并标明每格是「事实 / 推论 / 资料不足」。
"""
from __future__ import annotations

import json
import os
import re
from typing import Literal, Optional

from pydantic import BaseModel, Field

MODEL = os.environ.get("IPO_MODEL", "claude-opus-5-5")


def available() -> bool:
    return bool(os.environ.get("ANTHROPIC_API_KEY"))


def _client():
    import anthropic

    return anthropic.Anthropic()


# ---------- 1. 发现 ----------

DISCOVER_PROMPT = """你在维护一个马来西亚股市（Bursa Malaysia）IPO 资料库。今天是 {today}。
请用网络搜索找出：最近 30 天内发布招股书、开放认购、公布超额认购结果或上市的 Bursa Malaysia IPO（主板 Main、创业板 ACE、LEAP 都算），以及已公布日期的即将上市公司。
优先使用：bursamalaysia.com 公告、sc.com.my、公司官网新闻稿、The Star、The Edge、NST、Bernama、The Sun 等可信媒体。
已收录的公司（仍可附上新的资料链接）：{known}

只输出一个 JSON，放在 <json></json> 标签里，格式：
{{"ipos": [{{"name": "公司英文全名", "market": "Main|ACE|LEAP|unknown", "urls": ["每个公司 1-4 个最相关的原文链接"]}}]}}
不要猜测，没有把握的公司不要列出。"""


def discover(today: str, known: list[str]) -> list[dict]:
    client = _client()
    tools = [{"type": "web_search_20260209", "name": "web_search", "max_uses": 8}]
    messages = [{"role": "user", "content": DISCOVER_PROMPT.format(today=today, known=", ".join(known) or "无")}]
    resp = None
    for _ in range(5):  # 处理 pause_turn
        resp = client.beta.messages.create(
            model=MODEL,
            max_tokens=16000,
            betas=["server-side-fallback-2026-07-01"],
            fallbacks="default",
            tools=tools,
            messages=messages,
        )
        if resp.stop_reason != "pause_turn":
            break
        messages = [messages[0], {"role": "assistant", "content": resp.content}]
    if resp is None or resp.stop_reason == "refusal":
        return []
    text = "".join(b.text for b in resp.content if getattr(b, "type", "") == "text")
    m = re.search(r"<json>(.*?)</json>", text, re.S)
    if not m:
        return []
    try:
        return json.loads(m.group(1)).get("ipos", [])
    except json.JSONDecodeError:
        return []


# ---------- 2. 抽取事实 ----------

class Fact(BaseModel):
    key: Literal[
        "market", "business", "issue_price_rm", "new_shares", "ofs_shares", "proceeds_rm",
        "market_cap_rm", "enlarged_shares", "prospectus_date", "app_open", "app_close",
        "ballot_date", "listing_date", "oversub_public", "applications", "first_day_open_rm",
        "first_day_close_rm", "adviser", "yield_pct", "stock_code",
    ]
    value: str = Field(description="数值用纯数字（RM 换算成令吉整数，例如 RM31.92mil -> 31920000；倍数 36.46；日期 YYYY-MM-DD）；文字用简体中文")
    evidence: str = Field(description="从原文逐字复制的一小段英文/马来文原句（10-200 字符），必须能在原文中找到")
    note: Optional[str] = None


class Extraction(BaseModel):
    company_name: str
    is_bursa_ipo: bool
    facts: list[Fact]


EXTRACT_PROMPT = """下面是一篇关于马来西亚 IPO 的原文（来源：{url}）。
请只抽取原文**明确写出**的事实，不要推算、不要用常识补充。每个事实都要附上原文逐字引句 evidence。
没写的就不要输出该项。

<source>
{text}
</source>"""


def _norm(s: str) -> str:
    return re.sub(r"\s+", " ", s).strip().lower()


def extract(url: str, text: str) -> Extraction | None:
    client = _client()
    resp = client.messages.parse(
        model=MODEL,
        max_tokens=8000,
        messages=[{"role": "user", "content": EXTRACT_PROMPT.format(url=url, text=text[:60000])}],
        output_format=Extraction,
    )
    if resp.stop_reason == "refusal" or resp.parsed_output is None:
        return None
    out: Extraction = resp.parsed_output
    src = _norm(text)
    # 引句核对：对不上原文的事实一律丢弃
    out.facts = [f for f in out.facts if len(f.evidence) >= 8 and _norm(f.evidence) in src]
    return out


# ---------- 3. 商业模式解读 ----------

Basis = Literal["fact", "inference", "unknown"]


class Block(BaseModel):
    text: str
    basis: Basis


class Bmc(BaseModel):
    customer_segments: Block
    value_propositions: Block
    channels: Block
    customer_relationships: Block
    revenue_streams: Block
    key_resources: Block
    key_activities: Block
    key_partners: Block
    cost_structure: Block


class Risk(BaseModel):
    title: str
    detail: str
    basis: Basis


class Analysis(BaseModel):
    one_liner: str
    sector_zh: str
    summary: str
    bmc: Bmc
    moat: str
    money_flow: str
    watch: list[str]
    investor_takeaway: str
    sme_lessons: list[str]
    risks: list[Risk]


ANALYSIS_PROMPT = """你是一位懂生意的马来西亚华人分析师，读者是散户投资者和中小企业老板。
请根据下面【已核对的事实】（JSON），为这家 IPO 写商业模式 9 宫格解读。

要求：
- 简体中文，口语、易懂，可以用马来西亚的例子，但不要夸张、不要喊买卖。
- 只能用下面提供的事实里的数字；绝对不可以自己编造任何数字、客户名或日期。
- 每一格标 basis：fact（直接来自事实）、inference（你的合理推论）、unknown（资料不足，就直说“资料不足”）。
- one_liner：一句话讲它靠什么赚钱。sector_zh：中文行业标签，如“制造 · 天线 OEM”。
- summary：2-3 句，像跟朋友解释。moat：护城河。money_flow：募资拿去做什么、说明什么。
- watch：上市后要追踪的 3-5 个指标。investor_takeaway：给投资者的平衡观点。
- sme_lessons：2-3 条中小企业老板可以学的。risks：3-5 个主要风险。

【已核对的事实】
{facts}"""


def analyse(record: dict) -> Analysis | None:
    client = _client()
    payload = {
        "name": record.get("name"),
        "facts": {k: v.get("v") for k, v in record.get("facts", {}).items()},
        "use_of_proceeds": record.get("use_of_proceeds", []),
        "financials": record.get("financials", []),
    }
    resp = client.messages.parse(
        model=MODEL,
        max_tokens=8000,
        messages=[{"role": "user", "content": ANALYSIS_PROMPT.format(facts=json.dumps(payload, ensure_ascii=False, indent=1))}],
        output_format=Analysis,
    )
    if resp.stop_reason == "refusal":
        return None
    return resp.parsed_output
