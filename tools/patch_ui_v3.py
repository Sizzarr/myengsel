import re
import os

app_file = 'webapp/static/app.js'
styles_file = 'webapp/static/styles.css'
index_file = 'webapp/static/index.html'

# 1. Update index.html for font and version
with open(index_file, 'r', encoding='utf-8') as f:
    idx = f.read()
if 'fonts.googleapis.com' not in idx:
    idx = idx.replace('<title>', '<link rel="preconnect" href="https://fonts.googleapis.com">\n  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>\n  <link href="https://fonts.googleapis.com/css2?family=Poppins:wght@400;500;600;700&display=swap" rel="stylesheet">\n  <title>')
idx = re.sub(r'v=\d+', 'v=12400', idx)
with open(index_file, 'w', encoding='utf-8') as f:
    f.write(idx)

# 2. Update app.js
with open(app_file, 'r', encoding='utf-8') as f:
    app_js = f.read()

# Inject icons
whatsapp_svg = "<svg viewBox=\\\"0 0 24 24\\\" fill=\\\"none\\\" stroke=\\\"currentColor\\\" stroke-width=\\\"2\\\" stroke-linecap=\\\"round\\\" stroke-linejoin=\\\"round\\\"><path d=\\\"M21 11.5a8.38 8.38 0 0 1-.9 3.8 8.5 8.5 0 0 1-7.6 4.7 8.38 8.38 0 0 1-3.8-.9L3 21l1.9-5.7a8.38 8.38 0 0 1-.9-3.8 8.5 8.5 0 0 1 4.7-7.6 8.38 8.38 0 0 1 3.8-.9h.5a8.48 8.48 0 0 1 8 8v.5z\\\"/></svg>"
pie_svg = "<svg viewBox=\\\"0 0 24 24\\\" fill=\\\"none\\\" stroke=\\\"currentColor\\\" stroke-width=\\\"2\\\" stroke-linecap=\\\"round\\\" stroke-linejoin=\\\"round\\\"><path d=\\\"M21.21 15.89A10 10 0 1 1 8 2.83M22 12A10 10 0 0 0 12 2v10z\\\"/></svg>"
pin_svg = "<svg viewBox=\\\"0 0 24 24\\\" fill=\\\"none\\\" stroke=\\\"currentColor\\\" stroke-width=\\\"2\\\" stroke-linecap=\\\"round\\\" stroke-linejoin=\\\"round\\\"><path d=\\\"M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0 1 18 0z\\\"/><circle cx=\\\"12\\\" cy=\\\"10\\\" r=\\\"3\\\"/></svg>"
lightning_svg = "<svg viewBox=\\\"0 0 24 24\\\" fill=\\\"none\\\" stroke=\\\"currentColor\\\" stroke-width=\\\"2\\\" stroke-linecap=\\\"round\\\" stroke-linejoin=\\\"round\\\"><polygon points=\\\"13 2 3 14 12 14 11 22 21 10 12 10 13 2\\\"/></svg>"

# Add to icons dict
icons_dict_search = "const icons = {"
icons_dict_replace = f"const icons = {{\n  whatsapp: '{whatsapp_svg}',\n  pie: '{pie_svg}',\n  pin: '{pin_svg}',\n  lightning: '{lightning_svg}',"
if 'whatsapp:' not in app_js:
    app_js = app_js.replace(icons_dict_search, icons_dict_replace)

