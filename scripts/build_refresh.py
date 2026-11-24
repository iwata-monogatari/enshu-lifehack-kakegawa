"""Build authored guides + marked home sections, preserving existing articles/links.
Sources: data/refresh-guides.json, refresh-news.json, place-directory.json.
Run before inject_parts, build-search-index and build_sitemap. No network needed.
"""
import json,re,html
from datetime import date
from generate_pages import load_content_map, quick_answer_html
from pathlib import Path
from local_articles import build_local_articles, load_articles, update_guide_body
ROOT=Path(__file__).resolve().parent.parent
SITE='https://kakegawa.enshu-lifehack.com'
guides=json.loads((ROOT/'data/refresh-guides.json').read_text(encoding='utf8'))
news=json.loads((ROOT/'data/refresh-news.json').read_text(encoding='utf8'))
priority_life_pages={
 '/life/troubles-consult/living-costs-trouble/',
 '/life/education/school-zones/',
 '/life/education/after-school-club/',
 '/life/start-living/water-start-stop-fees/',
 '/life/start-living/garbage-sorting-calendar/',
 '/life/start-living/certificates/',
 '/life/housing/municipal-housing/',
 '/life/play-out/visit-library/',
 '/life/living-soon/transportation/',
}
articles=load_articles()
build_local_articles(articles)
esc=html.escape
notice_guides={
 '1215418':('/guide/water-bill-relief/','減免額と請求額の見方'),
 '61559':('/life/housing/municipal-housing/','市営住宅の募集と申込み'),
 '946824':('/life/play-out/visit-library/','市立図書館の利用案内'),
 '1229789':('/guide/visit/','掛川の歴史まちづくり'),
 '1201970':('/life/start-living/water-start-stop-fees/','水道の開始・中止の申込み'),
 '458842':('/guide/parenting/','保育園の入園手続き'),
 '554709':('/life/play-out/sports-facilities/','学校体育施設の予約'),
 '1186448':('/guide/food/','掛川茶の募集と案内'),
 '1113715':('/guide/counter/','市役所の窓口時間と証明書'),
 '324185':('/life/education/after-school-club/','学童保育の申込み'),
}
def link(u,t):return '<a href="'+esc(u,quote=True)+'">'+esc(t)+'</a>'
def notice_guide(source):
 return notice_guides.get(Path(source).stem)

def date_label(value):
 day=date.fromisoformat(value)
 return f"{day.year}年{day.month}月{day.day}日"

def checked_time(value):
 return f'<time datetime="{value}">{date_label(value)}</time>'

