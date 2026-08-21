import re

styles_file = 'webapp/static/styles.css'
with open(styles_file, 'r', encoding='utf-8') as f:
    css = f.read()

# 1. Colors and Body
css = css.replace('--blue-800: #0b36c9;', '--blue-800: #0B36C9;\n  --deep-blue: #09279F;\n  --bg-primary: #F5F7FC;\n  --text-main: #0B163F;\n  --text-sec: #7180A0;\n  --success: #16C99A;')
css = css.replace('background: #fff;', 'background: var(--bg-primary);')
css = css.replace("font-family: 'Poppins', ui-sans-serif,", "font-family: 'Poppins', 'Inter', sans-serif, ui-sans-serif,")
css = css.replace('color: var(--ink);', 'color: var(--text-main);')

# 2. Topbar & Layout
css = css.replace('.content {\n  max-width: 1320px;\n  margin: 0 auto;\n}', '.content {\n  max-width: 1500px;\n  margin: 0 auto;\n  padding: 0 32px;\n}')
css = css.replace('.workspace {\n  min-width: 0;\n  padding: 18px 26px 34px;\n}', '.workspace {\n  min-width: 0;\n  padding: 18px 0 34px;\n}')
css = css.replace('.topbar {\n  height: 64px;\n  display: flex;\n  align-items: center;\n  justify-content: space-between;\n  gap: 20px;\n  margin-bottom: 14px;\n}', '.topbar {\n  height: 64px;\n  display: flex;\n  align-items: center;\n  justify-content: space-between;\n  gap: 20px;\n  margin-bottom: 24px;\n  padding: 0 32px;\n  max-width: 1500px;\n  margin-left: auto;\n  margin-right: auto;\n}')
css = css.replace('.page-title h1 {\n  font-size: 27px;\n  margin: 0;\n  letter-spacing: -.035em;\n}', '.page-title h1 {\n  font-size: 28px;\n  margin: 0;\n  font-weight: 700;\n  letter-spacing: -.02em;\n  color: var(--text-main);\n}')
css = css.replace('.page-title p {\n  color: var(--muted);\n  margin: 5px 0 0;\n  font-size: 13px;\n}', '.page-title p {\n  color: var(--text-sec);\n  margin: 4px 0 0;\n  font-size: 14px;\n}')

# 3. Dashboard Summary
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

css = css.replace('.stat-block {\n  padding-left: 18px;\n  border-left: 1px solid var(--line);\n}', '.stat-block {\n  padding-left: 0;\n  border-left: none;\n}')
css = css.replace('.dash-grid {\n  display: grid;\n  grid-template-columns: 1.7fr .8fr;\n  gap: 18px;\n  margin-top: 18px;\n}', '.dash-grid {\n  display: grid;\n  grid-template-columns: minmax(0, 2fr) minmax(320px, 0.85fr);\n  gap: 16px;\n  margin-top: 18px;\n}')

# 4. Package Hero
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

# Update index.html cache buster
index_file = 'webapp/static/index.html'
with open(index_file, 'r', encoding='utf-8') as f:
    idx = f.read()
idx = re.sub(r'v=\d+', 'v=12410', idx)
# Add google fonts for Inter
if 'fonts.googleapis.com' not in idx:
    idx = idx.replace('<title>', '<link rel="preconnect" href="https://fonts.googleapis.com">\n<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>\n<link href="https://fonts.googleapis.com/css2?family=Poppins:wght@400;500;600;700&display=swap" rel="stylesheet">\n<title>')

with open(index_file, 'w', encoding='utf-8') as f:
    f.write(idx)

print("Apply Redesign CSS Success")
