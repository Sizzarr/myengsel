const $ = (q, root = document) => root.querySelector(q);
const $$ = (q, root = document) => [...root.querySelectorAll(q)];
const app = $('#app');
const modalRoot = $('#modal-root');
const toastEl = $('#toast');

const state = {
  accounts: JSON.parse(localStorage.getItem('accounts') || '[]'),
  dashboard: null,
  packages: [],
  storePackages: [],
  families: [],
  segments: [],
  unread: 0,
  loginNumber: '',
  otpTries: 5,
};

const icons = {
  whatsapp: '<svg viewBox=\"0 0 24 24\" fill=\"none\" stroke=\"currentColor\" stroke-width=\"2\" stroke-linecap=\"round\" stroke-linejoin=\"round\"><path d=\"M21 11.5a8.38 8.38 0 0 1-.9 3.8 8.5 8.5 0 0 1-7.6 4.7 8.38 8.38 0 0 1-3.8-.9L3 21l1.9-5.7a8.38 8.38 0 0 1-.9-3.8 8.5 8.5 0 0 1 4.7-7.6 8.38 8.38 0 0 1 3.8-.9h.5a8.48 8.48 0 0 1 8 8v.5z\"/></svg>',
  pie: '<svg viewBox=\"0 0 24 24\" fill=\"none\" stroke=\"currentColor\" stroke-width=\"2\" stroke-linecap=\"round\" stroke-linejoin=\"round\"><path d=\"M21.21 15.89A10 10 0 1 1 8 2.83M22 12A10 10 0 0 0 12 2v10z\"/></svg>',
  pin: '<svg viewBox=\"0 0 24 24\" fill=\"none\" stroke=\"currentColor\" stroke-width=\"2\" stroke-linecap=\"round\" stroke-linejoin=\"round\"><path d=\"M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0 1 18 0z\"/><circle cx=\"12\" cy=\"10\" r=\"3\"/></svg>',
  lightning: '<svg viewBox=\"0 0 24 24\" fill=\"none\" stroke=\"currentColor\" stroke-width=\"2\" stroke-linecap=\"round\" stroke-linejoin=\"round\"><polygon points=\"13 2 3 14 12 14 11 22 21 10 12 10 13 2\"/></svg>',
  dashboard: '<path d="M3 11.5 12 4l9 7.5"/><path d="M5 10.5V20h14v-9.5"/><path d="M9 20v-6h6v6"/>',
  package: '<path d="M4 8.5 12 4l8 4.5v8L12 21l-8-4.5z"/><path d="m4 8.5 8 4.5 8-4.5M12 13v8"/>',
  store: '<path d="M4 9h16l-1-5H5L4 9Z"/><path d="M5 9v11h14V9"/><path d="M9 20v-6h6v6"/>',
  transaction: '<path d="M7 7h11l-2.5-2.5M17 17H6l2.5 2.5"/><path d="M18 7 15.5 9.5M6 17l2.5-2.5"/>',
  family: '<circle cx="9" cy="8" r="3"/><circle cx="17" cy="9" r="2.5"/><path d="M3 19c.5-4 2.7-6 6-6s5.5 2 6 6M14.5 14c3.6.2 5.5 2 5.5 5"/>',
  circle: '<circle cx="12" cy="12" r="9"/><circle cx="12" cy="9" r="2.3"/><path d="M7.5 17c.6-2.8 2-4.2 4.5-4.2s4 1.4 4.5 4.2"/>',
  gift: '<path d="M4 10h16v10H4zM3 7h18v3H3zM12 7v13"/><path d="M12 7H8.5A2.5 2.5 0 1 1 11 4.5L12 7Zm0 0h3.5A2.5 2.5 0 1 0 13 4.5L12 7Z"/>',
  bookmark: '<path d="M6 4h12v17l-6-4-6 4z"/>',
  bell: '<path d="M18 8a6 6 0 0 0-12 0c0 7-3 7-3 9h18c0-2-3-2-3-9M10 21h4"/>',
  support: '<path d="M4 13a8 8 0 0 1 16 0"/><path d="M4 13v5h3v-5H4Zm13 0v5h3v-5h-3ZM17 18c0 2-1.5 3-4 3"/>',
  user: '<circle cx="12" cy="8" r="4"/><path d="M4 21c.7-5 3.4-7 8-7s7.3 2 8 7"/>',
  plus: '<path d="M12 5v14M5 12h14"/>',
  arrow: '<path d="m9 18 6-6-6-6"/>',
  back: '<path d="m15 18-6-6 6-6"/>',
  close: '<path d="m6 6 12 12M18 6 6 18"/>',
  phone: '<path d="M7 3h4l2 5-3 2c1 3 3 5 6 6l2-3 5 2v4c0 1-1 2-2 2C10 21 3 14 3 5c0-1 1-2 2-2h2Z"/>',
  lock: '<rect x="5" y="10" width="14" height="10" rx="2"/><path d="M8 10V7a4 4 0 0 1 8 0v3"/>',
  search: '<circle cx="11" cy="11" r="7"/><path d="m20 20-4-4"/>',
  trash: '<path d="M4 7h16M9 7V4h6v3M7 7l1 14h8l1-14M10 11v6M14 11v6"/>',
  check: '<path d="m5 12 4 4L19 6"/>',
  globe: '<circle cx="12" cy="12" r="9"/><path d="M3 12h18M12 3a14 14 0 0 1 0 18M12 3a14 14 0 0 0 0 18"/>',
  coin: '<circle cx="9" cy="9" r="6"/><path d="M7 9h4M9 6v6"/><circle cx="16" cy="15" r="5"/>',
  menu: '<path d="M4 7h16M4 12h16M4 17h16"/>',
  refresh: '<path d="M20 7v5h-5M4 17v-5h5"/><path d="M6.5 8a7 7 0 0 1 11.5-2l2 2M17.5 16a7 7 0 0 1-11.5 2l-2-2"/>',
  info: '<circle cx="12" cy="12" r="9"/><path d="M12 11v6M12 7h.01"/>',
};

function icon(name, cls = 'icon') {
  const classes = cls.split(/\s+/).includes('icon') ? cls : `${cls} icon`;
  return `<span class="${classes}"><svg viewBox="0 0 24 24" aria-hidden="true">${icons[name] || icons.info}</svg></span>`;
}

function brand() {
  return `<a class="brand" href="#/"><span class="brand-mark"></span><span>myXL</span></a>`;
}

function escapeHtml(value = '') {
  return String(value).replace(/[&<>'"]/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', "'": '&#39;', '"': '&quot;' }[c]));
}

function fmtMoney(value) {
  const n = Number(String(value ?? 0).replace(/[^0-9.-]/g, '')) || 0;
  return `Rp ${new Intl.NumberFormat('id-ID').format(n)}`;
}

function fmtQuota(bytes) {
  const n = Number(bytes) || 0;
  if (!n) return '0';
  if (n >= 1024 ** 3) return `${(n / (1024 ** 3)).toFixed(n / (1024 ** 3) >= 10 ? 0 : 2)} GB`;
  if (n >= 1024 ** 2) return `${(n / (1024 ** 2)).toFixed(1)} MB`;
  if (n >= 1024) return `${(n / 1024).toFixed(1)} KB`;
  return `${n}`;
}

function pct(rem, total) {
  const a = Number(rem) || 0, b = Number(total) || 0;
  return b > 0 ? Math.max(0, Math.min(100, Math.round((a / b) * 100))) : 0;
}

function toast(message, type = '') {
  toastEl.textContent = message;
  toastEl.className = `toast show ${type}`;
  clearTimeout(toastEl._t);
  toastEl._t = setTimeout(() => toastEl.className = 'toast', 3300);
}

async function api(url, options = {}) {
  const active = state.accounts.find(x => x.active) || state.accounts[0];
  const headers = { 'Content-Type': 'application/json', ...(options.headers || {}) };
  
  if (active && active.tokens) {
    headers['X-Number'] = active.number.toString();
    headers['X-Refresh-Token'] = active.tokens.refresh_token || '';
    headers['X-Subscriber-Id'] = active.subscriber_id || '';
    headers['X-Subscription-Type'] = active.subscription_type || '';
  }

  const opt = { ...options, headers };
  const res = await fetch(url, opt);
  let data = null;
  try { data = await res.json(); } catch { data = {}; }
  if (!res.ok) {
    if (res.status === 401 && active) {
      toast('Sesi habis, silakan login ulang.', 'error');
      state.accounts = state.accounts.filter(a => a.number !== active.number);
      saveAccounts();
      location.hash = '#/login';
    }
    throw new Error(data.detail || `Request gagal (${res.status})`);
  }
  
  // Update tokens if backend returned new ones (e.g. after refresh)
  if (data.tokens && active) {
     active.tokens = data.tokens;
     saveAccounts();
  }
  
  return data;
}

function saveAccounts() {
  localStorage.setItem('accounts', JSON.stringify(state.accounts));
}

function loading() {
  return `<div class="card loading"><div><div class="spinner"></div><p>Memuat data…</p></div></div>`;
}

function emptyState(title, text, iconName = 'info', action = '') {
  return `<div class="card empty"><div>${icon(iconName, 'feature-icon')}<h3>${escapeHtml(title)}</h3><p>${escapeHtml(text)}</p>${action}</div></div>`;
}

const navItems = [
  ['dashboard', 'Dashboard', 'dashboard'],
  ['packages', 'My Packages', 'package'],
  ['store', 'Store', 'store'],
  ['transactions', 'Transactions', 'transaction'],
  ['family', 'Family Plan', 'family'],
  ['circle', 'XL Circle', 'circle'],
  ['rewards', 'Rewards', 'gift'],
  ['bookmarks', 'Bookmarks', 'bookmark'],
  ['notifications', 'Notifications', 'bell'],
  ['support', 'Support', 'support'],
];

function sidebar(active) {
  return `<aside class="sidebar">${brand()}<nav class="side-nav">${navItems.map(([id, label, ic]) => `<a href="#/${id}" class="side-link ${active === id ? 'active' : ''}">${icon(ic)}<span>${label}</span>${id === 'notifications' && state.unread ? `<span class="count">${state.unread}</span>` : ''}</a>`).join('')}</nav><div class="side-footer"><strong>Web UI lokal</strong><br>UI ini memakai API dan file token yang sama dengan CLI.</div></aside>`;
}

