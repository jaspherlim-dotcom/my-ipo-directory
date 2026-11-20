(function () {
  var $ = function (q) { return document.querySelector(q); };
  var $$ = function (q) { return Array.prototype.slice.call(document.querySelectorAll(q)); };
  var params = new URLSearchParams(location.search);
  var search = $(".searchbar .search");

  // 底部导航中间的搜索键：首页就直接聚焦搜索框
  $$("[data-focus-search]").forEach(function (a) {
    a.addEventListener("click", function (e) {
      if (search && $(".cards")) { e.preventDefault(); window.scrollTo({ top: 0, behavior: "smooth" }); search.focus(); }
    });
  });

  var cards = $$(".card");
  if (!cards.length) return;
  var state = { status: params.get("s") || "all", market: params.get("m") || "all", shariah: params.get("h") || "all", q: (params.get("q") || "").toLowerCase() };
  var empty = $(".empty");

  function syncChips() {
    $$(".chips").forEach(function (g) {
      g.querySelectorAll(".chip").forEach(function (b) { b.classList.toggle("on", b.dataset.v === state[g.dataset.filter]); });
    });
  }
  function apply() {
    var shown = 0;
    cards.forEach(function (c) {
      var ok = (state.status === "all" || c.dataset.status === state.status) &&
               (state.market === "all" || c.dataset.market === state.market) &&
               (state.shariah === "all" || c.dataset.shariah === state.shariah) &&
               (!state.q || c.dataset.q.indexOf(state.q) !== -1);
      c.hidden = !ok;
      if (ok) shown++;
    });
    if (empty) empty.hidden = shown !== 0;
    syncChips();
  }
  function goList() { var a = $("#all"); if (a) a.scrollIntoView({ behavior: "smooth", block: "start" }); }

  $$(".chips").forEach(function (group) {
    group.addEventListener("click", function (e) {
      var b = e.target.closest(".chip");
      if (!b) return;
      state[group.dataset.filter] = b.dataset.v;
      apply();
    });
  });
  $$(".sc[data-set-status], .sc[data-set-market], .sc[data-set-shariah]").forEach(function (b) {
    b.addEventListener("click", function () {
      state = { status: b.dataset.setStatus || "all", market: b.dataset.setMarket || "all", shariah: b.dataset.setShariah || "all", q: "" };
      if (search) search.value = "";
      apply(); goList();
    });
  });
  var reset = $("[data-reset]");
  if (reset) reset.addEventListener("click", function () {
    state = { status: "all", market: "all", shariah: "all", q: "" };
    if (search) search.value = "";
    apply();
  });

  if (search) {
    search.value = params.get("q") || "";
    search.closest("form").addEventListener("submit", function (e) { e.preventDefault(); goList(); });
    search.addEventListener("input", function () {  // 搜索时看全部，不受快捷格筛选影响
      state = { status: "all", market: "all", shariah: "all", q: search.value.trim().toLowerCase() };
      apply();
    });
  }
  apply();

  // 底部提示卡：关掉后这台机不再出现
  var toast = $("[data-toast]");
  if (toast) {
    var seen = false;
    try { seen = localStorage.getItem("ipo-toast-x") === "1"; } catch (e) {}
    if (!seen) setTimeout(function () { toast.hidden = false; }, 900);
    toast.querySelector("[data-toast-x]").addEventListener("click", function () {
      toast.hidden = true;
      try { localStorage.setItem("ipo-toast-x", "1"); } catch (e) {}
    });
  }
})();
