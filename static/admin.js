/* 后台上传招股书：只有 admins 名单里的帐号能用（数据库规则把关，不靠这段 JS） */
(function () {
  var S = window.SITE || {};
  var form = document.getElementById("upload-form");
  if (!form) return;
  var msg = document.querySelector("[data-admin-msg]");
  var upMsg = document.querySelector("[data-upload-msg]");
  if (!(S.supabaseUrl && S.supabaseKey && window.supabase)) { msg.textContent = "会员系统尚未接上（目前是预览版）。"; return; }
  var sb = window.supabase.createClient(S.supabaseUrl, S.supabaseKey);
  var STATUS = { pending: "处理中", done: "完成", failed: "失败" };

  function td(text) { var c = document.createElement("td"); c.textContent = text || ""; return c; }

  async function refresh() {
    var r = await sb.from("prospectus_uploads").select("file_name, created_at, status, message, slug")
      .order("created_at", { ascending: false }).limit(20);
    var box = document.getElementById("upload-list");
    var body = box.querySelector("tbody");
    body.innerHTML = "";
    (r.data || []).forEach(function (u) {
      var tr = document.createElement("tr");
      tr.appendChild(td(u.file_name));
      tr.appendChild(td(new Date(u.created_at).toLocaleString("zh-CN")));
      tr.appendChild(td((STATUS[u.status] || u.status) + (u.message ? "：" + u.message : "")));
      body.appendChild(tr);
    });
    box.hidden = !(r.data && r.data.length);
  }

  (async function init() {
    var s = await sb.auth.getSession();
    if (!s.data.session) { location.href = (S.root || "") + "login.html?next=admin.html"; return; }
    var ok = await sb.rpc("is_admin");
    if (ok.error || !ok.data) { msg.textContent = "这个帐号没有后台权限。"; return; }
    msg.textContent = "已登入：" + s.data.session.user.email;
    form.hidden = false;
    refresh();
  })();

  form.addEventListener("submit", async function (e) {
    e.preventDefault();
    var f = document.getElementById("pdf").files[0];
    if (!f) return;
    if (f.type !== "application/pdf") { upMsg.textContent = "只收 PDF 文件。"; return; }
    var btn = form.querySelector("button"); btn.disabled = true;
    upMsg.textContent = "上传中…（" + (f.size / 1048576).toFixed(1) + "MB）";
    var safe = f.name.replace(/[^A-Za-z0-9._-]+/g, "-");
    var path = new Date().toISOString().replace(/[:.]/g, "-") + "-" + safe;
    var up = await sb.storage.from("prospectus").upload(path, f, { contentType: "application/pdf" });
    if (up.error) { upMsg.textContent = "上传失败：" + up.error.message; btn.disabled = false; return; }
    var ins = await sb.from("prospectus_uploads").insert({
      path: path, file_name: f.name,
      bursa_url: document.getElementById("bursa-url").value.trim() || null,
      slug: document.getElementById("slug").value || null,
    });
    btn.disabled = false;
    if (ins.error) { upMsg.textContent = "文件已上传，但登记失败：" + ins.error.message; return; }
    upMsg.textContent = "上传成功，等程序处理（通常 1 小时内）。";
    form.reset();
    refresh();
  });
})();
