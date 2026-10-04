// ============================================================
// Sunset Wallet — script.js
// Scroll reveal, animated counters, progress ring/bar fill,
// Chart.js charts, flash auto-dismiss, button ripple, hamburger,
// and a confetti burst used as a "nice job staying under budget"
// celebration cue.
// ============================================================

document.addEventListener("DOMContentLoaded", () => {
  setYear();
  initScrollReveal();
  initHamburger();
  initFlashMessages();
  initRipple();
  initCounters();
  initProgressFills();
  initCategoryChart();
  initSummaryCharts();
});

function setYear() {
  const el = document.getElementById("year");
  if (el) el.textContent = new Date().getFullYear();
}

// ---------------- scroll reveal ----------------
function initScrollReveal() {
  const items = document.querySelectorAll(".reveal");
  if (!items.length) return;

  const observer = new IntersectionObserver(
    (entries) => {
      entries.forEach((entry, i) => {
        if (entry.isIntersecting) {
          setTimeout(() => entry.target.classList.add("in-view"), i * 60);
          observer.unobserve(entry.target);
        }
      });
    },
    { threshold: 0.1 }
  );
  items.forEach((item) => observer.observe(item));
}

// ---------------- hamburger menu ----------------
function initHamburger() {
  const btn = document.getElementById("hamburger");
  const nav = document.getElementById("navLinks");
  if (!btn || !nav) return;
  btn.addEventListener("click", () => nav.classList.toggle("open"));
}

// ---------------- flash messages ----------------
function initFlashMessages() {
  document.querySelectorAll(".flash").forEach((flash) => {
    const hideDelay = parseInt(flash.dataset.autohide || "4500", 10);
    const timer = setTimeout(() => dismissFlash(flash), hideDelay);

    const closeBtn = flash.querySelector(".flash-close");
    if (closeBtn) {
      closeBtn.addEventListener("click", () => {
        clearTimeout(timer);
        dismissFlash(flash);
      });
    }
  });

  // celebrate a successful "add expense" by checking if the flash says so
  const successFlash = document.querySelector(".flash-success");
  if (successFlash && /added successfully/i.test(successFlash.textContent)) {
    burstConfetti();
  }
}

function dismissFlash(flash) {
  flash.classList.add("hide");
  setTimeout(() => flash.remove(), 350);
}

// ---------------- button ripple ----------------
function initRipple() {
  document.querySelectorAll(".btn-primary, .btn-ghost, .icon-btn").forEach((btn) => {
    btn.addEventListener("click", function (e) {
      const rect = this.getBoundingClientRect();
      const ripple = document.createElement("span");
      const size = Math.max(rect.width, rect.height);
      ripple.className = "ripple";
      ripple.style.width = ripple.style.height = size + "px";
      ripple.style.left = e.clientX - rect.left - size / 2 + "px";
      ripple.style.top = e.clientY - rect.top - size / 2 + "px";
      this.style.position = this.style.position || "relative";
      this.style.overflow = "hidden";
      this.appendChild(ripple);
      setTimeout(() => ripple.remove(), 650);
    });
  });
}

// ---------------- animated counters ----------------
function initCounters() {
  document.querySelectorAll("[data-count]").forEach((el) => {
    const target = parseFloat(el.dataset.count) || 0;
    const isMoney = el.closest(".gradient-coral") !== null;
    const duration = 1200;
    const start = performance.now();

    function tick(now) {
      const progress = Math.min((now - start) / duration, 1);
      const eased = 1 - Math.pow(1 - progress, 3);
      const value = target * eased;
      el.textContent = isMoney
        ? "₹" + value.toLocaleString("en-IN", { maximumFractionDigits: 0 })
        : Math.round(value).toLocaleString("en-IN");
      if (progress < 1) requestAnimationFrame(tick);
      else {
        el.textContent = isMoney
          ? "₹" + target.toLocaleString("en-IN", { maximumFractionDigits: 2 })
          : Math.round(target).toLocaleString("en-IN");
      }
    }
    requestAnimationFrame(tick);
  });
}

