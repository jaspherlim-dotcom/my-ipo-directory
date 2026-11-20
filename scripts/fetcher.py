"""礼貌抓取：先查 robots.txt，限速，带清楚的 User-Agent，失败不崩溃。"""
from __future__ import annotations

import time
import urllib.robotparser
from urllib.parse import urlparse

import requests

USER_AGENT = "MY-IPO-Directory-Bot/1.0 (+https://github.com/; non-commercial research, respects robots.txt)"
MIN_DELAY_SECONDS = 3.0

_robots: dict[str, urllib.robotparser.RobotFileParser | None] = {}
_last_hit: dict[str, float] = {}


def _robots_for(url: str) -> urllib.robotparser.RobotFileParser | None:
    host = urlparse(url).scheme + "://" + urlparse(url).netloc
    if host not in _robots:
        rp = urllib.robotparser.RobotFileParser()
        try:
            r = requests.get(host + "/robots.txt", headers={"User-Agent": USER_AGENT}, timeout=20)
            if r.status_code >= 400:
                # 没有 robots.txt（404）= 未设限制；被挡（401/403）= 保守起见当作不允许
                rp.parse([] if r.status_code == 404 else ["User-agent: *", "Disallow: /"])
            else:
                rp.parse(r.text.splitlines())
        except requests.RequestException:
            rp = None  # 连 robots 都拿不到，就不抓
        _robots[host] = rp
    return _robots[host]


def allowed(url: str) -> bool:
    rp = _robots_for(url)
    return bool(rp and rp.can_fetch(USER_AGENT, url))


def fetch(url: str) -> tuple[str | None, str]:
    """返回 (文本, 状态说明)。不允许或失败时文本为 None。"""
    if not allowed(url):
        return None, "robots_disallowed_or_unreachable"
    host = urlparse(url).netloc
    wait = MIN_DELAY_SECONDS - (time.time() - _last_hit.get(host, 0))
    if wait > 0:
        time.sleep(wait)
    _last_hit[host] = time.time()
    try:
        r = requests.get(url, headers={"User-Agent": USER_AGENT}, timeout=30)
    except requests.RequestException as e:
        return None, f"error:{type(e).__name__}"
    if r.status_code != 200:
        return None, f"http_{r.status_code}"
    return r.text, "ok"


def html_to_text(html: str) -> str:
    from bs4 import BeautifulSoup

    soup = BeautifulSoup(html, "html.parser")
    for tag in soup(["script", "style", "nav", "footer", "header", "aside", "form", "noscript"]):
        tag.decompose()
    text = soup.get_text("\n")
    lines = [ln.strip() for ln in text.splitlines()]
    return "\n".join(ln for ln in lines if ln)
