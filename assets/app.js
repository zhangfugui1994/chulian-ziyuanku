// 初恋资源库 —— 静态渲染逻辑
// 数据源: data/resources.json
// 布局参考:主列表(封面+标题+摘要)+ 侧栏热门榜 + 分页 + 顶部多栏目导航

const $ = (sel) => document.querySelector(sel);

const PAGE_SIZE = 12;          // 每页主列表条数
const SIDEBAR_TOP = 8;         // 侧栏热门榜条数

async function loadResources() {
  try {
    const res = await fetch("data/resources.json", { cache: "no-store" });
    if (!res.ok) throw new Error("HTTP " + res.status);
    const data = await res.json();
    // 兼容:支持 resources 为数组,或 {resources:[...]}
    return Array.isArray(data) ? data : (data.resources || []);
  } catch (err) {
    console.error("加载资料失败:", err);
    const catalog = $("#catalog");
    if (catalog) {
      catalog.innerHTML =
        '<p class="empty">资料加载失败:请通过 <strong>HTTP</strong> 访问(file:// 会被 CORS 拦截)。' +
        "部署到 GitHub / Cloudflare 后此问题不存在。</p>";
    }
    return [];
  }
}

function escapeHtml(s) {
  return String(s ?? "")
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;");
}

function fmtHotness(n) {
  const v = Number(n) || 0;
  if (v >= 10000) return (v / 10000).toFixed(2).replace(/\.?0+$/, "") + "K";
  return String(v);
}

// 封面:有 cover 显示图,没有显示占位块
function coverBlock(r) {
  if (r.cover) {
    return `<img class="cover" src="${escapeHtml(r.cover)}" alt="${escapeHtml(r.title)}" loading="lazy" onerror="this.parentElement.classList.add('cover-fallback')"/>`;
  }
  return `<div class="cover cover-fallback"><span>${escapeHtml((r.title || "").slice(0, 4))}</span></div>`;
}

// ---- 主列表卡片(左图右文,参考站版式)----
function cardHtml(r) {
  const cat = r.category ? `<a class="chip cat" href="index.html?cat=${encodeURIComponent(r.category)}">${escapeHtml(r.category)}</a>` : "";
  const tags = (r.tags || []).map((t) => `<span class="chip">${escapeHtml(t)}</span>`).join("");
  const meta = [
    r.time ? `<span>${escapeHtml(r.time)}</span>` : "",
    r.price ? `<span class="free">${escapeHtml(r.price)}</span>` : "",
    r.hotness != null ? `<span class="hot">热度 ${fmtHotness(r.hotness)}</span>` : "",
  ].filter(Boolean).join("");
  return `
    <article class="card">
      <a class="cover-wrap" href="resource.html?id=${encodeURIComponent(r.id)}">${coverBlock(r)}</a>
      <div class="card-main">
        <div class="chips">${cat}${tags}</div>
        <h3><a href="resource.html?id=${encodeURIComponent(r.id)}">${escapeHtml(r.title)}</a></h3>
        <p class="summary">${escapeHtml(r.summary || "")}</p>
        <div class="meta">${meta}</div>
      </div>
    </article>`;
}

function renderCatalog(items) {
  const catalog = $("#catalog");
  if (!items.length) {
    catalog.innerHTML = '<p class="empty">没有匹配的资料。</p>';
    return;
  }
  catalog.innerHTML = items.map(cardHtml).join("");
}

// ---- 侧栏热门榜(按 hotness 降序,取前 N)----
function renderSidebar(items) {
  const box = $("#sidebar");
  if (!box) return;
  const top = items
    .filter((r) => r.hotness != null)
    .sort((a, b) => (Number(b.hotness) || 0) - (Number(a.hotness) || 0))
    .slice(0, SIDEBAR_TOP);
  if (!top.length) {
    box.innerHTML = '<div class="side-box"><h4>热门榜</h4><p class="muted">暂无热度数据</p></div>';
    return;
  }
  box.innerHTML =
    '<div class="side-box"><h4>热门榜</h4><ol class="rank-list">' +
    top
      .map(
        (r, i) => `
      <li>
        <span class="rank-num">${i + 1}</span>
        <a href="resource.html?id=${encodeURIComponent(r.id)}" title="${escapeHtml(r.title)}">${escapeHtml(r.title)}</a>
        <span class="rank-hot">热度(${fmtHotness(r.hotness)})</span>
      </li>`
      )
      .join("") +
    "</ol></div>";
}

// ---- 分页 ----
function renderPager(total, page, applyPage) {
  const pager = $("#pager");
  if (!pager) return;
  const pages = Math.ceil(total / PAGE_SIZE);
  if (pages <= 1) {
    pager.innerHTML = "";
    pager.classList.add("hidden");
    return;
  }
  pager.classList.remove("hidden");
  const cur = Math.min(page, pages);
  const btn = (p, label, disabled) =>
    `<button class="page-btn" data-page="${p}" ${disabled ? "disabled" : ""}>${label}</button>`;
  let html = btn(cur - 1, "‹ 上一页", cur === 1);
  const start = Math.max(1, cur - 3);
  const end = Math.min(pages, cur + 3);
  for (let p = start; p <= end; p++) {
    html += `<button class="page-btn ${p === cur ? "active" : ""}" data-page="${p}">${p}</button>`;
  }
  html += btn(cur + 1, "下一页 ›", cur === pages);
  pager.innerHTML = html;
  pager.querySelectorAll(".page-btn[data-page]").forEach((b) => {
    b.addEventListener("click", () => applyPage(Number(b.dataset.page)));
  });
}

