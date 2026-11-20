"""在 Zo Computer（或任何一台一直开着的电脑/服务器）上跑整个网站。

一个程序做三件事：
  1. 开网站（静态文件，默认 8080 端口，可用 PORT 改）
  2. 每天早上 9:00（马来西亚时间）自动找新 IPO 资料
  3. 每小时检查后台有没有新上传的招股书
每次资料有变，就重新生成网站。

用法：python scripts/zo_run.py
设定放在专案根目录的 .env（参考 deploy/zo/env.example）。
"""
from __future__ import annotations

import datetime as dt
import functools
import hashlib
import http.server
import os
import shutil
import subprocess
import sys
import threading
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SITE = ROOT / "dist"
MYT = dt.timezone(dt.timedelta(hours=8))
PY = sys.executable


def load_env() -> None:
    f = ROOT / ".env"
    if not f.exists():
        return
    for line in f.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            k, v = line.split("=", 1)
            os.environ.setdefault(k.strip(), v.strip().strip('"').strip("'"))


def log(msg: str) -> None:
    print(f"[{dt.datetime.now(MYT):%Y-%m-%d %H:%M}] {msg}", flush=True)


def run(script: str) -> None:
    r = subprocess.run([PY, str(ROOT / "scripts" / script)], cwd=ROOT, capture_output=True, text=True, timeout=3600)
    out = (r.stdout + r.stderr).strip()
    log(f"{script} → {'OK' if r.returncode == 0 else '出错 ' + str(r.returncode)}" + (f"\n{out[-1500:]}" if out else ""))


def data_hash() -> str:
    h = hashlib.sha1()
    for f in sorted(p for p in (ROOT / "data").rglob("*.json") if not p.name.startswith("_")):
        h.update(f.name.encode()); h.update(f.read_bytes())
    return h.hexdigest()


def rebuild() -> None:
    """先生成到 dist.new，成功了才换上去，访客不会看到半成品。"""
    new, old = ROOT / "dist.new", ROOT / "dist.old"
    shutil.rmtree(new, ignore_errors=True)
    r = subprocess.run([PY, str(ROOT / "scripts" / "build.py")], cwd=ROOT, env={**os.environ, "IPO_DIST": str(new)},
                       capture_output=True, text=True)
    if r.returncode != 0:
        log("生成网站失败：\n" + (r.stdout + r.stderr)[-1500:])
        return
    shutil.rmtree(old, ignore_errors=True)
    if SITE.exists():
        SITE.rename(old)
    new.rename(SITE)
    shutil.rmtree(old, ignore_errors=True)
    log(r.stdout.strip())
    run("publish_premium.py")


class Handler(http.server.SimpleHTTPRequestHandler):
    def translate_path(self, path):  # 每次请求都重新指向 dist（重建后也能读到新文件）
        self.directory = str(SITE)
        return super().translate_path(path)

    def log_message(self, *a):  # 不把每个访客都印出来
        pass


def serve(port: int) -> None:
    srv = http.server.ThreadingHTTPServer(("0.0.0.0", port), functools.partial(Handler, directory=str(SITE)))
    log(f"网站已开：http://0.0.0.0:{port}")
    srv.serve_forever()


def main() -> None:
    load_env()
    rebuild()
    threading.Thread(target=serve, args=(int(os.environ.get("PORT", "8080")),), daemon=True).start()
    stamp = ROOT / "data" / "_zo_last_daily.txt"  # 重启也不会同一天跑两次
    last_daily = dt.date.fromisoformat(stamp.read_text().strip()) if stamp.exists() else None
    last_hourly = None
    while True:
        now = dt.datetime.now(MYT)
        before = data_hash()
        if now.hour >= 9 and last_daily != now.date():
            last_daily = now.date()
            stamp.write_text(last_daily.isoformat())
            log("每日更新开始")
            run("update.py")
        hour_key = now.strftime("%Y-%m-%d %H")
        if last_hourly != hour_key:
            last_hourly = hour_key
            run("pull_prospectus.py")
        if data_hash() != before:
            log("资料有变，重新生成网站")
            rebuild()
        time.sleep(60)


if __name__ == "__main__":
    main()