old_topbar = "return `<header class=\"topbar\"><div class=\"page-title\"><h1>${escapeHtml(title)}</h1>${subtitle ? `<p>${escapeHtml(subtitle)}</p>` : ''}</div><div class=\"top-actions\"><button class=\"btn btn-secondary btn-small\" data-action=\"add-account\">${icon('plus')} Tambah Akun</button><button class=\"account-switch\" data-action=\"accounts\">${`<span class=\"avatar\">${active ? String(active.number).slice(-2) : 'XL'}</span>`}<span class=\"switch-text\"><span class=\"switch-number\">${active ? escapeHtml(active.number) : 'Belum login'}</span><span class=\"switch-type\">${active ? escapeHtml(active.subscription_type || 'XL') : 'Pilih akun'}</span></span>${icon('arrow')}</button></div></header>`;"
new_topbar = "return `<header class=\"topbar\"><div class=\"page-title\"><h1>${escapeHtml(title)}</h1>${subtitle ? `<p>${escapeHtml(subtitle)}</p>` : ''}</div><div class=\"top-actions\"><button class=\"btn btn-outline\" data-action=\"add-account\">${icon('plus')} Tambah Akun</button><button class=\"account-switch\" data-action=\"accounts\"><div class=\"avatar-small\">${active ? String(active.number).slice(-2) : 'XL'}</div><span class=\"switch-text\"><span class=\"switch-number\">${active ? escapeHtml(active.number) : 'Belum login'}</span><span class=\"switch-type\">${active ? escapeHtml(active.subscription_type || 'PREPAID') : 'Pilih akun'}</span></span>${icon('arrow')}</button></div></header>`;"
app_js = app_js.replace(old_topbar, new_topbar)

old_render_benefit = """function renderBenefit(benefit) {
  const type = benefit.data_type || 'OTHER';
  let rem = benefit.remaining || 0, total = benefit.total || 0, label = '';
  if (benefit.is_unlimited) label = 'Unlimited';
  else if (type === 'DATA') label = `${fmtQuota(rem)} / ${fmtQuota(total)}`;
  else if (type === 'VOICE') label = `${Math.round(rem / 60)} / ${Math.round(total / 60)} menit`;
  else if (type === 'TEXT') label = `${rem} / ${total} SMS`;
  else label = `${rem} / ${total}`;
  return { name: benefit.name || type, label, percent: benefit.is_unlimited ? 100 : pct(rem, total), type };
}"""
new_render_benefit = """function renderBenefit(benefit) {
  const type = benefit.data_type || 'OTHER';
  let rem = benefit.remaining || 0, total = benefit.total || 0, label = '';
  if (benefit.is_unlimited) label = 'Unlimited';
  else if (type === 'DATA') label = `${fmtQuota(rem)} / ${fmtQuota(total)}`;
  else if (type === 'VOICE') label = `${Math.round(rem / 60)} / ${Math.round(total / 60)} menit`;
  else if (type === 'TEXT') label = `${rem} / ${total} SMS`;
  else label = `${rem} / ${total}`;
  const hasTotal = Number(total) > 0;
  const percent = hasTotal ? pct(rem, total) : (benefit.is_unlimited ? 100 : null);
  
  let ic = 'check';
  const ln = (benefit.name || type).toLowerCase();
  if (ln.includes('whatsapp') || ln.includes('wa')) ic = 'whatsapp';
  else if (ln.includes('area') || ln.includes('lokal')) ic = 'pin';
  else if (type === 'DATA') ic = 'pie';
  
  return { name: benefit.name || type, label, percent, type, ic };
}"""
app_js = app_js.replace(old_render_benefit, new_render_benefit)

