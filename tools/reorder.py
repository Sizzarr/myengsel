with open('webapp/static/app.js', 'r', encoding='utf-8') as f:
    text = f.read()

rewards_str = '<section class="card widget-rewards"><div class="w-rev-content"><div class="widget-head-qa">${icon(\'gift\')} Rewards</div><div class="w-rev-points">${escapeHtml(dash.points.current)} pts</div><a href="#/rewards" class="link-blue">Lihat redeemables ></a></div><div class="w-rev-ill">${icon(\'gift\')}</div></section>'

notifications_str = '<section class="card widget-notifications"><div class="w-rev-content"><div class="widget-head-qa">${icon(\'bell\')} Notifikasi</div><div class="w-rev-points">${dash.unread_count || 0} unread</div><span class="preview-label">${dash.unread_count ? `<a href="#/notifications" class="link-blue">Lihat notifikasi ></a>` : \'Belum ada notifikasi baru\'}</span></div><div class="w-rev-ill ill-bell">${icon(\'bell\')}</div></section>'

if rewards_str in text and notifications_str in text:
    print('Found both strings, replacing...')
    old_seq = rewards_str + notifications_str
    new_seq = notifications_str + rewards_str
    if old_seq in text:
        text = text.replace(old_seq, new_seq)
        with open('webapp/static/app.js', 'w', encoding='utf-8') as f:
            f.write(text)
        print('Successfully reordered in app.js')
    else:
        print('Did not find the exact sequence.')
else:
    print('Could not find strings')
