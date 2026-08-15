/* 沉陷区的地质记忆 · 门户交互
   - 导航栏滚动变实
   - Hero 视差
   - IntersectionObserver 入场动画
   - 数据数字滚动
*/
(function () {
  "use strict";

  var reduceMotion = window.matchMedia &&
    window.matchMedia("(prefers-reduced-motion: reduce)").matches;

  /* 导航栏 */
  var nav = document.getElementById("nav");
  function onScroll() {
    if (window.scrollY > 40) nav.classList.add("scrolled");
    else nav.classList.remove("scrolled");
  }
  window.addEventListener("scroll", onScroll, { passive: true });
  onScroll();

  /* Hero 视差（仅桌面端；移动端图文分离布局不需要） */
  var heroBg = document.getElementById("heroBg");
  if (!reduceMotion && heroBg) {
    window.addEventListener("scroll", function () {
      if (window.innerWidth <= 860) { heroBg.style.transform = "none"; return; }
      var y = window.scrollY;
      if (y < window.innerHeight * 1.2) {
        heroBg.style.transform = "translateY(" + y * 0.28 + "px)";
      }
    }, { passive: true });
  }

  /* 数字滚动 */
  function animateNum(el) {
    var target = parseFloat(el.getAttribute("data-count"));
    var dec = parseInt(el.getAttribute("data-dec") || "0", 10);
    var small = el.querySelector("small");
    var suffix = small ? small.outerHTML : "";
    if (reduceMotion) { el.innerHTML = target.toFixed(dec) + suffix; return; }
    var start = null, dur = 1600;
    function step(ts) {
      if (!start) start = ts;
      var p = Math.min((ts - start) / dur, 1);
      var eased = 1 - Math.pow(1 - p, 3);
      el.innerHTML = (target * eased).toFixed(dec) + suffix;
      if (p < 1) requestAnimationFrame(step);
      else el.innerHTML = target.toFixed(dec) + suffix;
    }
    requestAnimationFrame(step);
  }

  /* 入场动画 + 触发数字滚动 */
  var numsDone = new WeakSet();
  var io = new IntersectionObserver(function (entries) {
    entries.forEach(function (e) {
      if (!e.isIntersecting) return;
      e.target.classList.add("in");
      e.target.querySelectorAll(".num[data-count]").forEach(function (n) {
        if (!numsDone.has(n)) { numsDone.add(n); animateNum(n); }
      });
      io.unobserve(e.target);
    });
  }, { threshold: 0.12 });
  document.querySelectorAll(".reveal").forEach(function (el) { io.observe(el); });
})();