old_dashboard_body = r"""const body = `<section class="card dashboard-summary"><div class="summary-user"><span class="avatar">${String(dash.user.number).slice(-2)}</span><div><strong>${escapeHtml(dash.user.number)}</strong><small>${escapeHtml(dash.user.subscription_type || 'XL')}</small></div></div><div class="stat-block"><span class="stat-label">Balance</span><div class="stat-value">${fmtMoney(dash.balance.remaining)}</div><span class="preview-label">Aktif s.d. ${escapeHtml(dash.balance.expired_label)}</span></div><div class="stat-block"><span class="stat-label">Points</span><div class="stat-value">${escapeHtml(dash.points.current)}</div><span class="preview-label">Tier ${escapeHtml(dash.points.tier)}</span></div><div class="stat-block"><span class="stat-label">Notifications</span><div class="stat-value">${dash.unread_count || 0} unread</div><a href="#/notifications" class="link">Lihat notifikasi ></a></div></section><div class="dash-grid">${p ? `<section class="package-hero"><div class="package-hero-content"><div class="package-eyebrow">${icon('package')} Paket aktif</div><h2>${escapeHtml(p.name || p.group_name || 'My Package')}</h2><p>${escapeHtml(p.group_name || 'Paket XL')}</p><div class="quota-main"><span>Total kuota utama</span><strong>${mainData ? escapeHtml(mainData.label.split(' / ')[0]) : 'Lihat detail'}</strong>${mainData ? `<div class="quota-bar"><i style="width:${mainData.percent}%"></i></div>` : ''}</div><div class="benefit-row">${benefits.map(b => `<div class="benefit"><small>${escapeHtml(b.name)}</small><strong>${escapeHtml(b.label)}</strong></div>`).join('')}</div><a href="#/packages" class="btn" style="background:#fff;color:var(--blue-800)">Lihat My Packages ${icon('arrow')}</a></div></section>` : emptyState('Belum ada paket aktif', 'Data package quota-details tidak mengembalikan paket.', 'package')}<div class="side-stats"><div class="side-stats-top"><article class="card side-stat">${icon('coin', 'feature-icon')}<span class="preview-label">Balance</span><strong>${fmtMoney(dash.balance.remaining)}</strong><a href="#/transactions" class="link">Riwayat transaksi</a></article><article class="card side-stat">${icon('gift', 'feature-icon')}<span class="preview-label">Rewards</span><strong>${escapeHtml(dash.points.current)} pts</strong><a href="#/rewards" class="link">Lihat redeemables</a></article></div><section class="card quick-actions"><div class="quick-grid">${[['store', 'Beli Paket', 'store'], ['transactions', 'Transaksi', 'transaction'], ['family', 'Family Plan', 'family'], ['circle', 'XL Circle', 'circle']].map(([r, l, ic]) => `<a href="#/${r}" class="quick-action">${icon(ic, 'feature-icon')}<span>${l}</span></a>`).join('')}</div></section></div></div><div class="two-col"><div><div class="section-head"><h2>Recent Activity</h2><a href="#/transactions" class="link">Lihat semua</a></div>${tx.length ? `<div class="card list-card">${tx.map(renderTransactionRow).join('')}</div>` : emptyState('Belum ada transaksi', 'Riwayat transaksi belum tersedia.', 'transaction')}</div><div><div class="section-head"><h2>Bookmarks</h2><a href="#/bookmarks" class="link">Kelola</a></div><div id="dash-bookmarks">${loading()}</div></div></div><div class="section-head"><h2>Recommended Packages</h2><a href="#/store" class="link">Buka Store</a></div><div id="dash-recommended">${loading()}</div>`;"""
new_dashboard_body = r"""const body = `<section class="card dashboard-summary"><div class="summary-user"><div class="avatar-large">${String(dash.user.number).slice(-2)}</div><div class="sum-text"><strong class="sum-num">${escapeHtml(dash.user.number)}</strong><small class="sum-type">${escapeHtml(dash.user.subscription_type || 'PREPAID')}</small></div></div><div class="summary-divider"></div><div class="stat-block"><span class="stat-label">Balance</span><div class="stat-value">${fmtMoney(dash.balance.remaining)}</div><span class="preview-label">Aktif s.d. ${escapeHtml(dash.balance.expired_label)}</span></div><div class="summary-divider"></div><div class="stat-block"><span class="stat-label">Points</span><div class="stat-value">${escapeHtml(dash.points.current)}</div><span class="preview-label">Tier ${escapeHtml(dash.points.tier)}</span></div><div class="summary-divider"></div><div class="stat-block"><span class="stat-label">Notifications</span><div class="stat-value">${dash.unread_count || 0} unread</div><a href="#/notifications" class="link-blue">Lihat notifikasi &rarr;</a></div></section><div class="dash-grid">${p ? `<section class="package-hero"><div class="package-hero-content"><div class="package-eyebrow">${icon('package')} Paket aktif</div><h2>${escapeHtml(p.name || p.group_name || 'My Package')}</h2><p class="pkg-sub">${escapeHtml(p.group_name || 'Paket XL')}</p>${mainData && mainData.percent !== null ? `<div class="main-quota-wrap"><span class="main-quota-title">Total kuota utama</span><div class="main-quota-val">${escapeHtml(mainData.label.split(' / ')[0])}</div><div class="main-progress"><div class="main-progress-bar" style="width:${mainData.percent}%"></div></div></div>` : ''}<div class="benefit-row">${benefits.map(b => `<div class="benefit"><div class="benefit-top"><div class="b-icon-circle">${icon(b.ic)}</div><div class="b-text"><span class="b-name">${escapeHtml(b.name)}</span><span class="b-val">${escapeHtml(b.label)}</span></div></div>${b.percent !== null ? `<div class="benefit-bar"><i style="width:${b.percent}%"></i></div>` : ''}</div>`).join('')}</div><a href="#/packages" class="btn btn-white-pill">Lihat My Packages &rarr;</a></div></section>` : emptyState('Belum ada paket aktif', 'Data package quota-details tidak mengembalikan paket.', 'package')}<div class="side-stats"><section class="card widget-quick-actions"><div class="widget-head-qa">${icon('lightning')} Quick Actions</div><div class="qa-grid">${[['store', 'Beli Paket', 'store'], ['transactions', 'Transaksi', 'transaction'], ['family', 'Family Plan', 'family'], ['circle', 'XL Circle', 'circle']].map(([r, l, ic]) => `<a href="#/${r}" class="qa-btn"><div class="qa-icon-wrap">${icon(ic)}</div><span class="qa-label">${l}</span></a>`).join('')}</div></section><section class="card widget-rewards"><div class="w-rev-content"><div class="widget-head-qa">${icon('gift')} Rewards</div><div class="w-rev-points">${escapeHtml(dash.points.current)} pts</div><a href="#/rewards" class="link-blue">Lihat redeemables &rarr;</a></div><div class="w-rev-ill">${icon('gift')}</div></section><section class="card widget-notifications"><div class="w-rev-content"><div class="widget-head-qa">${icon('bell')} Notifikasi</div><div class="w-rev-points">${dash.unread_count || 0} unread</div><span class="preview-label">${dash.unread_count ? `<a href="#/notifications" class="link-blue">Lihat notifikasi &rarr;</a>` : 'Belum ada notifikasi baru'}</span></div><div class="w-rev-ill ill-bell">${icon('bell')}</div></section></div></div><div class="two-col"><div><div class="section-head"><h2>Recent Activity</h2><a href="#/transactions" class="link">Lihat semua</a></div>${tx.length ? `<div class="card list-card">${tx.map(renderTransactionRow).join('')}</div>` : emptyState('Belum ada transaksi', 'Riwayat transaksi belum tersedia.', 'transaction')}</div><div><div class="section-head"><h2>Bookmarks</h2><a href="#/bookmarks" class="link">Kelola</a></div><div id="dash-bookmarks">${loading()}</div></div></div><div class="section-head"><h2>Recommended Packages</h2><a href="#/store" class="link">Buka Store</a></div><div id="dash-recommended">${loading()}</div>`;"""
app_js = re.sub(r'const body = `<section class="card dashboard-summary">.*?appShell\(\'dashboard\', \'Dashboard\', \'Ringkasan akun dan fitur utama.\', body\);', new_dashboard_body + '\n    app.innerHTML = appShell(\'dashboard\', \'Dashboard\', \'Ringkasan akun dan fitur utama.\', body);', app_js, flags=re.DOTALL)