function topbar(title, subtitle = '') {
  const active = state.accounts.find(x => x.active) || state.accounts[0];
  return `<header class="topbar"><div class="page-title"><h1>${escapeHtml(title)}</h1>${subtitle ? `<p>${escapeHtml(subtitle)}</p>` : ''}</div><div class="top-actions">${active ? `<button class="btn btn-outline" style="border-color:var(--red);color:var(--red)" data-action="logout">Logout</button>` : ''}<a href="#/" class="btn btn-outline" style="text-decoration:none">${icon('home')} Home</a><button class="account-switch" data-action="accounts"><div class="avatar-small">${active ? String(active.number).slice(-2) : 'XL'}</div><span class="switch-text"><span class="switch-number">${active ? escapeHtml(active.number) : 'Belum login'}</span><span class="switch-type">${active ? escapeHtml(active.subscription_type || 'PREPAID') : 'Pilih akun'}</span></span>${icon('arrow')}</button></div></header>`;
}

function appShell(active, title, subtitle, body) {
  return `<div class="app-shell">${sidebar(active)}<main class="workspace">${topbar(title, subtitle)}<div class="content">${body}</div></main></div>`;
}

async function loadAccounts() {
  state.accounts = JSON.parse(localStorage.getItem('accounts') || '[]');
}

function landingPage() {
  app.innerHTML = `<div class="landing"><nav class="public-nav">${brand()}<div class="nav-links"><a class="active" href="#/">Home</a><a href="#/store">Packages</a><a href="#/rewards">Rewards</a><a href="#/family">Family Plan</a><a href="#/circle">XL Circle</a><a href="#/support">Support</a></div><div class="public-actions"><button class="btn btn-secondary btn-small" data-action="login">Login</button></div></nav><main class="landing-main"><section class="hero"><div class="hero-copy"><h1>Kelola layanan XL dalam satu tempat.</h1><p>Login aman dengan OTP, cek paket aktif, cari paket dari Store, lakukan pembayaran normal, serta kelola Family Plan dan XL Circle tanpa keramaian menu CLI.</p><div class="hero-actions"><button class="btn btn-primary" data-action="get-started">Mulai Sekarang ${icon('arrow')}</button><a class="btn btn-secondary" href="#/store">Lihat Paket</a></div></div><div class="hero-preview"><div class="preview-top"><div><span class="preview-label">Akun aktif</span><div class="preview-number">62819••••••••</div></div><div class="preview-balance"><span class="preview-label">Saldo</span><strong>Ringkas & jelas</strong></div></div><div class="preview-package"><div class="preview-package-head"><div><span class="mini-badge">Paket aktif</span><h3>Xtra Combo</h3></div><button class="link">Lihat Detail ${icon('arrow')}</button></div><div class="preview-grid"><div class="preview-stat"><span class="preview-label">Internet</span><strong>12.4 GB</strong><div class="mini-progress"><i style="width:62%"></i></div></div><div class="preview-stat"><span class="preview-label">Voice</span><strong>60 Min</strong><div class="mini-progress"><i style="width:60%"></i></div></div><div class="preview-stat"><span class="preview-label">SMS</span><strong>50 SMS</strong><div class="mini-progress"><i style="width:50%"></i></div></div><div class="preview-stat"><span class="preview-label">Points</span><strong>1.240</strong><div class="mini-progress"><i style="width:78%"></i></div></div></div></div></div></section><div class="landing-features">${[
    ['lock', 'Secure OTP Login', 'Login memakai nomor XL 628… dan OTP 6 digit sesuai flow program.'],
    ['package', 'My Packages', 'Lihat paket aktif, benefit DATA/VOICE/TEXT, kuota tersisa, dan detail paket.'],
    ['store', 'Store Packages', 'Cari package families, store packages, dan redeemables dari API program.'],
    ['family', 'Family & Circle', 'Kelola Family Plan/Akrab Organizer dan XL Circle sebagai dua fitur terpisah.'],
  ].map(x => `<article class="feature-card">${icon(x[0], 'feature-icon')}<div><h3>${x[1]}</h3><p>${x[2]}</p></div></article>`).join('')}</div><h2 class="section-title">Yang bisa dilakukan</h2><div class="capabilities">${[
    ['package', 'Cek Paket Aktif', 'Detail kuota, masa berlaku, serta unsubscribe dari paket yang didukung.'],
    ['store', 'Browse Store', 'Store segments, family list, packages, dan package detail.'],
    ['coin', 'Pembayaran Normal', 'Balance, DANA, ShopeePay, GoPay, OVO, dan QRIS.'],
    ['family', 'Family Plan', 'Lihat member, slot kosong, limit kuota, ganti dan hapus member.'],
    ['circle', 'XL Circle', 'Lihat group, member, quota, spending tracker, invitation, dan bonus.'],
    ['transaction', 'Transaksi', 'Tampilkan histori transaksi beserta metode dan status pembayarannya.'],
  ].map(x => `<article class="cap-card">${icon(x[0], 'feature-icon')}<h4>${x[1]}</h4><p>${x[2]}</p></article>`).join('')}</div><div class="landing-strip"><div class="strip-card"><span class="strip-icon">${icon('coin')}</span><div><span class="preview-label">Balance</span><strong>Dari akun XL aktif</strong></div></div><div class="strip-card"><span class="strip-icon">${icon('package')}</span><div><span class="preview-label">Quota</span><strong>DATA · VOICE · TEXT</strong></div></div><div class="strip-card"><span class="strip-icon">${icon('gift')}</span><div><span class="preview-label">Rewards</span><strong>Redeemables dari API</strong></div></div></div><footer class="public-footer"><div>${brand()}<p style="color:var(--muted);line-height:1.5">Web UI lokal untuk project me-cli-sunset. Fokus pada fungsi yang memang ada di program.</p></div><div><h5>Products</h5><a href="#/packages">My Packages</a><a href="#/store">Store</a></div><div><h5>Rewards</h5><a href="#/rewards">Redeemables</a><a href="#/bookmarks">Bookmarks</a></div><div><h5>Family</h5><a href="#/family">Family Plan</a><a href="#/circle">XL Circle</a></div><div><h5>Support</h5><a href="#/transactions">Transactions</a><a href="#/notifications">Notifications</a></div><div class="footer-note">Interface ini sengaja tidak menampilkan shortcut decoy, overwrite amount, atau loop purchase.</div></footer></main></div>`;
}

function authArt() {
  return `<section class="auth-art">${brand()}<h1>Masuk dengan nomor XL.</h1><p>Flow login tetap mengikuti program: nomor diawali 628, request OTP, lalu verifikasi 6 digit.</p><div class="auth-points"><div class="auth-point">${icon('lock', 'feature-icon')}<div><strong>OTP 6 digit</strong><span>Verifikasi sesuai endpoint CIAM yang sudah dipakai CLI.</span></div></div><div class="auth-point">${icon('user', 'feature-icon')}<div><strong>Multi-account</strong><span>Akun tersimpan tetap kompatibel dengan refresh-tokens.json.</span></div></div><div class="auth-point">${icon('refresh', 'feature-icon')}<div><strong>Account switcher</strong><span>Ganti akun tanpa mengubah struktur project lama.</span></div></div></div></section>`;
}

function loginPage() {
  const hasAccounts = state.accounts.length > 0;
  const fromDashboard = location.hash.includes('from=dashboard');
  const backBtn = fromDashboard 
    ? `<a href="#/dashboard" class="btn btn-ghost btn-small" style="align-self:flex-start;margin-bottom:16px;padding:0;color:var(--muted)">${icon('back')} Kembali ke Dashboard</a>`
    : `<a href="#/" class="btn btn-ghost btn-small" style="align-self:flex-start;margin-bottom:16px;padding:0;color:var(--muted)">${icon('back')} Kembali ke Home Page</a>`;
  app.innerHTML = `<div class="auth-page"><div class="auth-shell">${authArt()}<section class="auth-form">${backBtn}<h2>${hasAccounts ? 'Pilih atau tambah akun' : 'Login ke myXL'}</h2><p>${hasAccounts ? 'Gunakan akun tersimpan atau login dengan nomor baru.' : 'Masukkan nomor XL yang akan digunakan.'}</p>${hasAccounts ? `<div class="account-list">${state.accounts.map(a => `<div class="account-row ${a.active ? 'active' : ''}"><div><div class="account-number">${escapeHtml(a.number)}</div><div class="account-meta">${escapeHtml(a.subscription_type || 'XL')}${a.active ? ' · aktif' : ''}</div></div><div><button class="btn btn-secondary btn-small" data-switch-account="${a.number}">${a.active ? 'Masuk Dashboard' : 'Gunakan'}</button><button class="btn btn-ghost btn-small" data-remove-account="${a.number}">${icon('trash')}</button></div></div>`).join('')}</div><div style="height:1px;background:var(--line);margin:3px 0 22px"></div><button class="btn btn-secondary" style="width:100%" id="show-new-number">${icon('plus')} Tambahkan Nomor Baru</button>` : ''}<form id="login-form" style="${hasAccounts ? 'display:none;margin-top:20px' : ''}"><div class="field"><label>Nomor XL</label><input class="input" id="phone-number" placeholder="6281234567890" inputmode="numeric" maxlength="14" /></div><button class="btn btn-primary" style="width:100%" type="submit">Kirim OTP ${icon('arrow')}</button></form><div class="auth-note" id="login-note" style="${hasAccounts ? 'display:none' : ''}">Nomor harus diawali <strong>628</strong> dan berisi 10–14 digit.</div></section></div></div>`;
  $('#login-form').addEventListener('submit', requestOtp);
  if (hasAccounts) {
    $('#show-new-number').addEventListener('click', e => { e.target.style.display = 'none'; $('#login-form').style.display = 'block'; $('#login-note').style.display = 'block'; $('#phone-number').focus(); });
  }
}