// ---------------- progress ring / bar fill ----------------
function initProgressFills() {
  const ring = document.querySelector(".ring-fill");
  if (ring) {
    const pct = parseFloat(ring.dataset.pct) || 0;
    const circumference = 2 * Math.PI * 52; // r=52
    const clampedPct = Math.min(pct, 100);
    const offset = circumference - (clampedPct / 100) * circumference;
    requestAnimationFrame(() => {
      ring.style.strokeDasharray = `${circumference}`;
      ring.style.strokeDashoffset = `${offset}`;
    });
  }

  document.querySelectorAll(".bar-fill").forEach((bar) => {
    const width = Math.min(parseFloat(bar.dataset.width) || 0, 100);
    requestAnimationFrame(() => {
      setTimeout(() => (bar.style.width = width + "%"), 100);
    });
  });
}

// ---------------- chart.js: dashboard category donut ----------------
function initCategoryChart() {
  const canvas = document.getElementById("categoryChart");
  if (!canvas || typeof Chart === "undefined") return;
  const data = window.__categoryData || {};
  const labels = Object.keys(data);
  const values = Object.values(data);

  if (!labels.length) {
    const ctx = canvas.getContext("2d");
    ctx.font = "14px Poppins";
    ctx.fillStyle = "#6E5A80";
    ctx.fillText("No data to chart yet.", 10, 30);
    return;
  }

  new Chart(canvas, {
    type: "doughnut",
    data: {
      labels,
      datasets: [
        {
          data: values,
          backgroundColor: [
            "#FF9472", "#4FD3C4", "#9B5DE5", "#F45B69",
            "#FFC75F", "#2CC9A0", "#5C7AFF", "#B0A8C9",
          ],
          borderWidth: 2,
          borderColor: "#fff",
        },
      ],
    },
    options: {
      responsive: true,
      plugins: { legend: { position: "bottom", labels: { boxWidth: 12, font: { family: "Poppins" } } } },
      cutout: "62%",
      animation: { animateScale: true, animateRotate: true },
    },
  });
}

// ---------------- chart.js: summary page pie + trend ----------------
function initSummaryCharts() {
  const pieCanvas = document.getElementById("summaryPieChart");
  if (pieCanvas && typeof Chart !== "undefined") {
    const data = window.__pieData || {};
    const labels = Object.keys(data);
    const values = Object.values(data);
    if (labels.length) {
      new Chart(pieCanvas, {
        type: "pie",
        data: {
          labels,
          datasets: [
            {
              data: values,
              backgroundColor: [
                "#FF9472", "#4FD3C4", "#9B5DE5", "#F45B69",
                "#FFC75F", "#2CC9A0", "#5C7AFF", "#B0A8C9",
              ],
              borderWidth: 2,
              borderColor: "#fff",
            },
          ],
        },
        options: {
          responsive: true,
          plugins: { legend: { position: "bottom", labels: { font: { family: "Poppins" } } } },
        },
      });
    } else {
      const ctx = pieCanvas.getContext("2d");
      ctx.font = "14px Poppins";
      ctx.fillStyle = "#6E5A80";
      ctx.fillText("No data to chart yet.", 10, 30);
    }
  }

  const trendCanvas = document.getElementById("trendChart");
  if (trendCanvas && typeof Chart !== "undefined") {
    const trend = window.__trendData || [];
    new Chart(trendCanvas, {
      type: "line",
      data: {
        labels: trend.map((t) => t.month),
        datasets: [
          {
            label: "Total spent",
            data: trend.map((t) => t.total),
            borderColor: "#FF6F91",
            backgroundColor: "rgba(255,111,145,0.2)",
            tension: 0.4,
            fill: true,
            pointBackgroundColor: "#845EC2",
            pointRadius: 5,
          },
        ],
      },
      options: {
        responsive: true,
        plugins: { legend: { display: false } },
        scales: {
          y: { beginAtZero: true, grid: { color: "rgba(132,94,194,0.1)" } },
          x: { grid: { display: false } },
        },
      },
    });
  }
}

// ---------------- confetti burst ----------------
function burstConfetti() {
  const colors = ["#FF6F91", "#845EC2", "#FFC75F", "#2CC9B8", "#9B5DE5"];
  const count = 40;
  for (let i = 0; i < count; i++) {
    const piece = document.createElement("div");
    piece.className = "confetti-piece";
    piece.style.left = Math.random() * 100 + "vw";
    piece.style.background = colors[Math.floor(Math.random() * colors.length)];
    piece.style.animationDuration = 2 + Math.random() * 1.5 + "s";
    piece.style.opacity = String(0.7 + Math.random() * 0.3);
    document.body.appendChild(piece);
    setTimeout(() => piece.remove(), 3600);
  }
}