with open(app_file, 'w', encoding='utf-8') as f:
    f.write(app_js)

# 3. Update styles.css
with open(styles_file, 'r', encoding='utf-8') as f:
    css = f.read()

# Font, colors
css = css.replace('--blue-800: #0b36c9;', '--blue-800: #0B36C9;\n  --blue-900: #0A2688;\n  --cyan: #0EAEDB;\n  --bg-primary: #F5F7FC;\n  --text-main: #0B163F;\n  --text-sec: #7180A0;\n  --success: #16C99A;')
css = css.replace('background: #fff;', 'background: var(--bg-primary);')
css = css.replace("font-family: 'Poppins', ui-sans-serif,", "font-family: 'Poppins', 'Inter', sans-serif, ui-sans-serif,")
css = css.replace('color: var(--ink);', 'color: var(--text-main);')

# Topbar & Layout
css = css.replace('.content {\n  max-width: 1320px;\n  margin: 0 auto;\n}', '.content {\n  max-width: 1500px;\n  margin: 0 auto;\n  padding: 0 32px;\n}')
css = css.replace('.workspace {\n  min-width: 0;\n  padding: 18px 26px 34px;\n}', '.workspace {\n  min-width: 0;\n  padding: 18px 0 34px;\n}')
css = css.replace('.topbar {\n  height: 64px;\n  display: flex;\n  align-items: center;\n  justify-content: space-between;\n  gap: 20px;\n  margin-bottom: 14px;\n}', '.topbar {\n  height: 64px;\n  display: flex;\n  align-items: center;\n  justify-content: space-between;\n  gap: 20px;\n  margin-bottom: 24px;\n  padding: 0 32px;\n  max-width: 1500px;\n  margin-left: auto;\n  margin-right: auto;\n}')
css = css.replace('.page-title h1 {\n  font-size: 27px;\n  margin: 0;\n  letter-spacing: -.035em;\n}', '.page-title h1 {\n  font-size: 28px;\n  margin: 0;\n  font-weight: 700;\n  letter-spacing: -.02em;\n  color: var(--text-main);\n}')
css = css.replace('.page-title p {\n  color: var(--muted);\n  margin: 5px 0 0;\n  font-size: 13px;\n}', '.page-title p {\n  color: var(--text-sec);\n  margin: 4px 0 0;\n  font-size: 14px;\n}')