def card(g):return '<a class="guide-card" href="'+g['href']+'"><span class="guide-icon" aria-hidden="true">'+g['icon']+'</span><h3>'+esc(g['title'].split('｜')[0])+'</h3><p>'+esc(g['lead'])+'</p><span class="card-arrow" aria-hidden="true">→</span></a>'
nav='<nav class="guide-nav" aria-label="主なガイド"><div class="wrap">'+link('/#category-links','手続き')+link('/guide/updates/','最新情報')+link('/guide/visit/','お出かけ')+link('/guide/food/','お茶・特産品')+link('/guide/urgent/','急病のとき')+'</div></nav>'
(ROOT/'parts/header.html').write_text('<header class="site"><div class="wrap"><a class="logo" href="/">掛川ライフハック</a><span class="tag">暮らす・訪ねる・困りごとを解決する</span></div></header>'+nav,encoding='utf8')
(ROOT/'parts/head-css.html').write_text('<link rel="stylesheet" href="/assets/site.css?v=20261119b"><link rel="stylesheet" href="/assets/refresh.css?v=20261119c">',encoding='utf8')
for g in guides:
 related=[x for x in guides if x['href']!=g['href'] and x['href'] in ['/guide/moving/','/guide/parenting/','/guide/visit/','/guide/updates/']]
 page='''<!doctype html><html lang="ja"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>'''+esc(g['title'])+''' | 掛川ライフハック</title><meta name="description" content="'''+esc(g['lead'],quote=True)+'''">
<link rel="canonical" href="'''+SITE+g['href']+'''"><link rel="icon" href="/favicon.svg" type="image/svg+xml">
<!-- PART:head-css:START --><!-- PART:head-css:END --></head><body class="hub guide-page">
<!-- PART:header:START --><!-- PART:header:END -->
<main class="wrap"><p class="breadcrumb">'''+link('/','ホーム')+''' / 実用ガイド</p>
<header class="guide-hero"><p class="eyebrow"><span aria-hidden="true">'''+g['icon']+'''</span> 掛川の実用ガイド</p><h1>'''+esc(g['title'])+'''</h1><p class="lead">'''+esc(g['lead'])+'''</p><p class="date-line">公式情報確認：'''+checked_time(g.get('checked','2026-11-19'))+'''</p></header>
<p class="editorial-note">掛川市の公式サイトではありません。個別の申請条件・営業日・受付状況は、各項目の公式リンクで確認してください。</p>'''
 body=update_guide_body(g, articles)
 if g['href'] == '/guide/updates/':
  notices = []
  for period, status, title, summary, source in news:
   related_notice = notice_guide(source)
   follow = ' ／ '+link(*related_notice) if related_notice else ''
   notices.append(
    '<section class="guide-section"><h2>'+esc(title)+'</h2>'
    '<p class="date-line">'+esc(period)+' <span class="badge">'+esc(status)+'</span></p>'
    '<p>'+esc(summary)+'</p><p class="source-links">'+link(source,'掛川市の公式案内')+follow+'</p></section>'
   )
  body=''.join(notices)+body
 local_guide=g['href'] in ('/guide/visit/', '/guide/food/')
 if local_guide:
  page=page.replace('</head>', '<link rel="stylesheet" href="/assets/local-articles.css?v=1"></head>', 1)
 headings=re.findall(r'<h2>(.*?)</h2>',body)
 for i,h in enumerate(headings):body=body.replace('<h2>'+h+'</h2>','<h2 id="section-'+str(i+1)+'">'+h+'</h2>',1)
 page+='<nav class="guide-toc" aria-label="このページの目次"><b>このページでわかること</b><ol>'+''.join('<li>'+link('#section-'+str(i+1),h)+'</li>' for i,h in enumerate(headings))+'</ol></nav>'+body
 page+='<section class="guide-section"><h2>ほかのガイドへ</h2><div class="guide-grid">'+''.join(card(x) for x in related)+'</div></section>'
 if g['href'] != '/guide/visit/':
  page+='<p class="check-storage">チェック機能はこの端末のブラウザーにのみ保存されます。個人情報の送信や手続きの申請は行いません。共有端末では使い終わったらチェックを解除してください。</p>'
 script_version='?v=2' if local_guide else ''
 page+=f'</main><script src="/assets/guide-tools.js{script_version}" defer></script><!-- PART:footer:START --><!-- PART:footer:END --></body></html>'
 f=ROOT/g['href'].strip('/')/'index.html';f.parent.mkdir(parents=True,exist_ok=True);f.write_text(page,encoding='utf8')