async function requestOtp(e) {
  e.preventDefault();
  const number = $('#phone-number').value.trim();
  const btn = e.submitter;
  btn.disabled = true; btn.textContent = 'Mengirim OTP…';
  try {
    await api('/api/auth/request-otp', { method: 'POST', body: JSON.stringify({ number }) });
    state.loginNumber = number;
    state.otpTries = 5;
    location.hash = '#/otp';
  } catch (err) { toast(err.message, 'error'); }
  finally { btn.disabled = false; btn.innerHTML = `Kirim OTP ${icon('arrow')}`; }
}

function otpPage() {
  if (!state.loginNumber) { location.hash = '#/login'; return; }
  app.innerHTML = `<div class="auth-page"><div class="auth-shell">${authArt()}<section class="auth-form"><h2>Verifikasi OTP</h2><p>Kode verifikasi dikirim via SMS ke <strong>${escapeHtml(state.loginNumber)}</strong>.</p><form id="otp-form"><div class="field"><label>OTP 6 digit</label><div class="otp-boxes">${Array.from({ length: 6 }, (_, i) => `<input class="otp-box" inputmode="numeric" maxlength="1" data-otp="${i}" />`).join('')}</div></div><div style="display:flex;justify-content:space-between;color:var(--muted);font-size:12px;margin-bottom:18px"><span>Sisa percobaan: <strong id="tries">${state.otpTries}</strong></span><button class="link" type="button" data-action="resend-otp">Kirim ulang OTP</button></div><button class="btn btn-primary" style="width:100%" type="submit">Verifikasi & Masuk</button></form><button class="btn btn-ghost" style="margin-top:12px" data-action="back-login">${icon('arrow')} Ganti nomor</button></section></div></div>`;
  const boxes = $$('.otp-box');
  boxes.forEach((b, i) => {
    b.addEventListener('input', () => { b.value = b.value.replace(/\D/g, '').slice(0, 1); if (b.value && boxes[i + 1]) boxes[i + 1].focus(); });
    b.addEventListener('keydown', e => { if (e.key === 'Backspace' && !b.value && boxes[i - 1]) boxes[i - 1].focus(); });
  });
  boxes[0].focus();
  $('#otp-form').addEventListener('submit', submitOtpForm);
}

async function submitOtpForm(e) {
  e.preventDefault();
  const otp = $$('.otp-box').map(x => x.value).join('');
  if (otp.length !== 6) return toast('Masukkan 6 digit OTP.', 'error');
  const btn = e.submitter; btn.disabled = true; btn.textContent = 'Memverifikasi…';
  try {
    const data = await api('/api/auth/submit-otp', { method: 'POST', body: JSON.stringify({ number: state.loginNumber, otp }) });
    
    state.accounts.forEach(a => a.active = false);
    const existing = state.accounts.find(a => a.number == data.user.number);
    if (existing) {
       Object.assign(existing, data.user, { active: true, tokens: data.tokens });
    } else {
       state.accounts.push({ ...data.user, active: true, tokens: data.tokens });
    }
    saveAccounts();
    
    toast('Login berhasil.', 'success');
    location.hash = '#/dashboard';
  } catch (err) {
    state.otpTries = Math.max(0, state.otpTries - 1); $('#tries').textContent = state.otpTries;
    toast(err.message, 'error');
    if (state.otpTries <= 0) { setTimeout(() => location.hash = '#/login', 900); }
  } finally { btn.disabled = false; btn.textContent = 'Verifikasi & Masuk'; }
}

function renderBenefit(benefit) {
  const type = benefit.data_type || 'OTHER';
  let rem = benefit.remaining || 0, total = benefit.total || 0, label = '';
  if (benefit.is_unlimited) label = 'Unlimited';
  else if (type === 'DATA') label = `${fmtQuota(rem)} / ${fmtQuota(total)}`;
  else if (type === 'VOICE') label = `${Math.round(rem / 60)} / ${Math.round(total / 60)} menit`;
  else if (type === 'TEXT') label = `${rem} / ${total} SMS`;
  else label = `${rem} / ${total}`;
  const hasTotal = Number(total) > 0;
  const percent = hasTotal ? pct(rem, total) : (benefit.is_unlimited ? 100 : null);
  return { name: benefit.name || type, label, percent, type };
}

async function dashboardPage() {
  app.innerHTML = appShell('dashboard', 'Dashboard', 'Ringkasan akun dan fitur utama.', loading());
  try {
    const [dash, pkgData, txData] = await Promise.all([
      api('/api/dashboard'),
      api('/api/packages').catch(() => ({ packages: [] })),
      api('/api/transactions').catch(() => ({ transactions: [] })),
    ]);
    state.dashboard = dash; state.packages = pkgData.packages || []; state.unread = dash.unread_count || 0;
    const p = state.packages[0]; const benefits = (p?.benefits || []).slice(0, 3).map(renderBenefit);
    const mainData = benefits.find(x => x.type === 'DATA') || benefits[0];
    const tx = (txData.transactions || []).slice(0, 3);
    const body = `<section class="card dashboard-summary"><div class="summary-user"><div class="avatar-large">${String(dash.user.number).slice(-2)}</div><div class="sum-text"><strong class="sum-num">${escapeHtml(dash.user.number)}</strong><small class="sum-type">${escapeHtml(dash.user.subscription_type || 'PREPAID')}</small></div></div><div class="summary-divider"></div><div class="stat-block"><span class="stat-label">Balance</span><div class="stat-value">${fmtMoney(dash.balance.remaining)}</div><span class="preview-label">Aktif s.d. ${escapeHtml(dash.balance.expired_label)}</span></div><div class="summary-divider"></div><div class="stat-block"><span class="stat-label">Points</span><div class="stat-value">${escapeHtml(dash.points.current)}</div><span class="preview-label">Tier ${escapeHtml(dash.points.tier)}</span></div><div class="summary-divider"></div><div class="stat-block"><span class="stat-label">Notifications</span><div class="stat-value">${dash.unread_count || 0} unread</div><a href="#/notifications" class="link-blue">Lihat notifikasi ></a></div></section><div class="dash-grid">${p ? `<section class="package-hero"><div class="package-hero-content"><div class="package-eyebrow">${icon('package')} Paket aktif</div><h2>${escapeHtml(p.name || p.group_name || 'My Package')}</h2><p class="pkg-sub">${escapeHtml(p.group_name || 'Paket XL')}</p>${mainData && mainData.percent !== null ? `<div class="main-quota-wrap"><span class="main-quota-title">Total kuota utama</span><div class="main-quota-val">${escapeHtml(mainData.label.split(' / ')[0])}</div><div class="main-progress"><div class="main-progress-bar" style="width:${mainData.percent}%"></div></div></div>` : ''}<div class="benefit-row">${benefits.map(b => `<div class="benefit"><div class="benefit-top"><div class="b-icon-circle">${icon(b.ic)}</div><div class="b-text"><span class="b-name">${escapeHtml(b.name)}</span><span class="b-val">${escapeHtml(b.label)}</span></div></div>${b.percent !== null ? `<div class="benefit-bar"><i style="width:${b.percent}%"></i></div>` : ''}</div>`).join('')}</div><a href="#/packages" class="btn btn-white-pill">Lihat My Packages ></a></div></section>` : emptyState('Belum ada paket aktif', 'Data package quota-details tidak mengembalikan paket.', 'package')}<div class="side-stats"><section class="card widget-quick-actions"><div class="widget-head-qa">${icon('lightning')} Quick Actions</div><div class="qa-grid">${[['store', 'Beli Paket', 'store'], ['transactions', 'Transaksi', 'transaction'], ['family', 'Family Plan', 'family'], ['circle', 'XL Circle', 'circle']].map(([r, l, ic]) => `<a href="#/${r}" class="qa-btn"><div class="qa-icon-wrap">${icon(ic)}</div><span class="qa-label">${l}</span></a>`).join('')}</div></section><section class="card widget-notifications"><div class="w-rev-content"><div class="widget-head-qa">${icon('bell')} Notifikasi</div><div class="w-rev-points">${dash.unread_count || 0} unread</div><span class="preview-label">${dash.unread_count ? `<a href="#/notifications" class="link-blue">Lihat notifikasi ></a>` : 'Belum ada notifikasi baru'}</span></div><div class="w-rev-ill ill-bell">${icon('bell')}</div></section><section class="card widget-rewards"><div class="w-rev-content"><div class="widget-head-qa">${icon('gift')} Rewards</div><div class="w-rev-points">${escapeHtml(dash.points.current)} pts</div><a href="#/rewards" class="link-blue">Lihat redeemables ></a></div><div class="w-rev-ill">${icon('gift')}</div></section></div></div><div class="two-col"><div><div class="section-head"><h2>Recent Activity</h2><a href="#/transactions" class="link">Lihat semua</a></div>${tx.length ? `<div class="card list-card">${tx.map(renderTransactionRow).join('')}</div>` : emptyState('Belum ada transaksi', 'Riwayat transaksi belum tersedia.', 'transaction')}</div><div><div class="section-head"><h2>Bookmarks</h2><a href="#/bookmarks" class="link">Kelola</a></div><div id="dash-bookmarks">${loading()}</div></div></div><div class="section-head"><h2>Recommended Packages</h2><a href="#/store" class="link">Buka Store</a></div><div id="dash-recommended">${loading()}</div>`;
    app.innerHTML = appShell('dashboard', 'Dashboard', 'Ringkasan akun dan fitur utama.', body);
    loadDashboardExtras();
  } catch (err) { handleProtectedError(err); }
}

async function loadDashboardExtras() {
  try {
    const s = await api('/api/store/packages');
    const active = state.accounts.find(x => x.active) || state.accounts[0];
    const key = `bookmarks_${active ? active.number : ''}`;
    const bm = JSON.parse(localStorage.getItem(key) || '[]').slice(0, 2);
    $('#dash-bookmarks').innerHTML = bm.length ? `<div class="card list-card">${bm.map(x => `<div class="list-row">${icon('bookmark', 'list-icon')}<div class="list-main"><div class="list-title">${escapeHtml(x.family_name || x.option_name || 'Saved package')}</div><div class="list-sub">${escapeHtml(x.variant_name || '')} · ${escapeHtml(x.option_name || '')}</div></div></div>`).join('')}</div>` : emptyState('Belum ada bookmark', 'Simpan paket dari fitur bookmark agar tampil di sini.', 'bookmark');
    const pk = (s.data?.results_price_only || []).filter(x => x.action_type === 'PDP').slice(0, 3);
    $('#dash-recommended').innerHTML = pk.length ? `<div class="package-grid">${pk.map(renderStorePackage).join('')}</div>` : emptyState('Rekomendasi belum tersedia', 'Store API tidak mengembalikan paket.', 'store');
  } catch { }
}