# Dashboard Summary
old_summary_css = r""".dashboard-summary {
  padding: 22px;
  display: grid;
  grid-template-columns: 1.3fr repeat(3, .7fr);
  gap: 18px;
  align-items: center;
}"""
new_summary_css = r""".dashboard-summary {
  padding: 18px 24px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  border-radius: 18px;
  border: 1px solid #E6EAF3;
  box-shadow: 0 6px 20px rgba(27, 53, 116, 0.05);
  background: #fff;
  min-height: 100px;
}"""
css = css.replace(old_summary_css, new_summary_css)

# Stat block
css = css.replace('.stat-block {\n  padding-left: 18px;\n  border-left: 1px solid var(--line);\n}', '.stat-block {\n  padding-left: 0;\n  border-left: none;\n}')

# Dash grid
css = css.replace('.dash-grid {\n  display: grid;\n  grid-template-columns: 1.7fr .8fr;\n  gap: 18px;\n  margin-top: 18px;\n}', '.dash-grid {\n  display: grid;\n  grid-template-columns: minmax(0, 2fr) minmax(320px, 0.85fr);\n  gap: 16px;\n  margin-top: 18px;\n}')

# Package Hero
old_hero = r"""background: radial-gradient(circle at 85% 18%, rgba(0, 220, 255, .6), transparent 25%), linear-gradient(135deg, #071d83, #0a43d8 62%, #08b8de);"""
new_hero = r"""background: linear-gradient(120deg, #0829A9 0%, #064DDA 55%, #10B8DB 100%); padding: 32px;"""
css = css.replace(old_hero, new_hero)

# Benefits
old_benefit_css = r""".benefit {
  padding: 12px;
  border-radius: 13px;
  background: rgba(3, 25, 105, .34);
  border: 1px solid rgba(255, 255, 255, .16);
}

.benefit small {
  display: block;
  opacity: .72;
}

.benefit strong {
  margin-top: 4px;
  display: block;
  font-size: 16px;
}"""
new_benefit_css = r""".benefit {
  padding: 16px;
  border-radius: 14px;
  background: rgba(5, 33, 130, 0.38);
  border: 1px solid rgba(255, 255, 255, .20);
  display: flex;
  flex-direction: column;
  justify-content: space-between;
}
.benefit-top {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 12px;
}
.b-icon-circle {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  background: rgba(255,255,255,0.15);
  display: grid;
  place-items: center;
}
.b-icon-circle svg { width: 16px; height: 16px; }
.b-text { display: flex; flex-direction: column; }
.b-name { font-size: 12px; opacity: 0.9; }
.b-val { font-size: 13px; font-weight: 700; margin-top: 2px; }
.benefit-bar { height: 4px; border-radius: 999px; background: rgba(255,255,255,0.25); overflow: hidden; }
.benefit-bar i { display: block; height: 100%; border-radius: 999px; background: #16C99A; }
"""
css = css.replace(old_benefit_css, new_benefit_css)


