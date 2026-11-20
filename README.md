# 马股 IPO 观察站

中文的 Bursa Malaysia IPO 资料库：每个数字附来源，每家公司有加强版商业模式 9 宫格，每天自动更新。

## 它怎样运作

```
GitHub Actions（每天早上 9 点）
  └─ scripts/update.py
       1. 用 Claude 网络搜索找新 IPO 和新资料链接
       2. 先查 robots.txt，再礼貌抓原文（每站间隔 3 秒）
       3. AI 抽取事实，每项必须附原文引句；程序核对引句和数字，对不上就丢
       4. 只补空白字段；跟现有资料冲突就标“待人工核实”，不自动覆盖
       5. 资料有变时重写 9 宫格解读（标记 reviewed 的不动）
  └─ scripts/build.py → dist/（纯静态网站）
  └─ 发布到 GitHub Pages（免费）
```

## 资料结构

每家公司一个文件：`data/ipos/<slug>.json`

- `facts`：每项 `{"v": 值, "src": ["s1"], "note": "..."}`，`src` 对应 `sources` 里的来源。
- `sources`：`kind` 分为 `official`（Bursa/SC/招股书）、`press_release`、`news`、`aggregator`。
- `analysis`：AI 解读，`bmc` 9 格每格都有 `basis`：`fact` / `inference` / `unknown`。
- 人工看过、确认没问题的解读，把 `analysis.reviewed` 改成 `true`，以后自动更新就不会改写它。

## 第一次设置（约 10 分钟）

1. 在 GitHub 开一个新仓库，把整个文件夹推上去。
2. 仓库 **Settings → Pages**，Source 选 **GitHub Actions**。
3. 仓库 **Settings → Secrets and variables → Actions**，新增 `ANTHROPIC_API_KEY`（没有的话网站照样能跑，只是不会自动发现新 IPO）。
4. 到 **Actions** 页面，手动按一次 “Run workflow”。

## 本地预览

```bash
pip install -r requirements.txt
python scripts/build.py
cd dist && python -m http.server 8000   # 打开 http://localhost:8000
```

## 成本

- GitHub Pages + Actions：公开仓库免费。
- Claude API：每天一次发现 + 少量抽取和解读，预计每月几美元到十几美元，视新 IPO 数量而定。可用环境变量 `IPO_MODEL` 换模型。

## 原则

- 不编造数字：事实层只收原文明确写出的资料。
- 优先官方来源；第三方整理网站只作交叉参考。
- 遵守 robots.txt，不抓不允许的网站。
- 网站内容不构成投资建议。

## 会员系统（免费 4 家 + 登入解锁）

架构：公开网站只放免费的几家；其余公司的完整内容在 build 时生成到 `premium_out/`，由 GitHub Actions 上传到 Supabase 的 `premium_pages` 表。数据库规则（RLS）只让合格会员读取，所以别人看网页源码也拿不到。

- `config.json → membership`：`free_count`（免费几家，默认列表最前面 4 家）、`free_slugs`（想指定哪几家免费就填 slug）、`require_payment`（false = 只要免费注册登入；true = 要付费会员）。
- 登入方式：电邮登入链接（Supabase Auth），不用密码。

### 设置步骤
1. 到 supabase.com 开免费项目，在 SQL Editor 执行 `supabase/schema.sql`。
2. Authentication → URL Configuration：Site URL 填网站网址。
3. 把 Project URL 和 anon key 填进 `config.json` 的 `supabase_url`、`supabase_anon_key`（这两个本来就是公开的）。
4. GitHub 仓库 Secrets 加：`SUPABASE_URL`、`SUPABASE_SERVICE_ROLE_KEY`（service key 绝对不能放进网页）。

### 以后开始收费（Stripe）
1. Stripe 建两个订阅价格（月费、年费），各开一个 Payment Link，填进 `payment_link_monthly / yearly`。
2. 部署 webhook：`supabase functions deploy stripe-webhook --no-verify-jwt`，设 secrets `STRIPE_SECRET_KEY`、`STRIPE_WEBHOOK_SECRET`；在 Stripe 把 webhook 指向该函数网址，事件选 `checkout.session.completed`、`customer.subscription.updated`、`customer.subscription.deleted`。
3. Supabase 执行：`update public.site_settings set value = 'true' where key = 'require_payment';`，并把 `config.json` 的 `require_payment` 改成 `true`。
