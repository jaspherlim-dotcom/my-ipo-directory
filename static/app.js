(function () {
  var cards = Array.prototype.slice.call(document.querySelectorAll(".card"));
  if (!cards.length) return;
  var state = { status: "all", market: "all", q: "" };
  var empty = document.querySelector(".empty");

  function apply() {
    var shown = 0;
    cards.forEach(function (c) {
      var ok = (state.status === "all" || c.dataset.status === state.status) &&
               (state.market === "all" || c.dataset.market === state.market) &&
               (!state.q || c.dataset.q.indexOf(state.q) !== -1);
      c.hidden = !ok;
      if (ok) shown++;
    });
    if (empty) empty.hidden = shown !== 0;
  }

  document.querySelectorAll(".chips").forEach(function (group) {
    group.addEventListener("click", function (e) {
      var b = e.target.closest(".chip");
      if (!b) return;
      group.querySelectorAll(".chip").forEach(function (x) { x.classList.remove("on"); });
      b.classList.add("on");
      state[group.dataset.filter] = b.dataset.v;
      apply();
    });
  });
  var s = document.querySelector(".search");
  if (s) s.addEventListener("input", function () { state.q = s.value.trim().toLowerCase(); apply(); });
})();