css += r"""
/* NEW CLASSES */
.btn-outline {
  border: 1px solid var(--blue-800);
  background: #fff;
  color: var(--blue-800);
  border-radius: 12px;
  height: 44px;
  padding: 0 16px;
  font-weight: 600;
  display: inline-flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
  font-family: inherit;
  font-size: 14px;
}
.account-switch {
  display: flex;
  align-items: center;
  gap: 10px;
  border: 1px solid #E6EAF3;
  padding: 6px 12px 6px 6px;
  border-radius: 30px;
  background: #fff;
  cursor: pointer;
}
.avatar-small {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  background: var(--blue-800);
  color: #fff;
  display: grid;
  place-items: center;
  font-size: 12px;
  font-weight: 700;
}

.summary-user { display: flex; align-items: center; gap: 16px; }
.avatar-large { width: 50px; height: 50px; border-radius: 50%; background: var(--blue-800); color: #fff; display: grid; place-items: center; font-size: 18px; font-weight: 700; }
.sum-text { display: flex; flex-direction: column; }
.sum-num { font-size: 18px; color: var(--text-main); font-weight: 700; }
.sum-type { font-size: 12px; color: var(--text-sec); text-transform: uppercase; margin-top: 4px;}
.summary-divider { width: 1px; height: 40px; background: #E6EAF3; }
.stat-block .stat-label { font-size: 12px; color: var(--text-sec); margin-bottom: 4px; display: block; }
.stat-block .stat-value { font-size: 20px; font-weight: 700; color: var(--text-main); margin-bottom: 4px; }
.link-blue { color: var(--blue-800); font-size: 13px; font-weight: 600; text-decoration: none; }

.pkg-sub { font-size: 14px; opacity: 0.9; margin-top: 4px; margin-bottom: 24px; }
.main-quota-wrap { margin-bottom: 24px; }
.main-quota-title { font-size: 14px; font-weight: 500; }
.main-quota-val { font-size: 38px; font-weight: 700; margin-top: 4px; margin-bottom: 12px; letter-spacing: -1px; }
.main-progress { width: 80%; height: 8px; border-radius: 999px; background: rgba(255,255,255,0.25); overflow: hidden; }
.main-progress-bar { height: 100%; border-radius: 999px; background: #16C99A; }

.btn-white-pill {
  background: #fff;
  color: var(--blue-800);
  border: 0;
  border-radius: 10px;
  height: 40px;
  font-weight: 600;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  padding: 0 16px;
  cursor: pointer;
  margin-top: 24px;
}

.widget-quick-actions, .widget-rewards, .widget-notifications {
  background: #fff;
  border-radius: 16px;
  padding: 20px;
  border: 1px solid #E6EAF3;
  margin-bottom: 16px;
  display: flex;
}
.widget-quick-actions { flex-direction: column; }
.widget-rewards, .widget-notifications { align-items: center; justify-content: space-between; }

.widget-head-qa {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 14px;
  font-weight: 700;
  color: var(--text-main);
  margin-bottom: 16px;
}
.widget-head-qa svg { width: 18px; height: 18px; color: var(--blue-800); }

.qa-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 12px;
}
.qa-btn {
  border: 1px solid #F0F2F7;
  border-radius: 12px;
  padding: 12px 14px;
  display: flex;
  align-items: center;
  gap: 12px;
  text-decoration: none;
  color: var(--text-main);
  font-weight: 600;
  font-size: 13px;
  transition: 0.2s;
}
.qa-btn:hover { border-color: var(--blue-800); background: #F8FAFF; }
.qa-icon-wrap {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  background: #F0F4FF;
  color: var(--blue-800);
  display: grid;
  place-items: center;
}
.qa-icon-wrap svg { width: 16px; height: 16px; }

.w-rev-points {
  font-size: 24px;
  font-weight: 700;
  color: var(--text-main);
  margin-bottom: 4px;
}
.w-rev-ill {
  color: var(--blue-800);
  opacity: 0.15;
}
.w-rev-ill svg { width: 80px; height: 80px; }
.ill-bell { color: var(--cyan); }
"""
with open(styles_file, 'w', encoding='utf-8') as f:
    f.write(css)

print("Patch applied")
