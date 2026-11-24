"""Build authored guides + marked home sections, preserving existing articles/links.
Sources: data/refresh-guides.json, refresh-news.json, place-directory.json.
Run before inject_parts, build-search-index and build_sitemap. No network needed.
"""
import json,re,html
from datetime import date
from pathlib import Path
from local_articles import build_local_articles, load_articles, update_guide_body
ROOT=Path(__file__).resolve().parent.parent
SITE='https://kakegawa.enshu-lifehack.com'
guides=json.loads((ROOT/'data/refresh-guides.json').read_text(encoding='utf8'))
news=json.loads((ROOT/'data/refresh-news.json').read_text(encoding='utf8'))
articles=load_articles()
build_local_articles(articles)
esc=html.escape
def link(u,t):return '<a href="'+esc(u,quote=True)+'">'+esc(t)+'</a>'
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
   notices.append(
    '<section class="guide-section"><h2>'+esc(title)+'</h2>'
    '<p class="date-line">'+esc(period)+' <span class="badge">'+esc(status)+'</span></p>'
    '<p>'+esc(summary)+'</p><p class="source-links">'+link(source,'掛川市の公式案内')+'</p></section>'
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
hero='''<section class="hero refresh-hero"><div><p class="eyebrow">KAKEGAWA · LIFE & LOCAL GUIDE</p><h1>掛川の暮らしに、<br>頼れる入口を。</h1><p class="lead">手続きも、子育ても、次の休日も。<br>掛川・大東・大須賀の情報を、暮らしの場面から探せます。</p><div class="hero-links">'''+link('#quick-start','困りごとから探す')+link('/guide/visit/','掛川を訪ねる')+link('#community-gallery','昔の掛川を写真で見る')+'''</div><p class="date-line">お知らせ確認 <time datetime="2026-11-24">2026年11月24日</time></p></div>
<figure class="home-hero-photo">
<a href="/discover/kakegawajyo/"><img src="/assets/discover-photos/castle-960.webp" srcset="/assets/discover-photos/castle-480.webp 480w, /assets/discover-photos/castle-960.webp 960w" sizes="(max-width: 700px) calc(100vw - 76px), (max-width: 1050px) 45vw, 460px" width="960" height="640" fetchpriority="high" alt="石垣の上に建つ掛川城の木造復元天守"></a>
<figcaption><span class="hero-photo-place">掛川城の木造復元天守</span><span>写真：<a href="https://www.city.kakegawa.shizuoka.jp/opendata/dataset/11540.html">掛川市オープンデータ</a>（<a href="https://creativecommons.org/licenses/by/4.0/">CC BY 4.0</a>、縮小・WebP変換）</span></figcaption>
</figure></section>'''
s=re.sub(r'<section class="hero(?: refresh-hero)?">.*?</section>',lambda _:hero,s,count=1,flags=re.S)
s=re.sub(r'<title>.*?</title>','<title>掛川ライフハック｜暮らし・子育て・手続き・観光の地域ガイド</title>',s,count=1)
s=re.sub(r'<meta name="description" content="[^"]*">','<meta name="description" content="掛川市の暮らし・子育て・介護・引っ越しと、お茶・城下町・大東・大須賀のお出かけを案内。公式情報の変更、受付状況、チェックリスト、地区別の相談先を整理する非公式ガイドです。">',s,count=1)
quick='<section id="quick-start" class="refresh-section"><p class="eyebrow">START HERE</p><h2>今、知りたいことから</h2><div class="quick-grid">'+''.join('<a href="'+guides[i]['href']+'"><span aria-hidden="true">'+guides[i]['icon']+'</span><strong>'+label+'</strong><small>'+desc+'</small></a>' for i,label,desc in [(0,'引っ越し・移住','水道・住所変更・地区選び'),(1,'子育て・入園','手当・医療費・園の申請'),(4,'親の介護','地区別の相談先・認定'),(3,'ごみ・片付け','区域別カレンダー・リユース'),(7,'市役所・証明書','窓口時間・コンビニ交付'),(5,'住まい・空き家','住宅募集・耐震・解体'),(8,'防災・避難','住所のリスクと家族の準備'),(6,'おくやみ','予約・持ち物・相続'),(2,'急な病気・けが','救急相談と診療時間')])+'</div></section>'
updates='<section class="refresh-section"><div class="section-heading"><div><p class="eyebrow">2026年11月24日確認</p><h2>いま確認したい変更・お知らせ</h2></div>'+link('/guide/updates/','すべてのお知らせ →')+'</div><div class="news-grid">'+''.join('<article><span class="badge">'+n[1]+'</span><p class="date-line">'+n[0]+'</p><h3>'+link(n[4],n[2])+'</h3><p>'+n[3]+'</p></article>' for n in news[:6])+'</div><p class="mini">確認日現在の情報です。申込み・来訪前はリンク先の最新発表をご確認ください。</p></section>'
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
block='<!-- REFRESH:START -->'+quick+updates+explore+'<!-- REFRESH:END -->'
if '<!-- REFRESH:START -->' in s:s=re.sub(r'<!-- REFRESH:START -->.*?<!-- REFRESH:END -->',lambda _:block,s,flags=re.S)
else:s=s.replace('<section id="category-links">',block+'<section id="category-links">',1)
bottom='<!-- GUIDES:START -->'+allguides+faq+method+'<!-- GUIDES:END -->'
if '<!-- GUIDES:START -->' in s:s=re.sub(r'<!-- GUIDES:START -->.*?<!-- GUIDES:END -->',lambda _:bottom,s,flags=re.S)
else:s=re.sub(r'<section class="updates">.*?</section>',lambda _:bottom,s,count=1,flags=re.S)
home.write_text(s,encoding='utf8')
# Apply separately dated source notes without replacing manual article additions.
for note in json.loads((ROOT/'data/current-notes.json').read_text(encoding='utf8')):
 f=ROOT/note['href'].strip('/')/'index.html'
 s=f.read_text(encoding='utf8')
 extra=' ／ '+link(note['extra_source'],'水道基本料金の減免') if 'extra_source' in note else ''
 block='<!-- CURRENT:START --><aside class="verified-update"><h2>'+date_label(note['date'])+'確認の変更・補足</h2><p>'+esc(note['text'])+'</p><p>'+link(note['source'],'公式案内で確認する')+extra+' ／ '+link('/guide/'+note['guide']+'/','手順と準備をまとめて見る')+'</p></aside><!-- CURRENT:END -->'
 if '<!-- CURRENT:START -->' in s:s=re.sub(r'<!-- CURRENT:START -->.*?<!-- CURRENT:END -->',lambda _:block,s,flags=re.S)
 else:
  pos=s.find('</section>',s.find('<section class="hero"'))+len('</section>')
  if pos<len('</section>'):raise RuntimeError(str(f))
  s=s[:pos]+block+s[pos:]
 f.write_text(s,encoding='utf8')
print('Built',len(guides),'guides and home marked sections')