function renderTransactionRow(t) {
  const status = (t.status || t.payment_status || '').toUpperCase();
  const cls = status.includes('SUCCESS') ? 'status-success' : status.includes('FAIL') ? 'status-failed' : 'status-pending';
  return `<div class="list-row" style="cursor:pointer" onclick="openTransactionModal('${encodeURIComponent(JSON.stringify(t)).replace(/'/g, "&#39;")}')">${icon('transaction', 'list-icon')}<div class="list-main"><div class="list-title">${escapeHtml(t.title || 'Transaction')}</div><div class="list-sub">${escapeHtml(t.payment_method_label || t.payment_method || '-')} · ${escapeHtml(t.formated_date || '')}</div></div><div class="list-right"><strong>${escapeHtml(t.price || fmtMoney(t.raw_price))}</strong><br><span class="${cls}">${escapeHtml(status || 'UNKNOWN')}</span></div></div>`;
}

function openTransactionModal(tData) {
  try {
    const t = JSON.parse(decodeURIComponent(tData));
    const status = (t.status || t.payment_status || '').toUpperCase();
    const cls = status.includes('SUCCESS') ? 'status-success' : status.includes('FAIL') ? 'status-failed' : 'status-pending';
    
    let txId = t.trx_code || t.code || t.transaction_id || t.id || '-';
    if (txId === 'to get detail') txId = '-';
    let timeStr = t.formated_date || '';
    if (!timeStr && t.timestamp) {
      const ms = t.timestamp > 1e11 ? t.timestamp : t.timestamp * 1000;
      timeStr = new Date(ms).toLocaleString('id-ID', { year: 'numeric', month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit' });
    }

    let qrTime = 0;
    try {
      const cached = JSON.parse(localStorage.getItem('cached_qris') || '{}');
      const c = cached[txId];
      if (c && !t.qr_png && !t.qr_code) {
        if (typeof c === 'string') { t.qr_png = c; qrTime = Date.now(); }
        else if (c.qr) { t.qr_code = c.qr; qrTime = c.time; }
        else { t.qr_png = c.img; qrTime = c.time; }
      }
    } catch(e) {}

    let qrHtml = '';
    const qrisLogo = `<img src="https://upload.wikimedia.org/wikipedia/commons/a/a2/Logo_QRIS.svg" style="position:absolute;top:50%;left:50%;transform:translate(-50%,-50%);width:40px;height:11px;background:#fff;padding:3px;border-radius:6px;box-shadow:0 2px 5px rgba(0,0,0,0.1)">`;
    
    const isExpired = qrTime && (Date.now() - qrTime > 30 * 60 * 1000);
    if (isExpired) {
      qrHtml = `<div class="qr-wrap" style="background:rgba(255,255,255,0.5);padding:16px;border-radius:12px;margin-bottom:16px;text-align:center"><div style="font-weight:600;font-size:13px">QR Code Kedaluwarsa</div><div style="font-size:11px;color:var(--muted);margin-top:4px;line-height:1.4">Waktu pembayaran 30 menit telah habis.</div></div>`;
    } else if (t.qr_png || t.qr_code) {
      const timerHtml = qrTime ? `<div id="qris-timer-${txId}" style="margin-top:8px;font-size:13px;color:var(--red);font-weight:700"></div>` : `<div style="margin-top:8px;font-weight:600;color:var(--ink)">Scan QRIS</div>`;
      const imgSrc = t.qr_png ? escapeHtml(t.qr_png) : `https://api.qrserver.com/v1/create-qr-code/?size=250x250&data=${encodeURIComponent(t.qr_code)}`;
      qrHtml = `<div class="qr-wrap" style="background:#fff;padding:12px;border-radius:12px;margin-bottom:16px;text-align:center"><div style="position:relative;display:inline-block"><img src="${imgSrc}" style="max-width:200px;border-radius:8px" alt="QRIS">${qrisLogo}</div>${timerHtml}</div>`;
    } else if ((t.payment_method || '').includes('QRIS') || (t.payment_method_label || '').includes('QRIS')) {
      qrHtml = `<div class="qr-wrap" style="background:rgba(255,255,255,0.5);padding:16px;border-radius:12px;margin-bottom:16px;text-align:center"><div style="font-weight:600;font-size:13px">QR Code tidak tersedia</div><div style="font-size:11px;color:var(--muted);margin-top:4px;line-height:1.4">API XL tidak menyimpan gambar QR Code pada riwayat transaksi ini.</div></div>`;
    }

    const body = `<div style="text-align:center;margin-bottom:20px"><div style="font-size:28px;font-weight:700;margin-bottom:12px;letter-spacing:-1px">${escapeHtml(t.price || fmtMoney(t.raw_price))}</div><span class="${cls}" style="padding:4px 12px;border-radius:20px;font-size:12px;display:inline-block">${escapeHtml(status || 'UNKNOWN')}</span></div>${qrHtml}<div style="background:var(--soft);border-radius:12px;padding:16px;font-size:13px"><div style="display:flex;justify-content:space-between;margin-bottom:12px;border-bottom:1px solid var(--line);padding-bottom:12px"><span style="color:var(--muted)">Item</span><strong style="text-align:right;max-width:200px">${escapeHtml(t.title || 'Transaction')}</strong></div><div style="display:flex;justify-content:space-between;margin-bottom:12px;border-bottom:1px solid var(--line);padding-bottom:12px"><span style="color:var(--muted)">Waktu</span><strong style="text-align:right">${escapeHtml(timeStr)}</strong></div><div style="display:flex;justify-content:space-between;margin-bottom:12px;border-bottom:1px solid var(--line);padding-bottom:12px"><span style="color:var(--muted)">Metode Pembayaran</span><strong style="text-align:right">${escapeHtml(t.payment_method_label || t.payment_method || '-')}</strong></div><div style="display:flex;justify-content:space-between"><span style="color:var(--muted);flex-shrink:0;margin-right:12px">Transaction ID</span><strong style="text-align:right;word-break:break-all">${escapeHtml(txId)}</strong></div></div>`;
    showModal('Detail Transaksi', body);
    
    if (qrTime && !isExpired) {
      const tmr = document.getElementById(`qris-timer-${txId}`);
      if (tmr) {
        const updateTmr = () => {
          if (!document.contains(tmr)) return;
          const rem = Math.floor((30 * 60 * 1000 - (Date.now() - qrTime)) / 1000);
          if (rem <= 0) {
            tmr.textContent = 'Kedaluwarsa';
            tmr.style.color = 'var(--muted)';
          } else {
            const m = Math.floor(rem / 60).toString().padStart(2, '0');
            const s = (rem % 60).toString().padStart(2, '0');
            tmr.textContent = `Sisa Waktu: ${m}:${s}`;
            setTimeout(updateTmr, 1000);
          }
        };
        updateTmr();
      }
    }
  } catch(e) {}
}

async function packagesPage() {
  app.innerHTML = appShell('packages', 'My Packages', 'Paket aktif dan benefit yang tersedia.', loading());
  try {
    const data = await api('/api/packages'); state.packages = data.packages || [];
    const body = state.packages.length ? `<div class="package-grid">${state.packages.map((p, i) => { const bs = (p.benefits || []).map(renderBenefit); return `<article class="card info-card"><h3 style="margin:0 0 16px">${escapeHtml(p.name || `Package ${i + 1}`)}</h3>${bs.slice(0, 3).map(b => `<div class="progress-row"><div class="progress-label"><span style="white-space:nowrap;overflow:hidden;text-overflow:ellipsis">${escapeHtml(b.name)}</span><strong>${escapeHtml(b.label)}</strong></div><div class="progress"><i style="width:${b.percent}%"></i></div></div>`).join('')}<div style="display:flex;gap:8px;margin-top:auto;padding-top:18px"><button class="btn btn-primary btn-small" style="flex:1" data-package-detail="${escapeHtml(p.quota_code)}">Detail</button>${p.product_domain || p.product_subscription_type ? `<button class="btn btn-secondary btn-small" style="flex:1" data-unsubscribe='${JSON.stringify({ quota_code: p.quota_code, product_domain: p.product_domain || '', product_subscription_type: p.product_subscription_type || '' }).replace(/'/g, '&#39;')}'>Berhenti</button>` : ''}</div></article>` }).join('')}</div>` : emptyState('Tidak ada paket aktif', 'quota-details tidak mengembalikan paket untuk akun ini.', 'package', '<a href="#/store" class="btn btn-primary" style="margin-top:15px">Buka Store</a>');
    app.innerHTML = appShell('packages', 'My Packages', 'Paket aktif dan benefit yang tersedia.', body);
  } catch (err) { handleProtectedError(err) }
}

function renderStorePackage(p) {
  const price = Number(p.discounted_price || 0) > 0 ? p.discounted_price : p.original_price || 0;
  return `<article class="card package-card"><div class="package-card-top"><span class="tag">${escapeHtml(p.family_name || 'XL Package')}</span><h3>${escapeHtml(p.title || 'Package')}</h3></div><div class="package-card-body"><div class="family">${escapeHtml(p.family_name || '')}</div><div class="package-name">${escapeHtml(p.title || 'Package')}</div><div class="package-meta"><span>${escapeHtml(p.validity || '-')}</span></div><div class="package-price" style="margin-top:12px"><span>${fmtMoney(price)}</span>${p.action_type === 'PDP' ? `<button class="round-action" data-package-detail="${escapeHtml(p.action_param)}">${icon('plus')}</button>` : p.action_type === 'PLP' ? `<button class="round-action" data-family-detail="${escapeHtml(p.action_param)}">${icon('arrow')}</button>` : ''}</div></div></article>`;
}

async function storePage() {
  app.innerHTML = appShell('store', 'Store', 'Package families, store packages, dan browse detail.', loading());
  try {
    const [pk, fam, seg] = await Promise.all([api('/api/store/packages'), api('/api/store/families').catch(() => ({ data: { results: [] } })), api('/api/store/segments').catch(() => ({ data: { store_segments: [] } }))]);
    state.storePackages = pk.data?.results_price_only || []; state.families = fam.data?.results || []; state.segments = seg.data?.store_segments || [];
    const body = `<div class="card page-card"><div class="tabs"><button class="tab active" data-store-tab="packages">Packages</button><button class="tab" data-store-tab="families">Family List</button><button class="tab" data-store-tab="segments">Segments</button><button class="tab" data-store-tab="search">Cari Kode</button></div><div class="filter-bar"><div class="search-input">${icon('search')}<input id="store-search" class="input" placeholder="Cari package name…" /></div></div><div id="store-content">${renderStorePackages(state.storePackages)}</div></div>`;
    app.innerHTML = appShell('store', 'Store', 'Package families, store packages, dan browse detail.', body);
    $('#store-search').addEventListener('input', e => { const q = e.target.value.toLowerCase(); $('#store-content').innerHTML = renderStorePackages(state.storePackages.filter(p => (p.title || '').toLowerCase().includes(q) || (p.family_name || '').toLowerCase().includes(q))); });
  } catch (err) { handleProtectedError(err) }
}

function renderStorePackages(list) {
  const items = list.filter(x => ['PDP', 'PLP'].includes(x.action_type)).slice(0, 18);
  return items.length ? `<div class="package-grid">${items.map(renderStorePackage).join('')}</div>` : emptyState('Paket tidak ditemukan', 'Coba family list atau akun lain.', 'store');
}

function renderFamilies() {
  return state.families.length ? `<div class="package-grid">${state.families.map(f => `<article class="card package-card"><div class="package-card-top"><span class="tag">Family</span><h3>${escapeHtml(f.label || 'Package Family')}</h3></div><div class="package-card-body"><div class="package-meta" style="padding-top:0"><span style="word-break:break-all;line-height:1.4">ID: <strong style="font-weight:600">${escapeHtml(f.id || '')}</strong></span></div><div class="package-price" style="margin-top:12px;justify-content:flex-end"><button class="round-action" data-family-detail="${escapeHtml(f.id)}">${icon('arrow')}</button></div></div></article>`).join('')}</div>` : emptyState('Family list kosong', 'API tidak mengembalikan family list.', 'package');
}

function renderSearchCode() {
  return `<div class="card info-card" style="margin-top:20px;max-width:500px;margin-inline:auto">
    <h3 style="margin-bottom:12px;text-align:center">Cari Kode Langsung</h3>
    <p style="color:var(--muted);margin-bottom:20px;text-align:center">Masukkan kode untuk membuka paket atau family plan (sama seperti menu CLI).</p>
    <div style="margin-bottom:16px">
      <input id="manual-code-input" class="input" style="width:100%" placeholder="Misal: 8111317 (Option) atau 72X03 (Family)" />
    </div>
    <div style="display:flex;gap:8px">
      <button class="btn btn-primary" style="flex:1" data-action="search-option-code">Buka Option Code</button>
      <button class="btn btn-secondary" style="flex:1" data-action="search-family-code">Buka Family Code</button>
    </div>
  </div>`;
}

function renderSegments() {
  if (!state.segments.length) return emptyState('Store segments kosong', 'API tidak mengembalikan segment/banner.', 'store');
  return state.segments.slice(0, 8).map(seg => `<section><div class="section-head"><h2>${escapeHtml(seg.title || 'Store Segment')}</h2></div><div class="package-grid">${(seg.banners || []).filter(b => ['PDP', 'PLP'].includes(b.action_type)).slice(0, 6).map(b => renderStorePackage({ ...b, original_price: b.discounted_price || b.original_price || 0 })).join('')}</div></section>`).join('');
}

async function transactionsPage() {
  app.innerHTML = appShell('transactions', 'Transactions', 'Riwayat transaksi dari payment history.', loading());
  try { const data = await api('/api/transactions'); const tx = data.transactions || []; const body = tx.length ? `<div class="card list-card">${tx.map(renderTransactionRow).join('')}</div>` : emptyState('Belum ada transaksi', 'Riwayat pembayaran belum tersedia.', 'transaction'); app.innerHTML = appShell('transactions', 'Transactions', 'Riwayat transaksi dari payment history.', body); } catch (err) { handleProtectedError(err) }
}

async function familyPage() {
  app.innerHTML = appShell('family', 'Family Plan', 'Akrab Organizer: shared quota, slots, dan member.', loading());
  try {
    const res = await api('/api/family-plan'); const m = res.data?.member_info;
    if (!m || !m.plan_type) { app.innerHTML = appShell('family', 'Family Plan', 'Akrab Organizer: shared quota, slots, dan member.', emptyState('Bukan Family Plan Organizer', 'Akun aktif tidak memiliki role organizer Family Plan.', 'family')); return; }
    const members = m.members || [], total = Number(m.total_quota) || 0, remaining = Number(m.remaining_quota) || 0;
    const body = `<section class="card family-header"><div class="family-main"><span class="mini-badge">${escapeHtml(m.plan_type)}</span><h2 style="margin-top:12px">Family Plan</h2><p>Parent: ${escapeHtml(m.parent_msisdn || '-')}</p><div class="family-quota"><div class="progress-label"><span>Shared Quota</span><strong>${fmtQuota(remaining)} / ${fmtQuota(total)}</strong></div><div class="progress"><i style="width:${pct(remaining, total)}%"></i></div></div></div><div class="stat-block"><span class="stat-label">Members</span><div class="stat-value">${members.filter(x => x.msisdn).length} / ${members.length}</div><span class="preview-label">Slot terisi</span></div></section><div class="section-head"><h2>Members & Slots</h2></div><div class="member-grid">${members.map((mem, i) => { const usage = mem.usage || {}, alloc = usage.quota_allocated || 0, used = usage.quota_used || 0; return `<article class="card member-card"><span class="avatar">${mem.msisdn ? String(mem.msisdn).slice(-2) : '+'}</span><div class="member-main"><strong>${escapeHtml(mem.msisdn || 'Empty Slot')}</strong><small>${escapeHtml(mem.alias || `Slot ${i + 1}`)} · ${escapeHtml(mem.member_type || '')}</small></div><div class="member-quota"><strong>${mem.msisdn ? `${fmtQuota(used)} / ${fmtQuota(alloc)}` : 'Available'}</strong>${mem.msisdn ? `<div style="margin-top:7px"><button class="link" data-family-limit='${JSON.stringify({ family_member_id: mem.family_member_id, original_allocation: alloc, slot: i + 1 }).replace(/'/g, '&#39;')}'>Limit</button><button class="link" style="color:var(--red)" data-family-remove="${escapeHtml(mem.family_member_id || '')}">Hapus</button></div>` : `<button class="link" data-family-add='${JSON.stringify({ family_member_id: mem.family_member_id, slot_id: mem.slot_id, slot: i + 1 }).replace(/'/g, '&#39;')}'>Tambah member</button>`}</div></article>` }).join('')}</div>`;
    app.innerHTML = appShell('family', 'Family Plan', 'Akrab Organizer: shared quota, slots, dan member.', body);
  } catch (err) { handleProtectedError(err) }
}

async function circlePage() {
  app.innerHTML = appShell('circle', 'XL Circle', 'Group, member, quota, spending tracker, dan bonus.', loading());
  try {
    const res = await api('/api/circle'); const d = res.data || {}, g = d.group || {};
    if (!g.group_id) { app.innerHTML = appShell('circle', 'XL Circle', 'Group, member, quota, spending tracker, dan bonus.', emptyState('Belum berada dalam Circle', 'Akun aktif belum punya group Circle. Buat Circle baru dengan satu member awal.', 'circle', '<button class="btn btn-primary" style="margin-top:15px" data-action="create-circle">Buat Circle</button>')); return; }
    const members = d.members || [], pack = d.package || {}, ben = pack.benefit || {}, spend = d.spending || {};
    const body = `<section class="package-hero" style="min-height:230px"><div class="package-hero-content"><div class="package-eyebrow">${icon('circle')} ${escapeHtml(g.group_status || 'ACTIVE')}</div><h2>${escapeHtml(g.group_name || 'XL Circle')}</h2><p>Owner: ${escapeHtml(g.owner_name || '-')}</p><div class="quota-main"><span>${escapeHtml(pack.name || 'Circle package')}</span><strong>${fmtQuota(ben.remaining || 0)} / ${fmtQuota(ben.allocation || 0)}</strong><div class="quota-bar"><i style="width:${pct(ben.remaining, ben.allocation)}%"></i></div></div></div></section><div class="cards-4" style="margin-top:16px"><article class="card info-card"><h3>Members</h3><div class="stat-value">${members.length}</div><p>Member dalam Circle</p></article><article class="card info-card"><h3>Spending</h3><div class="stat-value">${fmtMoney(spend.spend || 0)}</div><p>Target ${fmtMoney(spend.target || 0)}</p></article><article class="card info-card"><h3>Bonuses</h3><div class="stat-value">${(d.bonuses || []).length}</div><p>Bonus Circle tersedia</p></article><article class="card info-card"><h3>Invite</h3><button class="btn btn-primary btn-small" style="margin-top:12px" data-circle-invite='${JSON.stringify({ group_id: g.group_id, parent_member_id: d.parent_member_id }).replace(/'/g, '&#39;')}'>Invite member</button></article></div><div class="section-head"><h2>Members</h2></div><div class="member-grid">${members.map((m, i) => `<article class="card member-card"><span class="avatar">${String(m.plain_msisdn || m.member_name || i + 1).slice(-2)}</span><div class="member-main"><strong>${escapeHtml(m.member_name || m.plain_msisdn || 'Member')}</strong><small>${escapeHtml(m.plain_msisdn || '')} · ${escapeHtml(m.member_role || 'MEMBER')} · ${escapeHtml(m.status || '')}</small></div><div class="member-quota"><strong>${fmtQuota(m.remaining || 0)} / ${fmtQuota(m.allocation || 0)}</strong>${m.member_role !== 'PARENT' ? `<div style="margin-top:7px">${m.status === 'INVITED' ? `<button class="link" data-circle-accept='${JSON.stringify({ group_id: g.group_id, member_id: m.member_id }).replace(/'/g, '&#39;')}'>Terima</button>` : ''}<button class="link" style="color:var(--red)" data-circle-remove='${JSON.stringify({ group_id: g.group_id, member_id: m.member_id, parent_member_id: d.parent_member_id, is_last_member: members.length === 2 }).replace(/'/g, '&#39;')}'>Hapus</button></div>` : ''}</div></article>`).join('')}</div>${(d.bonuses || []).length ? `<div class="section-head"><h2>Circle Bonuses</h2></div><div class="rewards-grid">${d.bonuses.slice(0, 6).map(b => `<article class="card reward-card"><span class="mini-badge">${escapeHtml(b.bonus_type || 'Bonus')}</span><h3>${escapeHtml(b.name || 'Circle Bonus')}</h3><p>${escapeHtml(b.action_type || '')} · ${escapeHtml(b.action_param || '')}</p>${b.action_type === 'PDP' ? `<button class="link" data-package-detail="${escapeHtml(b.action_param)}">Lihat detail</button>` : b.action_type === 'PLP' ? `<button class="link" data-family-detail="${escapeHtml(b.action_param)}">Lihat family</button>` : ''}</article>`).join('')}</div>` : ''}`;
    app.innerHTML = appShell('circle', 'XL Circle', 'Group, member, quota, spending tracker, dan bonus.', body);
  } catch (err) { handleProtectedError(err) }
}

async function rewardsPage() {
  app.innerHTML = appShell('rewards', 'Rewards', 'Redeemables yang tersedia untuk akun aktif.', loading());
  try {
    const res = await api('/api/rewards'); const cats = res.data?.categories || [];
    const activeCats = cats.filter(c => c.redeemables && c.redeemables.length > 0);
    const body = activeCats.length ? activeCats.map(c => `<section><div class="section-head"><div><h2>${escapeHtml(c.category_name || 'Rewards')}</h2><p>${escapeHtml(c.category_code || '')}</p></div></div><div class="rewards-grid">${c.redeemables.map(r => `<article class="card reward-card" style="display:flex;flex-direction:column"><span class="mini-badge">${escapeHtml(r.action_type || 'Reward')}</span><h3>${escapeHtml(r.name || 'Redeemable')}</h3><p>Valid sampai ${r.valid_until ? new Date(r.valid_until * 1000).toLocaleDateString('id-ID') : '-'}</p>${r.action_param ? `<div style="margin-top:auto;display:flex;justify-content:flex-end;padding-top:12px"><button class="round-action" ${r.action_type === 'PDP' ? `data-package-detail="${escapeHtml(r.action_param)}"` : `data-family-detail="${escapeHtml(r.action_param)}"`}>${icon('arrow')}</button></div>` : ''}</article>`).join('')}</div></section>`).join('') : emptyState('Tidak ada redeemables', 'Akun aktif belum memiliki reward/redeemable.', 'gift');
    app.innerHTML = appShell('rewards', 'Rewards', 'Redeemables yang tersedia untuk akun aktif.', body);
  } catch (err) { handleProtectedError(err) }
}

async function bookmarksPage() {
  app.innerHTML = appShell('bookmarks', 'Bookmarks', 'Paket yang disimpan dari store.', loading());
  try { 
    const active = state.accounts.find(x => x.active) || state.accounts[0];
    const key = `bookmarks_${active ? active.number : ''}`;
    const b = JSON.parse(localStorage.getItem(key) || '[]'); 
    const body = b.length ? `<div class="cards-4">${b.map(x => `<article class="card info-card"><span class="mini-badge">Bookmark</span><h3 style="font-size:16px;margin-top:12px">${escapeHtml(x.family_name || x.option_name || 'Package')}</h3><p>${escapeHtml(x.variant_name || '')} · ${escapeHtml(x.option_name || '')}</p><div style="display:flex;gap:8px;margin-top:15px"><button class="btn btn-secondary btn-small" data-family-detail="${escapeHtml(x.family_code)}">Buka Family</button><button class="btn btn-ghost btn-small" style="color:var(--red)" data-bookmark-remove='${JSON.stringify(x).replace(/'/g, '&#39;')}'>${icon('trash')}</button></div></article>`).join('')}</div>` : emptyState('Belum ada bookmark', 'Bookmark yang disimpan akan tampil di sini.', 'bookmark'); 
    app.innerHTML = appShell('bookmarks', 'Bookmarks', 'Paket yang disimpan dari store.', body); 
  } catch (err) { toast(err.message, 'error') }
}

function openNotificationModal(nData) {
  try {
    const n = JSON.parse(decodeURIComponent(nData));
    const title = n.brief_message || 'Notification';
    const msg = String(n.full_message || '').replace(/\n/g, '<br/>');
    let btnHtml = '';
    if (n.action_url) btnHtml = `<a href="${escapeHtml(n.action_url)}" target="_blank" class="btn btn-primary" style="margin-top:20px;width:100%;text-align:center">Buka Tautan</a>`;
    const body = `<div style="text-align:center;margin-bottom:24px"><div style="display:inline-flex;align-items:center;justify-content:center;width:64px;height:64px;background:rgba(255,255,255,0.1);border-radius:16px;color:var(--blue-700);margin-bottom:16px">${icon('bell')}</div><h3 style="font-size:20px;margin-bottom:8px">${escapeHtml(title)}</h3><p style="color:var(--muted);font-size:12px">${escapeHtml(n.timestamp || '')}</p></div><div style="background:var(--soft);padding:16px;border-radius:12px;font-size:14px;line-height:1.6;color:var(--ink);text-align:left">${msg}</div>${btnHtml}`;
    showModal('Detail Notifikasi', body);
  } catch(e) {}
}

async function notificationsPage() {
  app.innerHTML = appShell('notifications', 'Notifications', 'Notifikasi dashboard dan status read/unread.', loading());
  try { const res = await api('/api/notifications'); const n = res.notifications || []; state.unread = n.filter(x => !x.is_read).length; const body = `<div class="section-head"><div><h2>${n.length} notifikasi</h2><p>${state.unread} belum dibaca</p></div>${state.unread ? '<button class="btn btn-secondary btn-small" data-action="read-all">Tandai semua dibaca</button>' : ''}</div>${n.length ? `<div class="card list-card">${n.map(x => `<div class="list-row" style="cursor:pointer" onclick="openNotificationModal('${encodeURIComponent(JSON.stringify(x)).replace(/'/g, "&#39;")}')">${icon('bell', 'list-icon')}<div class="list-main" style="min-width:0"><div class="list-title">${!x.is_read ? '<span style="color:var(--blue-700)">● </span>' : ''}${escapeHtml(x.brief_message || 'Notification')}</div><div class="list-sub" style="white-space:nowrap;overflow:hidden;text-overflow:ellipsis">${escapeHtml(x.full_message || '')}</div></div><div class="list-right" style="white-space:nowrap">${escapeHtml(x.timestamp || '')}</div></div>`).join('')}</div>` : emptyState('Tidak ada notifikasi', 'Dashboard segments tidak mengembalikan notifikasi.', 'bell')}`; app.innerHTML = appShell('notifications', 'Notifications', 'Notifikasi dashboard dan status read/unread.', body); } catch (err) { handleProtectedError(err) }
}

function supportPage() {
  const body = `<div class="two-col"><section class="card page-card"><h2 style="margin-top:0">Tentang Web UI</h2><p style="color:var(--muted);line-height:1.7">Web UI ini tidak mengganti CLI. Ia menjadi interface lokal yang memakai endpoint dan file token yang sama. Menu eksperimen seperti decoy, overwrite amount, dan loop purchase tidak diekspos.</p><div class="section-head"><h2>Flow tersedia</h2></div><div class="list-card">${[['lock', 'Login OTP', '628… → request OTP → verifikasi 6 digit'], ['package', 'Package & Store', 'Paket aktif, family list, store packages, redeemables'], ['coin', 'Payment', 'BALANCE, DANA, ShopeePay, GoPay, OVO, QRIS'], ['family', 'Family Plan & Circle', 'Family Plan dan XL Circle tetap dua fitur berbeda']].map(x => `<div class="list-row">${icon(x[0], 'list-icon')}<div class="list-main"><div class="list-title">${x[1]}</div><div class="list-sub">${x[2]}</div></div></div>`).join('')}</div></section><section class="card page-card"><h2 style="margin-top:0">Advanced tools</h2><p style="color:var(--muted);font-size:12px">Dua utilitas yang memang ada di program, diletakkan di sini supaya sidebar tidak ramai.</p><form id="validate-form"><div class="field"><label>Validate MSISDN</label><input id="validate-msisdn" class="input" placeholder="6281234567890" /></div><button class="btn btn-secondary" type="submit">Validate</button></form><hr style="border:0;border-top:1px solid var(--line);margin:25px 0"><form id="register-form"><h3>Register Dukcapil</h3><div class="field"><label>MSISDN</label><input id="reg-msisdn" class="input" placeholder="628…" /></div><div class="field"><label>NIK</label><input id="reg-nik" class="input" /></div><div class="field"><label>KK</label><input id="reg-kk" class="input" /></div><button class="btn btn-primary" type="submit">Kirim Registrasi</button></form></section></div>`;
  app.innerHTML = appShell('support', 'Support & Tools', 'Info web UI dan utilitas program yang tidak perlu memenuhi sidebar.', body);
  $('#validate-form').addEventListener('submit', async e => { e.preventDefault(); try { const r = await api('/api/tools/validate-msisdn', { method: 'POST', body: JSON.stringify({ msisdn: $('#validate-msisdn').value.trim() }) }); showJsonModal('Hasil Validate MSISDN', r); } catch (err) { toast(err.message, 'error') } });
  $('#register-form').addEventListener('submit', async e => { e.preventDefault(); try { const r = await api('/api/tools/register', { method: 'POST', body: JSON.stringify({ msisdn: $('#reg-msisdn').value.trim(), nik: $('#reg-nik').value.trim(), kk: $('#reg-kk').value.trim() }) }); showJsonModal('Hasil Registrasi', r); } catch (err) { toast(err.message, 'error') } });
}

async function openFamily(code) {
  showModal('Package Family', loading());
  try { const res = await api(`/api/family/${encodeURIComponent(code)}`); const d = res.data || {}, fam = d.package_family || {}, vars = d.package_variants || []; const body = `<div class="detail-hero"><div class="family">Family</div><h3>${escapeHtml(fam.name || code)}</h3><p>${escapeHtml(fam.package_family_type || '')}</p></div>${vars.map(v => `<div class="section-head"><h2>${escapeHtml(v.name || 'Variant')}</h2></div><div class="cards-4">${(v.package_options || []).map(o => `<article class="card info-card"><h3>${escapeHtml(o.name || 'Option')}</h3><p>Order ${escapeHtml(o.order)}</p><div class="package-price"><span>${fmtMoney(o.price)}</span><button class="round-action" data-package-detail="${escapeHtml(o.package_option_code)}">${icon('arrow')}</button></div></article>`).join('')}</div>`).join('')}`; setModalBody(body); } catch (err) { setModalBody(emptyState('Gagal membuka family', err.message, 'package')); }
}

async function openPackage(code) {
  showModal('Detail Paket', loading());
  try {
    const res = await api(`/api/package/${encodeURIComponent(code)}`), p = res.package || {}, opt = p.package_option || {}, fam = p.package_family || {}, vari = p.package_detail_variant || {}, benefits = opt.benefits || [];
    const bookmarkData = { family_code: fam.code || fam.id || fam.package_family_code || '', family_name: fam.name || '', variant_name: vari.name || '', option_name: opt.name || '', order: 0, is_enterprise: false };
    const famCode = fam.code || fam.id || fam.package_family_code || '-';
    const body = `<div class="detail-hero">${famCode !== '-' ? `<button class="btn btn-small" style="background:rgba(255,255,255,0.2);color:#fff;border:none;margin-bottom:12px;padding:6px 12px" onclick="openFamily('${escapeHtml(famCode)}')">${icon('back')} Kembali ke Family</button>` : ''}<div class="family">${escapeHtml(fam.name || 'XL Package')}</div><h3>${escapeHtml([vari.name, opt.name].filter(Boolean).join(' · ') || opt.name || code)}</h3><div style="font-size:12px;margin:12px 0;background:rgba(255,255,255,0.15);padding:10px;border-radius:8px;word-break:break-all;text-align:left"><div style="margin-bottom:6px"><strong>Option Code:</strong><br/><span style="font-family:monospace;opacity:0.9">${escapeHtml(code)}</span></div><div><strong>Family Code:</strong><br/><span style="font-family:monospace;opacity:0.9">${escapeHtml(famCode)}</span></div></div><p style="margin-bottom:4px">Masa aktif: <strong>${escapeHtml(opt.validity || '-')}</strong> · ${escapeHtml(fam.plan_type || '')}</p><div class="detail-price">${fmtMoney(opt.price || 0)}</div></div><div class="benefits-list">${benefits.map(b => { const x = renderBenefit(b); return `<div class="benefit-light"><strong>${escapeHtml(x.name)}</strong><small>${escapeHtml(x.label)}</small></div>` }).join('') || '<div class="benefit-light"><strong>Benefit</strong><small>Data benefit tidak tersedia.</small></div>'}</div><div style="display:flex;gap:8px"><button class="btn btn-primary" style="flex:1" data-buy-package="${escapeHtml(code)}">Beli Paket</button><button class="btn btn-secondary" data-bookmark-add='${JSON.stringify(bookmarkData).replace(/'/g, '&#39;')}'>Simpan Paket</button></div>${opt.tnc ? `<div style="margin-top:24px;border-top:1px solid var(--line);padding-top:16px"><h4 style="margin-bottom:12px;font-size:14px">Syarat & Ketentuan</h4><div style="color:var(--muted);font-size:12px;line-height:1.6;white-space:pre-wrap">${String(opt.tnc).replace(/<br\s*\/?>/ig, '\n').replace(/<[^>]*>/g, '').trim()}</div></div>` : ''}`;
    setModalBody(body);
  } catch (err) { setModalBody(emptyState('Gagal mengambil detail paket', err.message, 'package')); }
}

function checkoutModal(code) {
  const body = `<div class="field"><label>Metode pembayaran</label><div class="payment-methods">${[['BALANCE', 'Pulsa / Balance'], ['QRIS', 'QRIS'], ['DANA', 'DANA'], ['SHOPEEPAY', 'ShopeePay'], ['GOPAY', 'GoPay'], ['OVO', 'OVO']].map(([v, l], i) => `<label class="payment-method"><input type="radio" name="pay-method" value="${v}" ${i === 0 ? 'checked' : ''}><strong>${l}</strong></label>`).join('')}</div></div><div class="field" id="wallet-field" style="display:none"><label>Nomor e-wallet</label><input id="wallet-number" class="input" placeholder="08xxxxxxxxxx" /></div><button class="btn btn-primary" style="width:100%" id="pay-submit">Lanjutkan Pembayaran</button><p class="auth-note">Pembelian ini memakai settlement normal dari program. Tidak ada overwrite amount atau decoy.</p>`;
  showModal('Checkout', body);
  $$('input[name=pay-method]').forEach(r => r.addEventListener('change', () => { $('#wallet-field').style.display = ['DANA', 'OVO'].includes(r.value) && r.checked ? 'grid' : 'none'; }));
  $('#pay-submit').addEventListener('click', async () => { const method = $('input[name=pay-method]:checked').value; const wallet = $('#wallet-number')?.value.trim() || ''; const btn = $('#pay-submit'); btn.disabled = true; btn.textContent = 'Memproses…'; try { const res = await api('/api/purchase', { method: 'POST', body: JSON.stringify({ option_code: code, method, wallet_number: wallet }) }); if (method === 'QRIS' && res.qr_png) { try { const cached = JSON.parse(localStorage.getItem('cached_qris') || '{}'); cached[res.transaction_id] = { qr: res.qris, time: Date.now() }; localStorage.setItem('cached_qris', JSON.stringify(cached)); } catch(e){} const qrisLogo = `<img src="https://upload.wikimedia.org/wikipedia/commons/a/a2/Logo_QRIS.svg" style="position:absolute;top:50%;left:50%;transform:translate(-50%,-50%);width:50px;height:14px;background:#fff;padding:4px;border-radius:6px;box-shadow:0 2px 5px rgba(0,0,0,0.1)">`; setModalBody(`<div class="qr-wrap" style="text-align:center"><div style="position:relative;display:inline-block"><img src="${res.qr_png}" alt="QRIS" style="max-width:250px;border-radius:8px">${qrisLogo}</div><h3 style="margin-top:16px">Scan QRIS</h3><p style="color:var(--muted);font-size:12px;word-break:break-all;margin-top:8px;background:var(--soft);padding:10px;border-radius:8px">Transaction ID:<br><strong>${escapeHtml(res.transaction_id)}</strong></p></div>`); return; } const deeplink = res.result?.data?.deeplink; if (deeplink) { setModalBody(`<div class="empty">${icon('check', 'feature-icon')}<h3>Pembayaran dibuat</h3><p>Selesaikan pembayaran melalui e-wallet.</p><a class="btn btn-primary" href="${escapeHtml(deeplink)}" target="_blank" rel="noopener" style="margin-top:16px">Buka E-Wallet</a></div>`); return; } if (res.ok) { setModalBody(emptyState('Transaksi berhasil dibuat', 'Cek My Packages atau Transactions untuk status terbaru.', 'check')); } else { throw new Error('Settlement tidak berhasil.'); } } catch (err) { toast(err.message, 'error'); btn.disabled = false; btn.textContent = 'Lanjutkan Pembayaran'; } });
}

function showModal(title, body) { modalRoot.innerHTML = `<div class="modal-backdrop"><div class="modal"><div class="modal-head"><h2>${escapeHtml(title)}</h2><button class="close-btn" data-action="close-modal">${icon('close')}</button></div><div class="modal-body">${body}</div></div></div>`; }
function setModalBody(body) { const x = $('.modal-body', modalRoot); if (x) x.innerHTML = body; }
function closeModal() { modalRoot.innerHTML = ''; }
function showJsonModal(title, data) { showModal(title, `<pre style="white-space:pre-wrap;word-break:break-word;background:var(--soft);padding:16px;border-radius:13px;font-size:11px;max-height:60vh;overflow:auto">${escapeHtml(JSON.stringify(data, null, 2))}</pre>`); }

async function showAccountsModal() {
  await loadAccounts();
  showModal('Pilih Akun', state.accounts.length ? `<div class="account-list">${state.accounts.map(a => `<div class="account-row ${a.active ? 'active' : ''}"><div><div class="account-number">${escapeHtml(a.number)}</div><div class="account-meta">${escapeHtml(a.subscription_type || 'XL')} ${a.active ? '· aktif' : ''}</div></div><div>${a.active ? '<span class="mini-badge" style="margin-right:8px">Aktif</span>' : `<button class="btn btn-secondary btn-small" data-switch-account="${a.number}" style="margin-right:8px">Gunakan</button>`}<button class="btn btn-ghost btn-small" data-remove-account="${a.number}">${icon('trash')}</button></div></div>`).join('')}</div><button class="btn btn-primary" style="width:100%" data-action="add-account">${icon('plus')} Tambah Akun</button>` : `${emptyState('Belum ada akun', 'Tambahkan akun XL untuk melanjutkan.', 'user')}<button class="btn btn-primary" style="width:100%" data-action="add-account">Tambah Akun</button>`);
}

async function switchAccount(number) {
  try { 
    state.accounts.forEach(a => a.active = (a.number == number));
    saveAccounts();
    closeModal(); 
    toast('Akun diaktifkan.', 'success'); 
    if (routeName() === 'login') {
      location.hash = '#/dashboard';
    } else {
      route(); 
    }
  } catch (err) { toast(err.message, 'error') }
}

async function handleUnsubscribe(raw) {
  const body = typeof raw === 'string' ? JSON.parse(raw) : raw;
  if (!confirm('Berhenti berlangganan paket ini?')) return;
  try { const r = await api('/api/packages/unsubscribe', { method: 'POST', body: JSON.stringify(body) }); toast(r.ok ? 'Berhasil unsubscribe.' : 'Unsubscribe gagal.', r.ok ? 'success' : 'error'); if (r.ok) packagesPage(); } catch (err) { toast(err.message, 'error') }
}

function simpleFormModal(title, fields, onSubmit) {
  const body = `<form id="generic-form">${fields.map(f => `<div class="field"><label>${escapeHtml(f.label)}</label><input class="input" name="${f.name}" type="${f.type || 'text'}" value="${escapeHtml(f.value || '')}" placeholder="${escapeHtml(f.placeholder || '')}" ${f.required === false ? '' : 'required'} /></div>`).join('')}<button class="btn btn-primary" style="width:100%" type="submit">Simpan</button></form>`;
  showModal(title, body); $('#generic-form').addEventListener('submit', async e => { e.preventDefault(); const values = Object.fromEntries(new FormData(e.currentTarget).entries()); try { await onSubmit(values); closeModal(); toast('Berhasil.', 'success'); route(); } catch (err) { toast(err.message, 'error') } });
}

function handleProtectedError(err) {
  if (/belum login|401/i.test(err.message)) { toast('Silakan login terlebih dahulu.', 'error'); setTimeout(() => location.hash = '#/login', 350); } else { app.innerHTML = appShell('', 'Terjadi kesalahan', '', emptyState('Data gagal dimuat', err.message, 'info')); }
}

function routeName() { return (location.hash.replace(/^#\/?/, '').split('?')[0] || '').toLowerCase(); }
async function route() {
  closeModal(); await loadAccounts(); const r = routeName();
  if (!r) return landingPage();
  if (r === 'login') return loginPage();
  if (r === 'otp') return otpPage();
  const protectedRoutes = { dashboard: dashboardPage, packages: packagesPage, store: storePage, transactions: transactionsPage, family: familyPage, circle: circlePage, rewards: rewardsPage, bookmarks: bookmarksPage, notifications: notificationsPage, support: supportPage };
  if (protectedRoutes[r]) return protectedRoutes[r]();
  landingPage();
}

// Global event delegation
document.addEventListener('click', async e => {
  const t = e.target.closest('[data-action],[data-package-detail],[data-family-detail],[data-buy-package],[data-switch-account],[data-remove-account],[data-unsubscribe],[data-bookmark-remove],[data-bookmark-add],[data-family-limit],[data-family-remove],[data-family-add],[data-circle-invite],[data-circle-remove],[data-circle-accept],[data-store-tab]');
  if (!t) return;
  if (t.dataset.packageDetail) return openPackage(t.dataset.packageDetail);
  if (t.dataset.familyDetail) return openFamily(t.dataset.familyDetail);
  if (t.dataset.buyPackage) return checkoutModal(t.dataset.buyPackage);
  if (t.dataset.switchAccount) return switchAccount(t.dataset.switchAccount);
  if (t.dataset.removeAccount) { 
    if (!confirm(`Hapus akun ${t.dataset.removeAccount}?`)) return; 
    state.accounts = state.accounts.filter(a => a.number != t.dataset.removeAccount);
    saveAccounts();
    toast('Akun dihapus.', 'success'); 
    route(); 
    return; 
  }
  if (t.dataset.unsubscribe) return handleUnsubscribe(t.dataset.unsubscribe);
  if (t.dataset.bookmarkRemove) { 
    const b = JSON.parse(t.dataset.bookmarkRemove); 
    const key = `bookmarks_${state.accounts.find(x => x.active)?.number}`;
    let items = JSON.parse(localStorage.getItem(key) || '[]');
    items = items.filter(x => !(x.family_code === b.family_code && x.variant_name === b.variant_name && x.order === b.order && x.is_enterprise === b.is_enterprise));
    localStorage.setItem(key, JSON.stringify(items));
    toast('Bookmark dihapus.', 'success'); 
    bookmarksPage(); 
    return; 
  }
  if (t.dataset.bookmarkAdd) { 
    const b = JSON.parse(t.dataset.bookmarkAdd); 
    const key = `bookmarks_${state.accounts.find(x => x.active)?.number}`;
    let items = JSON.parse(localStorage.getItem(key) || '[]');
    if (!items.find(x => x.family_code === b.family_code && x.variant_name === b.variant_name && x.order === b.order && x.is_enterprise === b.is_enterprise)) {
      items.push(b);
      localStorage.setItem(key, JSON.stringify(items));
      toast('Bookmark ditambahkan.', 'success');
    } else {
      toast('Sudah ada di bookmark.', 'info');
    }
    return; 
  }
  if (t.dataset.familyLimit) { const d = JSON.parse(t.dataset.familyLimit); return simpleFormModal(`Limit Kuota Slot ${d.slot}`, [{ name: 'new_allocation_mb', label: 'Limit baru (MB)', type: 'number', placeholder: '1024' }], async v => { const r = await api('/api/family-plan/limit', { method: 'POST', body: JSON.stringify({ ...d, new_allocation_mb: Number(v.new_allocation_mb) }) }); if (r.status !== 'SUCCESS') throw new Error(r.message || 'Gagal mengatur limit.') }); }
  if (t.dataset.familyRemove) { if (!confirm('Hapus member dari Family Plan?')) return; try { const r = await api('/api/family-plan/remove', { method: 'POST', body: JSON.stringify({ family_member_id: t.dataset.familyRemove }) }); if (r.status !== 'SUCCESS') throw new Error(r.message || 'Gagal menghapus member.'); toast('Member dihapus.', 'success'); familyPage(); } catch (err) { toast(err.message, 'error') } return; }
  if (t.dataset.familyAdd) { const d = JSON.parse(t.dataset.familyAdd); return simpleFormModal(`Tambah Member Slot ${d.slot}`, [{ name: 'msisdn', label: 'Nomor member', placeholder: '628…' }, { name: 'parent_alias', label: 'Alias parent' }, { name: 'alias', label: 'Alias member' }], async v => { const r = await api('/api/family-plan/change', { method: 'POST', body: JSON.stringify({ ...d, ...v }) }); if (r.status !== 'SUCCESS') throw new Error(r.message || 'Gagal menambah member.') }); }
  if (t.dataset.circleInvite) { const d = JSON.parse(t.dataset.circleInvite); return simpleFormModal('Invite Member', [{ name: 'msisdn', label: 'Nomor member', placeholder: '628…' }, { name: 'name', label: 'Nama member' }], async v => { const r = await api('/api/circle/invite', { method: 'POST', body: JSON.stringify({ ...d, ...v }) }); if (r.status !== 'SUCCESS') throw new Error(r.message || 'Gagal mengundang member.') }); }
  if (t.dataset.circleRemove) { const d = JSON.parse(t.dataset.circleRemove); if (!confirm('Hapus member dari Circle?')) return; try { const r = await api('/api/circle/remove', { method: 'POST', body: JSON.stringify(d) }); if (r.status !== 'SUCCESS') throw new Error(r.message || 'Gagal menghapus member.'); toast('Member dihapus.', 'success'); circlePage(); } catch (err) { toast(err.message, 'error') } return; }
  if (t.dataset.circleAccept) { const d = JSON.parse(t.dataset.circleAccept); try { const r = await api('/api/circle/accept', { method: 'POST', body: JSON.stringify(d) }); if (r.status !== 'SUCCESS') throw new Error(r.message || 'Gagal menerima invitation.'); toast('Invitation diterima.', 'success'); circlePage(); } catch (err) { toast(err.message, 'error') } return; }
  if (t.dataset.storeTab) { $$('[data-store-tab]').forEach(x => x.classList.toggle('active', x === t)); $('#store-search').parentElement.style.display = t.dataset.storeTab === 'packages' ? 'block' : 'none'; $('#store-content').innerHTML = t.dataset.storeTab === 'packages' ? renderStorePackages(state.storePackages) : t.dataset.storeTab === 'families' ? renderFamilies() : t.dataset.storeTab === 'search' ? renderSearchCode() : renderSegments(); return; }
  const a = t.dataset.action;
  if (a === 'login' || a === 'get-started') { closeModal(); location.hash = '#/login'; return; }
  if (a === 'add-account') { closeModal(); location.hash = '#/login?from=dashboard'; return; }
  if (a === 'open-dashboard') { location.hash = state.accounts.length ? '#/dashboard' : '#/login'; return; }
  if (a === 'logout') { 
    state.accounts.forEach(a => a.active = false);
    saveAccounts();
    toast('Berhasil logout.', 'success'); 
    state.dashboard = null; 
    location.hash = '#/login'; 
    return; 
  }
  if (a === 'accounts') return showAccountsModal();
  if (a === 'close-modal') return closeModal();
  if (a === 'back-login') { location.hash = '#/login'; return; }
  if (a === 'resend-otp') { try { await api('/api/auth/request-otp', { method: 'POST', body: JSON.stringify({ number: state.loginNumber }) }); toast('OTP dikirim ulang.', 'success'); } catch (err) { toast(err.message, 'error') } return; }
  if (a === 'read-all') { try { await api('/api/notifications/read-all', { method: 'POST' }); toast('Notifikasi ditandai dibaca.', 'success'); notificationsPage(); } catch (err) { toast(err.message, 'error') } return; }
  if (a === 'search-option-code') { const code = $('#manual-code-input')?.value?.trim(); if (code) openPackage(code); return; }
  if (a === 'search-family-code') { const code = $('#manual-code-input')?.value?.trim(); if (code) openFamily(code); return; }
  if (a === 'create-circle') return simpleFormModal('Buat XL Circle', [{ name: 'parent_name', label: 'Nama parent' }, { name: 'group_name', label: 'Nama Circle' }, { name: 'member_msisdn', label: 'Nomor member awal', placeholder: '628…' }, { name: 'member_name', label: 'Nama member awal' }], async v => { const r = await api('/api/circle/create', { method: 'POST', body: JSON.stringify(v) }); if (r.status !== 'SUCCESS') throw new Error(r.message || 'Gagal membuat Circle.') });
});

document.addEventListener('click', e => { if (e.target.classList.contains('modal-backdrop')) closeModal(); });
window.addEventListener('hashchange', route);
route();
