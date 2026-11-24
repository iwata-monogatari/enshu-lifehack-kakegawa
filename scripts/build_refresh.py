"""Build authored guides + marked home sections, preserving existing articles/links.
Sources: data/refresh-guides.json, refresh-news.json, place-directory.json.
Run before inject_parts, build-search-index and build_sitemap. No network needed.
"""
import json,re,html
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
<header class="guide-hero"><p class="eyebrow"><span aria-hidden="true">'''+g['icon']+'''</span> 掛川の実用ガイド</p><h1>'''+esc(g['title'])+'''</h1><p class="lead">'''+esc(g['lead'])+'''</p><p class="date-line">公式情報確認：<time datetime="2026-11-19">2026年11月19日</time></p></header>
<p class="editorial-note">掛川市の公式サイトではありません。個別の申請条件・営業日・受付状況は、各項目の公式リンクで確認してください。</p>'''
 body=update_guide_body(g, articles)
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
hero='''<section class="hero refresh-hero"><div><p class="eyebrow">KAKEGAWA · LIFE & LOCAL GUIDE</p><h1>掛川の暮らしに、<br>頼れる入口を。</h1><p class="lead">手続きも、子育ても、次の休日も。<br>掛川・大東・大須賀の情報を、暮らしの場面から探せます。</p><div class="hero-links">'''+link('#quick-start','困りごとから探す')+link('/guide/visit/','掛川を訪ねる')+link('#community-gallery','昔の掛川を写真で見る')+'''</div><p class="date-line">2026年11月19日 公式情報を確認・更新</p></div><div class="town-art" aria-hidden="true"><svg viewBox="0 0 420 290" xmlns="http://www.w3.org/2000/svg"><circle cx="323" cy="68" r="42" fill="#e8b85c"/><path d="M0 157Q70 70 145 145Q240 37 420 170V290H0Z" fill="#94b0a0"/><path d="M0 218Q138 132 420 210V290H0Z" fill="#477966"/><path d="M0 255Q140 185 420 235M0 275Q160 207 420 255" stroke="#a8c79a" stroke-width="9" fill="none"/><path d="M143 228L158 196H254L270 228" fill="#b2b8ac"/><path d="M161 195V139H250V195M177 139V103H234V139M190 103V77H219V103" fill="#fff9e9"/><g fill="#254f4d"><path d="M137 150L179 123H232L272 150Z"/><path d="M162 111L188 92H221L247 111Z"/><path d="M179 82L204 62L231 82Z"/><path d="M194 171H213V195H194Z"/><path d="M186 117H193V128H186ZM216 117H223V128H216Z"/></g><path d="M275 285Q335 255 420 268V290H275Z" fill="#80b9bd"/></svg><span>城下町から、茶畑と海へ</span></div></section>'''
s=re.sub(r'<section class="hero(?: refresh-hero)?">.*?</section>',lambda _:hero,s,count=1,flags=re.S)
s=re.sub(r'<title>.*?</title>','<title>掛川ライフハック｜暮らし・子育て・手続き・観光の地域ガイド</title>',s,count=1)
s=re.sub(r'<meta name="description" content="[^"]*">','<meta name="description" content="掛川市の暮らし・子育て・介護・引っ越しと、お茶・城下町・大東・大須賀のお出かけを案内。公式情報の変更、受付状況、チェックリスト、地区別の相談先を整理する非公式ガイドです。">',s,count=1)
quick='<section id="quick-start" class="refresh-section"><p class="eyebrow">START HERE</p><h2>今、知りたいことから</h2><div class="quick-grid">'+''.join('<a href="'+guides[i]['href']+'"><span aria-hidden="true">'+guides[i]['icon']+'</span><strong>'+label+'</strong><small>'+desc+'</small></a>' for i,label,desc in [(0,'引っ越し・移住','水道・住所変更・地区選び'),(1,'子育て・入園','手当・医療費・園の申請'),(4,'親の介護','地区別の相談先・認定'),(3,'ごみ・片付け','区域別カレンダー・リユース'),(7,'市役所・証明書','窓口時間・コンビニ交付'),(5,'住まい・空き家','住宅募集・耐震・解体'),(8,'防災・避難','住所のリスクと家族の準備'),(6,'おくやみ','予約・持ち物・相続'),(2,'急な病気・けが','救急相談と診療時間')])+'</div></section>'
updates='<section class="refresh-section"><div class="section-heading"><div><p class="eyebrow">CHECKED 2026.11.19</p><h2>いま確認したい変更・お知らせ</h2></div>'+link('/guide/updates/','すべてのお知らせ →')+'</div><div class="news-grid">'+''.join('<article><span class="badge">'+n[1]+'</span><p class="date-line">'+n[0]+'</p><h3>'+link(n[4],n[2])+'</h3><p>'+n[3]+'</p></article>' for n in [news[0],news[1],news[2],news[5]])+'</div><p class="mini">確認日現在の情報です。申込み・来訪前はリンク先の最新発表をご確認ください。</p></section>'
history_card={'href':'/guide/history/','icon':'🏯','title':'掛川の歴史・文化','lead':'掛川三城、日坂宿と旧東海道、横須賀の町並み、寺社や美術館の背景を読む。'}
explore='<section class="refresh-section explore"><h2>掛川の観光・歴史・お茶を知る</h2><div class="guide-grid">'+''.join(card(g) for g in [guides[9],history_card,guides[10]])+'</div><p>'+link('/guide/visit/#local-articles',f'観光・歴史・特産品の全{len(articles)}記事を探す')+'</p></section>'
allguides='<section class="refresh-section"><p class="eyebrow">PRACTICAL GUIDES</p><h2>手順と準備を、ひとつのページで</h2><p>持ち物や順序に迷ったら、ガイド内のチェックリストを使えます。</p><div class="guide-grid">'+''.join(card(g) for g in guides if g['href'] not in ['/guide/visit/','/guide/food/'])+'</div></section>'
faq='<section class="refresh-section home-faq"><h2>よくある質問</h2>'+''.join('<details><summary>'+q+'</summary><p>'+answer+' '+link(url,'詳しく確認する')+'</p></details>' for q,answer,url in [
('市役所は何時までですか？','通常窓口は2026年11月2日から9:00〜16:30。電話は8:30〜17:15で、対象外施設・木曜夜間の扱いは個別に確認が必要です。','/guide/counter/'),
('水道はネットで開始できますか？','2026年11月19日時点では開始・中止のネット申請が停止中です。平日の電話または窓口で申し込んでください。','/guide/moving/'),
('2027年4月の入園はこれから申し込めますか？','当初受付は10月30日に終了しました。未申請の方はこども保育支援課へ相談してください。','/guide/parenting/'),
('休日の午後に歯科を受診できますか？','小笠掛川急患診療所の歯科は休日の午前のみです。午後と平日夜間は歯科診療がありません。','/guide/urgent/'),
('ごみの日は市内で同じですか？','掛川区域と大東・大須賀区域のカレンダーを選び、さらに自分の地区の収集日を確認してください。','/guide/garbage/'),
('親の介護はどこに相談しますか？','親の住所を担当する地域包括支援センターへ。市内5窓口の担当地区・電話番号を掲載しています。','/guide/care/'),
('チェックした情報は送信されますか？','チェックの状態だけを利用中のブラウザー内に保存します。名前や病歴を入力する欄はなく、申請・予約の代わりにはなりません。','/guide/moving/')])+'</section>'
method='<section class="refresh-section editorial-note"><h2>情報の確認について</h2><p>2026年11月19日に、市の生活情報・観光案内などの公式ページを確認し、窓口時間、申請停止、受付終了、閉館などを反映しました。個別制度の条件は各ページの出典をご参照ください。既存の手続きページは項目ごとの確認日を残し、今回確認した変更点を追記しています。</p><p>市内すべての店舗・イベントの営業や受付をリアルタイムで保証するものではありません。</p></section>'
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
 block='<!-- CURRENT:START --><aside class="verified-update"><h2>2026年11月19日確認の変更・補足</h2><p>'+esc(note['text'])+'</p><p>'+link(note['source'],'公式案内で確認する')+' ／ '+link('/guide/'+note['guide']+'/','手順と準備をまとめて見る')+'</p></aside><!-- CURRENT:END -->'
 if '<!-- CURRENT:START -->' in s:s=re.sub(r'<!-- CURRENT:START -->.*?<!-- CURRENT:END -->',lambda _:block,s,flags=re.S)
 else:
  pos=s.find('</section>',s.find('<section class="hero"'))+len('</section>')
  if pos<len('</section>'):raise RuntimeError(str(f))
  s=s[:pos]+block+s[pos:]
 f.write_text(s,encoding='utf8')
print('Built',len(guides),'guides and home marked sections')