home=ROOT/'index.html';s=home.read_text(encoding='utf8')
home_title = '掛川ライフハック｜暮らし・子育て・手続き・観光の地域ガイド'
home_description = '掛川市の暮らし・子育て・介護・引っ越しと、お茶・城下町・大東・大須賀のお出かけを案内。公式情報の変更、受付状況、チェックリスト、地区別の相談先を整理する非公式ガイドです。'
hero_image_path = '/assets/discover-photos/castle-960.webp'
hero='''<section class="hero refresh-hero"><div><p class="eyebrow">KAKEGAWA · LIFE & LOCAL GUIDE</p><h1>掛川の暮らしに、<br>頼れる入口を。</h1><p class="lead">手続きも、子育ても、次の休日も。<br>掛川・大東・大須賀の情報を、暮らしの場面から探せます。</p><div class="hero-links">'''+link('#quick-start','困りごとから探す')+link('/guide/visit/','掛川を訪ねる')+link('#community-gallery','昔の掛川を写真で見る')+'''</div><p class="date-line">お知らせ確認 <time datetime="2026-11-24">2026年11月24日</time></p></div>
<figure class="home-hero-photo">
<a href="/discover/kakegawajyo/"><img src="'''+hero_image_path+'''" srcset="/assets/discover-photos/castle-480.webp 480w, /assets/discover-photos/castle-960.webp 960w" sizes="(max-width: 700px) calc(100vw - 76px), (max-width: 1050px) 45vw, 460px" width="960" height="640" fetchpriority="high" alt="石垣の上に建つ掛川城の木造復元天守"></a>
<figcaption><span class="hero-photo-place">掛川城の木造復元天守</span><span>写真：<a href="https://www.city.kakegawa.shizuoka.jp/opendata/dataset/11540.html">掛川市オープンデータ</a>（<a href="https://creativecommons.org/licenses/by/4.0/">CC BY 4.0</a>、縮小・WebP変換）</span></figcaption>
</figure></section>'''
s=re.sub(r'<section class="hero(?: refresh-hero)?">.*?</section>',lambda _:hero,s,count=1,flags=re.S)
s=re.sub(r'<title>.*?</title>',f'<title>{esc(home_title)}</title>',s,count=1)
s=re.sub(r'<meta name="description" content="[^"]*">',f'<meta name="description" content="{esc(home_description,quote=True)}">',s,count=1)
quick='<section id="quick-start" class="refresh-section"><p class="eyebrow">START HERE</p><h2>今、知りたいことから</h2><div class="quick-grid">'+''.join('<a href="'+guides[i]['href']+'"><span aria-hidden="true">'+guides[i]['icon']+'</span><strong>'+label+'</strong><small>'+desc+'</small></a>' for i,label,desc in [(0,'引っ越し・移住','水道・住所変更・地区選び'),(1,'子育て・入園','手当・医療費・園の申請'),(4,'親の介護','地区別の相談先・認定'),(3,'ごみ・片付け','区域別カレンダー・リユース'),(7,'市役所・証明書','窓口時間・コンビニ交付'),(5,'住まい・空き家','住宅募集・耐震・解体'),(8,'防災・避難','住所のリスクと家族の準備'),(6,'おくやみ','予約・持ち物・相続'),(2,'急な病気・けが','救急相談と診療時間')])+'</div></section>'
updates='<section class="refresh-section"><div class="section-heading"><div><p class="eyebrow">2026年11月24日確認</p><h2>いま確認したい変更・お知らせ</h2></div>'+link('/guide/updates/','すべてのお知らせ →')+'</div><div class="news-grid">'+''.join('<article><span class="badge">'+n[1]+'</span><p class="date-line">'+n[0]+'</p><h3>'+link((notice_guide(n[4]) or (n[4],))[0],n[2])+'</h3><p>'+n[3]+'</p><p class="mini">'+link(n[4],'掛川市の公式発表')+'</p></article>' for n in news[:6])+'</div><p class="mini">確認日現在の情報です。申込み・来訪前はリンク先の最新発表をご確認ください。</p></section>'
history_card={'href':'/guide/history/','icon':'🏯','title':'掛川の歴史・文化','lead':'掛川三城、日坂宿と旧東海道、横須賀の町並み、寺社や美術館の背景を読む。'}
explore='<section class="refresh-section explore"><h2>掛川の観光・歴史・お茶を知る</h2><div class="guide-grid">'+''.join(card(g) for g in [guides[9],history_card,guides[10]])+'</div><p>'+link('/guide/visit/#local-articles',f'観光・歴史・特産品の全{len(articles)}記事を探す')+'</p></section>'
allguides='<section class="refresh-section"><p class="eyebrow">PRACTICAL GUIDES</p><h2>手順と準備を、ひとつのページで</h2><p>持ち物や順序に迷ったら、ガイド内のチェックリストを使えます。</p><div class="guide-grid">'+''.join(card(g) for g in guides if g['href'] not in ['/guide/visit/','/guide/food/'])+'</div></section>'
faq='<section class="refresh-section home-faq"><h2>よくある質問</h2>'+''.join('<details><summary>'+q+'</summary><p>'+answer+' '+link(url,'詳しく確認する')+'</p></details>' for q,answer,url in [
('市役所は何時までですか？','通常窓口は2026年11月2日から9:00〜16:30。電話は8:30〜17:15で、対象外施設・木曜夜間の扱いは個別に確認が必要です。','/guide/counter/'),
('水道はネットで開始できますか？','市の11月20日発表では、開始・中止・変更のオンライン手続きは停止中です。平日の電話または窓口をご利用ください。','/guide/moving/'),
('2027年4月の入園はこれから申し込めますか？','当初受付は10月30日に終了しました。未申請の方はこども保育支援課へ相談してください。','/guide/parenting/'),
('休日の午後に歯科を受診できますか？','小笠掛川急患診療所の歯科は休日の午前のみです。午後と平日夜間は歯科診療がありません。','/guide/urgent/'),
('ごみの日は市内で同じですか？','掛川区域と大東・大須賀区域のカレンダーを選び、さらに自分の地区の収集日を確認してください。','/guide/garbage/'),
('親の介護はどこに相談しますか？','親の住所を担当する地域包括支援センターへ。市内5窓口の担当地区・電話番号を掲載しています。','/guide/care/'),
('チェックした情報は送信されますか？','チェックの状態だけを利用中のブラウザー内に保存します。名前や病歴を入力する欄はなく、申請・予約の代わりにはなりません。','/guide/moving/')])+'</section>'
method='<section class="refresh-section editorial-note"><h2>情報の確認について</h2><p>2026年11月24日に、水道基本料金の減免、市営住宅の先着受付、図書館のオンラインサービス休止などを市の公式案内と照合しました。手続きページでは項目ごとの確認日と出典をご覧いただけます。</p><p>市内すべての店舗・イベントの営業や受付をリアルタイムで保証するものではありません。</p></section>'
frequent_links=[
 ('/life/start-living/garbage-sorting-calendar/','地区別ごみ収集カレンダー'),
 ('/life/start-living/certificates/','住民票などのコンビニ交付'),
 ('/life/education/after-school-club/','学童保育の申込み'),
 ('/life/education/school-zones/','住所から小・中学校の通学区を調べる'),
 ('/life/troubles-consult/living-costs-trouble/','生活費・家計の相談先'),
 ('/life/living-soon/transportation/','掛川のバス・電車'),
 ('/discover/kakegawajyo/','掛川城の開館時間・アクセス'),
 ('/discover/kakegawa-three-castles/','掛川三城の巡り方'),
]
frequent='<nav class="refresh-section editorial-note" aria-labelledby="frequent-guide-links"><h2 id="frequent-guide-links">よく使う案内</h2><ul>'+''.join('<li>'+link(*item)+'</li>' for item in frequent_links)+'</ul></nav>'
block='<!-- REFRESH:START -->'+quick+updates+frequent+explore+'<!-- REFRESH:END -->'
if '<!-- REFRESH:START -->' in s:s=re.sub(r'<!-- REFRESH:START -->.*?<!-- REFRESH:END -->',lambda _:block,s,flags=re.S)
else:s=s.replace('<section id="category-links">',block+'<section id="category-links">',1)
bottom='<!-- GUIDES:START -->'+allguides+faq+method+'<!-- GUIDES:END -->'
if '<!-- GUIDES:START -->' in s:s=re.sub(r'<!-- GUIDES:START -->.*?<!-- GUIDES:END -->',lambda _:bottom,s,flags=re.S)
else:s=re.sub(r'<section class="updates">.*?</section>',lambda _:bottom,s,count=1,flags=re.S)
home_share_fields = {
 'og:type': 'website',
 'og:locale': 'ja_JP',
 'og:site_name': '掛川ライフハック',
 'og:url': SITE+'/',
 'og:title': home_title,
 'og:description': home_description,
 'og:image': SITE+hero_image_path,
 'og:image:width': '960',
 'og:image:height': '640',
 'og:image:alt': '掛川城の木造復元天守',
}
home_share='<meta name="robots" content="max-image-preview:large">'+''.join(
 f'<meta property="{key}" content="{esc(value,quote=True)}">' for key,value in home_share_fields.items()
)+'<meta name="twitter:card" content="summary_large_image">'
share_block='<!-- HOME-SHARE:START -->'+home_share+'<!-- HOME-SHARE:END -->'
if '<!-- HOME-SHARE:START -->' in s:
 s=re.sub(r'<!-- HOME-SHARE:START -->.*?<!-- HOME-SHARE:END -->',lambda _:share_block,s,count=1,flags=re.S)
