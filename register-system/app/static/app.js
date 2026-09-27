(function () {
  "use strict";

  // Confirmation prompts for forms marked data-confirm (inline handlers are blocked by the CSP).
  document.querySelectorAll("form[data-confirm]").forEach(function (form) {
    form.addEventListener("submit", function (e) {
      if (!window.confirm(form.getAttribute("data-confirm"))) e.preventDefault();
    });
  });

  document.querySelectorAll("[data-print]").forEach(function (btn) {
    btn.addEventListener("click", function () { window.print(); });
  });

  // Register: show "minutes late" only when Late is selected.
  function syncLate(row) {
    var late = row.querySelector('input[type=radio][value="late"]');
    var box = row.querySelector(".late-mins");
    if (late && box) box.classList.toggle("show", late.checked);
  }
  var form = document.getElementById("register-form");
  if (form) {
    form.querySelectorAll("tbody tr").forEach(function (row) {
      syncLate(row);
      row.addEventListener("change", function () { syncLate(row); });
    });
    var markAll = form.querySelector("[data-mark-all]");
    if (markAll) {
      markAll.addEventListener("click", function () {
        form.querySelectorAll("tbody tr").forEach(function (row) {
          if (!row.querySelector("input[type=radio]:checked")) {
            var r = row.querySelector('input[type=radio][value="' + markAll.getAttribute("data-mark-all") + '"]');
            if (r) r.checked = true;
          }
          syncLate(row);
        });
      });
    }
    var dirty = false;
    form.addEventListener("change", function () { dirty = true; });
    form.addEventListener("submit", function () { dirty = false; });
    window.addEventListener("beforeunload", function (e) { if (dirty) { e.preventDefault(); e.returnValue = ""; } });
  }

  // Countdown to the pastoral alert, using server time to avoid client clock drift.
  var timer = document.querySelector(".pastoral-timer:not(.done)");
  if (timer) {
    var due = Date.parse(timer.getAttribute("data-due"));
    var offset = Date.parse(timer.getAttribute("data-now")) - Date.now();
    var out = timer.querySelector(".countdown");
    var tick = function () {
      var left = Math.round((due - (Date.now() + offset)) / 1000);
      if (!out) return;
      if (left <= 0) { out.textContent = "Alert time reached – absentees are being sent to Pastoral Support."; return; }
      var m = Math.floor(left / 60), s = left % 60;
      out.textContent = "(" + m + "m " + (s < 10 ? "0" : "") + s + "s left)";
      setTimeout(tick, 1000);
    };
    tick();
  }
})();