// ---- 分类下拉(筛选,保留原有功能)----
function renderFilters(items) {
  const select = $("#filter-category");
  const cats = [...new Set(items.map((i) => i.category).filter(Boolean))];
  select.innerHTML =
    `<option value="">全部分类</option>` +
    cats.map((c) => `<option value="${escapeHtml(c)}">${escapeHtml(c)}</option>`).join("");
}

// ---- 顶部多栏目导航(参考站式:首页 + 各分类)----
function renderNav(items) {
  const nav = $("#nav-cats");
  if (!nav) return;
  const cats = [...new Set(items.map((i) => i.category).filter(Boolean))];
  nav.innerHTML =
    `<a class="nav-item active" href="index.html">首页</a>` +
    cats.map((c) => `<a class="nav-item" href="index.html?cat=${encodeURIComponent(c)}">${escapeHtml(c)}</a>`).join("");
}

// ---- 列表页 ----
function initListPage() {
  if (!document.getElementById("catalog")) return;
  let all = [];
  let page = 1;

  const applyFilters = () => {
    const q = ($("#search")?.value || "").trim().toLowerCase();
    const catSel = $("#filter-category")?.value || "";
    // 支持 URL ?cat= 直接命中导航
    const urlCat = new URLSearchParams(location.search).get("cat") || "";
    const cat = catSel || urlCat;
    const filtered = all.filter((r) => {
      const hay = (r.title + " " + (r.summary || "") + " " + (r.tags || []).join(" ") + " " + (r.category || "")).toLowerCase();
      const okCat = !cat || r.category === cat;
      const okQ = !q || hay.includes(q);
      return okCat && okQ;
    });
    // 分页切第一页
    page = 1;
    renderPaged(filtered);
  };

  const renderPaged = (filtered) => {
    const total = filtered.length;
    const start = (page - 1) * PAGE_SIZE;
    const slice = filtered.slice(start, start + PAGE_SIZE);
    renderCatalog(slice);
    renderPager(total, page, (p) => {
      page = p;
      renderPaged(filtered);
      window.scrollTo({ top: 0, behavior: "smooth" });
    });
    renderSidebar(all);
  };

  loadResources().then((items) => {
    all = items || [];
    renderNav(all);
    renderFilters(all);
    $("#search").addEventListener("input", applyFilters);
    $("#filter-category").addEventListener("change", applyFilters);
    // 若 URL 带 ?cat=,选中对应筛选项
    const urlCat = new URLSearchParams(location.search).get("cat");
    if (urlCat) $("#filter-category").value = urlCat;
    applyFilters();
  });
}

// ---- 详情页 ----
function initDetailPage() {
  if (!document.getElementById("detail")) return;
  const params = new URLSearchParams(location.search);
  const id = params.get("id");
  loadResources().then((items) => {
    const item = (items || []).find((r) => r.id === id);
    const root = $("#detail");
    if (!item) {
      root.innerHTML = `<p class="empty">未找到该资料(id=${escapeHtml(id || "?")})。<a class="back" href="index.html">← 返回列表</a></p>`;
      return;
    }
    document.title = item.title + " · 初恋资源库";
    const cover = item.cover
      ? `<img class="detail-cover" src="${escapeHtml(item.cover)}" alt="${escapeHtml(item.title)}" onerror="this.style.display='none'"/>`
      : "";
    const tags = (item.tags || []).map((t) => `<span class="chip">${escapeHtml(t)}</span>`).join("");
    const cat = item.category ? `<span class="chip cat">${escapeHtml(item.category)}</span>` : "";
    const meta = [
      item.time ? `<span>${escapeHtml(item.time)}</span>` : "",
      item.price ? `<span class="free">${escapeHtml(item.price)}</span>` : "",
      item.hotness != null ? `<span class="hot">热度 ${fmtHotness(item.hotness)}</span>` : "",
    ].filter(Boolean).join("");
    const body = (item.body || "暂无正文。").split(/\n+/).map((p) => `<p>${escapeHtml(p)}</p>`).join("");
    root.innerHTML = `
      <a class="back" href="index.html">← 返回列表</a>
      <div class="detail-head">
        ${cover ? `<div class="detail-cover-wrap">${cover}</div>` : ""}
        <div class="detail-title">
          <h1>${escapeHtml(item.title)}</h1>
          <div class="meta">${cat}${tags}${meta}</div>
        </div>
      </div>
      <div class="body">${body}</div>`;
  });
}

initListPage();
initDetailPage();