else:
 s=s.replace('</head>',share_block+'\n</head>',1)
home.write_text(s,encoding='utf8')
# Apply separately dated source notes without replacing manual article additions.
for note in json.loads((ROOT/'data/current-notes.json').read_text(encoding='utf8')):
 f=ROOT/note['href'].strip('/')/'index.html'
 s=f.read_text(encoding='utf8')
 extra=' ／ '+link(note['extra_source'],'水道基本料金の減免') if 'extra_source' in note else ''
 if note.get('extra_source') == 'https://www.city.kakegawa.shizuoka.jp/gyosei/docs/1215418.html':
  extra+=' ／ '+link(*notice_guides['1215418'])
 if note['href'] == '/life/education/after-school-club/':
  extra+=' ／ '+link('https://www.city.kakegawa.shizuoka.jp/gyosei/docs/919599.html','2027年度の入所申込書類')
 block='<!-- CURRENT:START --><aside class="verified-update"><h2>'+date_label(note['date'])+'確認の変更・補足</h2><p>'+esc(note['text'])+'</p><p>'+link(note['source'],'公式案内で確認する')+extra+' ／ '+link('/guide/'+note['guide']+'/','手順と準備をまとめて見る')+'</p></aside><!-- CURRENT:END -->'
 if '<!-- CURRENT:START -->' in s:s=re.sub(r'<!-- CURRENT:START -->.*?<!-- CURRENT:END -->',lambda _:block,s,flags=re.S)
 else:
  pos=s.find('</section>',s.find('<section class="hero"'))+len('</section>')
  if pos<len('</section>'):raise RuntimeError(str(f))
  s=s[:pos]+block+s[pos:]
 f.write_text(s,encoding='utf8')
