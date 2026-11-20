/* 会员系统：Supabase 登入（电邮链接）+ 付费内容解锁 + Stripe 订阅 */
(function () {
  var S = window.SITE || {};
  var root = S.root || "";
  var ready = !!(S.supabaseUrl && S.supabaseKey && window.supabase);
  var sb = ready ? window.supabase.createClient(S.supabaseUrl, S.supabaseKey) : null;
  var $ = function (q) { return document.querySelector(q); };
  var $$ = function (q) { return Array.prototype.slice.call(document.querySelectorAll(q)); };
  var NOT_READY = "会员系统尚未接上（目前是预览版）。";

  function setText(sel, txt) { $$(sel).forEach(function (el) { el.textContent = txt; }); }

  async function getUser() {
    if (!sb) return null;
    var r = await sb.auth.getSession();
    return r.data.session ? r.data.session.user : null;
  }

  async function getMember(user) {
    if (!sb || !user) return null;
    var r = await sb.from("members").select("status, plan, current_period_end").eq("user_id", user.id).maybeSingle();
    return r.data || null;
  }

  function isActive(m) {
    if (!S.requirePayment) return true; // 免费注册阶段：登入即可
    return !!m && (m.status === "active" || m.status === "trialing") &&
      (!m.current_period_end || new Date(m.current_period_end) > new Date());
  }

  function payLink(kind, user) {
    var base = kind === "yearly" ? S.payYearly : S.payMonthly;
    if (!base) return null;
    var u = new URL(base);
    u.searchParams.set("client_reference_id", user.id);
    if (user.email) u.searchParams.set("prefilled_email", user.email);
    return u.toString();
  }

  // 顶部导航：已登入就显示“我的会员”
  async function nav(user) {
    if (!user) return;
    var a = $("[data-auth-link]");
    if (a) { a.classList.add("on"); a.title = "我的会员"; a.href = root + "account.html"; }
    var t = $("[data-auth-tab]");
    if (t) t.href = root + "account.html";
  }

  // 登入页
  function loginPage() {
    var f = $("#login-form");
    if (!f) return;
    f.addEventListener("submit", async function (e) {
      e.preventDefault();
      if (!sb) return setText("[data-login-msg]", NOT_READY);
      var email = $("#email").value.trim();
      var next = new URLSearchParams(location.search).get("next") || "account.html";
      var redirect = new URL(root + next, location.href).toString();
      setText("[data-login-msg]", "寄出中…");
      var r = await sb.auth.signInWithOtp({ email: email, options: { emailRedirectTo: redirect } });
      setText("[data-login-msg]", r.error ? "出错了：" + r.error.message : "登入链接已寄到 " + email + "，请到邮箱点击链接。");
    });
  }

  // 会员页
  async function accountPage(user, member) {
    var box = $("[data-account]");
    if (!box) return;
    if (!sb) { box.innerHTML = "<p class='muted'>" + NOT_READY + "</p>"; return; }
    if (!user) { location.href = root + "login.html?next=account.html"; return; }
    var active = isActive(member);
    var until = member && member.current_period_end ? new Date(member.current_period_end).toLocaleDateString("zh-CN") : null;
    box.innerHTML =
      "<p>登入电邮：<b></b></p>" +
      "<p>会员状态：<b>" + (!S.requirePayment ? "免费会员（可看全部 IPO）" : active ? "有效会员" + (until ? "（到 " + until + "）" : "") : "未订阅") + "</b></p>" +
      (active ? "<p><a class='btn' href='" + root + "index.html'>去看全部 IPO</a></p>"
              : "<p><a class='btn' href='" + root + "membership.html'>订阅会员</a></p>") +
      "<p><button class='btn ghost' data-logout>登出</button></p>";
    box.querySelector("p b").textContent = user.email || "";
    box.querySelector("[data-logout]").addEventListener("click", async function () {
      await sb.auth.signOut(); location.href = root + "index.html";
    });
  }

  // 方案页的订阅按钮
  function membershipPage(user) {
    $$("[data-subscribe]").forEach(function (btn) {
      btn.addEventListener("click", function () {
        if (!sb) return setText("[data-subscribe-msg]", NOT_READY);
        if (!user) { location.href = root + "login.html?next=membership.html"; return; }
        var link = payLink(btn.dataset.subscribe, user);
        if (!link) return setText("[data-subscribe-msg]", "付款链接尚未设定。");
        location.href = link;
      });
    });
  }

  // IPO 详情页：会员就从后台拿完整内容
  async function premiumPage(user, member) {
    var wall = $("#premium");
    if (!wall) return;
    if (!sb) return setText("[data-member-msg]", NOT_READY);
    if (!user) return;
    if (!isActive(member)) {
      var ui = wall.querySelector("[data-member-ui]");
      if (ui) ui.innerHTML = "<a class='btn' href='" + root + "membership.html'>订阅会员解锁</a>";
      return setText("[data-member-msg]", "你已登入，但还不是有效会员。");
    }
    setText("[data-member-msg]", "载入会员内容中…");
    var r = await sb.from("premium_pages").select("html").eq("slug", wall.dataset.slug).maybeSingle();
    if (r.error || !r.data) return setText("[data-member-msg]", "暂时载入不到内容，请稍后再试。");
    var target = wall.querySelector("[data-premium-target]");
    target.innerHTML = r.data.html; // 内容由本站自己生成上传
    target.hidden = false;
    wall.querySelector(".paywall-teaser").hidden = true;
    wall.classList.remove("paywall");
  }

  (async function init() {
    loginPage();
    var user = await getUser();
    var member = await getMember(user);
    nav(user);
    membershipPage(user);
    accountPage(user, member);
    premiumPage(user, member);
  })();
})();
