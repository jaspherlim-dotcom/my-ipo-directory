# 在 Zo Computer 上线（约 10 分钟）

Zo 上只需要开**一个服务**。它会开网站、每天 9:00 找新 IPO 资料、每小时处理后台上传的招股书，资料有变就重新生成网站。
不用 Zo 的 Automations：那个每跑一次都花 Zo 的 AI 额度。我们的程序直接用你自己的 Anthropic API key，更便宜，结果也固定。

## 1. 把程序放上 Zo
下载 `ipo-directory-zo.zip`，在 Zo 里上传（拖进 Files 或聊天框都可以）。

## 2. 把下面整段贴给 Zo 的 AI

```
我上传了 ipo-directory-zo.zip。请帮我：
1. 解压到 /home/workspace/ipo-directory
2. 在那个文件夹执行：pip install -r requirements.txt
3. 把 deploy/zo/env.example 复制成 /home/workspace/ipo-directory/.env（先不用填）
4. 开一个 Service：
   - Label: ipo-site
   - Type: http
   - Local port: 8080
   - Entrypoint: python3 scripts/zo_run.py
   - Working directory: /home/workspace/ipo-directory
   设成公开（public），然后告诉我公开网址。
5. 打开那个网址，确认首页有 15 家 IPO。
```

## 3. 之后补上钥匙（不急，网站没钥匙也能开）
在 Zo 打开 `/home/workspace/ipo-directory/.env`，填：
- `ANTHROPIC_API_KEY`：有了才会自动找新 IPO、读招股书
- `SUPABASE_URL`、`SUPABASE_SERVICE_ROLE_KEY`：有了会员登入和后台上传才会动

填完叫 Zo「重启 ipo-site 服务」。钥匙只放在 Zo 的 .env，不要贴到聊天里。

## 4. 会员系统要改的一个地方
Supabase → Authentication → URL Configuration → Site URL：填 Zo 给你的公开网址。
`config.json` 里的 `supabase_url`、`supabase_anon_key` 照 README 填。

## 5. 想用自己的网址
Zo 支持把自己的域名指向公开服务（Zo 设置里的 Custom domains）。

## 看运行纪录
叫 Zo「给我看 ipo-site 服务最近的 log」。每次更新都会写一行时间和结果。