# Update static life-page excerpts from the corresponding on-page introduction.
content_by_path=load_content_map()
for topic in json.loads((ROOT/'data/topics_master.json').read_text(encoding='utf8')):
 f=ROOT/topic['href'].strip('/')/'index.html'
 s=f.read_text(encoding='utf8')
 intro=re.search(r'<p class="lead">([^<]+)</p>',s)
 if intro is None:
  raise ValueError(f'Missing life-page introduction: {f}')
 lead=html.unescape(intro[1]).strip()
 description=lead if '掛川' in lead else '掛川市の案内。'+lead
 s=re.sub(r'(<meta name="description" content=")[^"]*(")',lambda m:m[1]+esc(description,quote=True)+m[2],s,count=1)
 title=topic['title']
 title_html=esc(title)
 if topic['href'] in priority_life_pages:
  s=re.sub(r'<title>[^<]+</title>',lambda _:f'<title>{title_html} | 掛川ライフハック</title>',s,count=1)
  s=re.sub(r'(<h1[^>]*>)[^<]+(</h1>)',lambda m:m[1]+title_html+m[2],s,count=1)
 answer=content_by_path.get(topic['href'],{}).get('quick_answer')
 if answer:
  answer_block=quick_answer_html(answer)
  if '<!-- SEARCH-INTENT:START -->' in s:
   s=re.sub(r'<!-- SEARCH-INTENT:START -->.*?<!-- SEARCH-INTENT:END -->',lambda _:answer_block,s,count=1,flags=re.S)
  else:
   hero_end=s.index('</section>',s.index('<section class="hero"'))+len('</section>')
   s=s[:hero_end]+answer_block+s[hero_end:]
 f.write_text(s,encoding='utf8')
print('Built',len(guides),'guides and home marked sections')
