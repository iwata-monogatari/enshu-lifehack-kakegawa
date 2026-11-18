"""Render the local article collection into static pages and reusable lists."""
import html
import json
import re
from collections import defaultdict
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SITE = 'https://kakegawa.enshu-lifehack.com'
GROUP_ICONS = {
    '歴史・まち歩き': '🏯', '自然・公園': '🌿', '文化・美術': '🎨',
    '体験・温泉': '♨️', '食・特産品': '🍵', '閉館・過去資料': '📚',
}
FOOD_VISITS = {'seatopia', 'akazukin-farm'}


def read_data(name):
    return json.loads((ROOT / 'data' / name).read_text(encoding='utf8'))


def link(url, label):
    return f'<a href="{html.escape(url, quote=True)}">{html.escape(label)}</a>'


def part(name):
    return f'<!-- PART:{name}:START --><!-- PART:{name}:END -->'


def load_articles():
    config = read_data('local-article-sources.json')
    records = {item['slug']: item for item in read_data('place-directory.json')}
    for slug, (name, group, url) in config['extra_entries'].items():
        if slug in records:
            raise ValueError(f'Duplicate directory entry: {slug}')
        records[slug] = {'slug': slug, 'name': name, 'group': group, 'url': url}

    articles = {}
    for line in (ROOT / 'data/local-articles.txt').read_text(encoding='utf8').splitlines():
        if not line or line.startswith('#'):
            continue
        slug, theme, title, lead, background, practical = line.split('|')
        if slug in articles or not re.fullmatch(r'[a-z0-9][a-z0-9_-]*', slug):
            raise ValueError(f'Invalid or duplicate article slug: {slug}')
        article = dict(records[slug])
        sources = [(('掛川市の公式案内' if 'city.kakegawa.shizuoka.jp' in article['url'] else '施設・運営団体の公式案内'), article['url'])]
        for key in config['supplementary'].get(slug, []):
            label, url = config['source_sets'][key]
            if url not in {u for _, u in sources}:
                sources.append((label, url))
        note = config['visit_notes'].get(slug)
        if note:
            note = (note[0], *config['source_sets'][note[1]])
        article.update(theme=theme, title=title, lead=lead, background=background, practical=practical,
                       href=f'/discover/{slug}/', sources=sources, note=note, checked=config['checked'],
                       status='閉館済み' if article.get('closed') else config['status'].get(slug),
                       aliases=config['aliases'].get(slug, []))
        articles[slug] = article
    if set(articles) != set(records):
        raise ValueError(f'Missing article drafts: {set(records) - set(articles)}')
    return articles


def select_articles(articles, section):
    if section == 'food':
        return [a for a in articles.values() if a['group'] == '食・特産品' or a['slug'] in FOOD_VISITS]
    if section == 'history':
        return [a for a in articles.values() if a['group'] in {'歴史・まち歩き', '文化・美術', '閉館・過去資料'}]
    return list(articles.values())


def article_list(articles, section):
    entries = select_articles(articles, section)
    groups = [g for g in GROUP_ICONS if any(a['group'] == g for a in entries)]
    options = ''.join(f'<option>{html.escape(g)}</option>' for g in groups)
    html_cards = []
    for article in entries:
        name = html.escape(' '.join([article['name'], article['title'], *article['aliases']]), quote=True)
        address = article.get('address')
        status = article['status']
        body = [f'<article class="place-card local-card" data-name="{name}" data-group="{html.escape(article["group"])}">',
                f'<p class="local-kind">{html.escape(article["group"])}</p>',
                f'<h3>{link(article["href"], article["title"])}</h3>',
                f'<p class="local-description">{html.escape(article["lead"])}</p>']
        if status:
            body.append(f'<p class="local-status">{html.escape(status)}</p>')
        if address and not article.get('closed'):
            body.append(f'<p>{html.escape(address)}</p>')
        html_cards.append(''.join(body) + '</article>')
    example = {'history': '例：高天神、日坂、古墳', 'food': '例：深蒸し茶、いちご、葛布'}.get(section, '例：掛川城、温泉、深蒸し茶')
    return f'''<div class="directory-controls" hidden>
      <div><label for="place-query">名前・キーワード</label><input type="search" id="place-query" placeholder="{example}"></div>
      <div><label for="place-group">分野</label><select id="place-group"><option value="">すべて</option>{options}</select></div>
    </div><p id="place-count" aria-live="polite">{len(entries)}件の記事</p>
    <div class="place-grid local-grid">{''.join(html_cards)}</div>'''


def sections(heading, content, section_id=''):
    attrs = f' id="{section_id}"' if section_id else ''
    return f'<section class="guide-section"{attrs}><h2>{html.escape(heading)}</h2>{content}</section>'


def paragraph(text):
    return f'<p>{html.escape(text)}</p>'


def wrap_page(title, lead, href, breadcrumb, content, scripts=''):
    return f'''<!doctype html>
<html lang="ja"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{html.escape(title)} | 掛川ライフハック</title>
<meta name="description" content="{html.escape(lead, quote=True)}">
<link rel="canonical" href="{SITE}{href}"><link rel="icon" href="/favicon.svg" type="image/svg+xml">
{part('head-css')}<link rel="stylesheet" href="/assets/local-articles.css?v=1">
</head><body class="hub guide-page local-page">
{part('header')}
<main class="wrap"><nav class="breadcrumb" aria-label="現在の位置">{breadcrumb}</nav>
{content}</main>{scripts}
{part('footer')}
</body></html>
'''


def write_page(href, content):
    path = ROOT / href.strip('/') / 'index.html'
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding='utf8')


def build_local_articles(articles):
    by_theme = defaultdict(list)
    for article in articles.values():
        by_theme[article['theme']].append(article)

    search = []
    for article in articles.values():
        title, lead, href = (article[k] for k in ('title', 'lead', 'href'))
        group = article['group']
        home = link('/', 'ホーム')
        food = group == '食・特産品'
        historical = group in {'歴史・まち歩き', '文化・美術', '閉館・過去資料'}
        if food:
            listing = link('/guide/food/#local-articles', 'お茶・特産品の記事一覧')
        elif historical:
            listing = link('/guide/history/#local-articles', '歴史・文化の記事一覧')
        else:
            listing = link('/guide/visit/#local-articles', 'お出かけの記事一覧')
        checked = date.fromisoformat(article['checked'])
        checked_label = f'{checked.year}年{checked.month}月{checked.day}日'
        header = f'''<header class="guide-hero local-hero"><p class="local-kind"><span aria-hidden="true">{GROUP_ICONS[group]}</span> {html.escape(group)}</p>
<h1>{html.escape(title)}</h1><p class="lead">{html.escape(lead)}</p>
<p class="date-line">公式情報確認 <time datetime="{article['checked']}">{checked_label}</time></p></header>'''
        status = f'<p class="local-status">{html.escape(article["status"])}</p>' if article['status'] else ''
        if article['note']:
            note, source_label, source_url = article['note']
            status += f'<aside class="local-notice" aria-label="確認できた利用情報">{paragraph(note)}{link(source_url, source_label)}</aside>'
        location = ''
        if article.get('address') and not article.get('closed'):
            location = f'<dl class="local-location"><dt>所在地</dt><dd>{html.escape(article["address"])}</dd></dl>'
        body = sections('背景と見どころ', paragraph(article['background']))
        practical_title = '閉館後に確認できる資料' if article.get('closed') else '選び方と確認先' if food else '訪ねる前の確認'
        body += sections(practical_title, paragraph(article['practical']) + location)
        sources = ''.join(f'<li>{link(url, label)}</li>' for label, url in article['sources'])
        body += sections('公式情報・出典', f'<ul>{sources}</ul>')

        related = [a for a in by_theme[article['theme']] if a is not article]
        if article['slug'] in {'kakegawajyo', 'kakegawajyogoten'}:
            related.insert(0, articles['kakegawa-three-castles'])
        if article['slug'] == 'kakegawa-three-castles':
            related.insert(0, articles['kakegawajyo'])
        if len(related) < 2:
            related.extend(a for a in articles.values() if a is not article and a not in related and a['group'] == group)
        related_list = ''.join(f'<li>{link(a["href"], a["title"])}</li>' for a in related[:4])
        body += sections('あわせて読む', f'<ul>{related_list}</ul><p>{listing}</p>')
        write_page(href, wrap_page(title, lead, href, f'{home} / {listing}', header + status + body))
        search.append(dict(href=href, title=title, category=group, icon=GROUP_ICONS[group],
                           synonyms=[article['name'], *article['aliases']]))

    history_title = '掛川の歴史・文化の記事一覧｜三城・東海道・寺社・美術館'
    history_lead = '掛川三城、日坂宿と旧東海道、横須賀の町並み、寺社・古墳・美術館を、解説記事からたどれます。'
    history_url = '/guide/history/'
    history_cards = [('三つの城を比べる', 'kakegawa-three-castles'), ('旧東海道の峠を知る', 'sayononakayama'), ('横須賀の町を歩く', 'mikumanojinjya'), ('掛川の古代を知る', 'wadaokakofun')]
    highlights = ''.join(f'<li>{link(articles[slug]["href"], label)}<span>{html.escape(articles[slug]["lead"])}</span></li>' for label, slug in history_cards)
    body = f'<header class="guide-hero local-hero"><h1>{history_title}</h1><p class="lead">{history_lead}</p></header>'
    body += sections('テーマから読む', f'<ul class="local-highlights">{highlights}</ul>')
    body += sections('歴史・文化の記事一覧', article_list(articles, 'history'), 'local-articles')
    body += f'<p>{link("/guide/visit/#local-articles", "すべてのお出かけ記事")} ／ {link("/guide/food/#local-articles", "お茶・特産品の記事")}</p>'
    write_page(history_url, wrap_page(history_title, history_lead, history_url, link('/', 'ホーム'), body, '<script src="/assets/guide-tools.js?v=2" defer></script>'))
    search.append(dict(href=history_url, title=history_title, category='歴史・まち歩き', icon='🏯', synonyms=['史跡', '歴史', '文化', '東海道', '掛川三城']))
    (ROOT / 'data/local-search-topics.json').write_text(json.dumps(search, ensure_ascii=False, indent=2) + '\n', encoding='utf8')


def update_guide_body(guide, articles):
    section = guide['href'].strip('/').split('/')[-1]
    if section not in {'visit', 'food'}:
        return guide['body']
    body = guide['body']
    destination_links = {a['url']: a for a in articles.values() if not a.get('closed')}
    if section == 'visit':
        introduction = ('<p>掛川城や旧東海道、自然・温泉、特産品の背景や見どころを、項目ごとの記事で読めます。'
                        '各記事から市や運営者の公式情報を確認できます。</p>')
        introduction += f'<p>{link("/guide/history/", "歴史・文化の記事一覧")}</p>'
        listing = sections('観光・歴史・特産品の記事一覧', introduction + article_list(articles, 'visit'), 'local-articles')
        body, count = re.subn(r'<section class="guide-section"><h2>場所を絞り込んで探す</h2>.*?</section>', lambda _: listing, body, flags=re.S)
        body = body.replace('掛川花鳥園、加茂荘花鳥園、キウイフルーツカントリーJAPAN、森林果樹公園などは、体験の内容と季節を確認して選びます。',
                            '掛川花鳥園、キウイフルーツカントリーJapan、森林果樹公園などは、体験の内容と季節を確認して選びます。加茂荘花鳥園は観光協会の11月16日更新情報では長期休園中です。')
    else:
        introduction = f'<p>{link(articles["kakegawacha"]["href"], "掛川茶と深蒸し煎茶を知る")} ／ {link(articles["chagusaba"]["href"], "世界農業遺産・茶草場農法を知る")}</p>'
        listing = sections('お茶・特産品の記事一覧', introduction + article_list(articles, 'food'), 'local-articles')
        body, count = re.subn(r'<div class="place-grid">.*?</div>', lambda _: '</section>' + listing + '<section class="guide-section local-empty" hidden>', body, flags=re.S)
        body = body.replace('<section class="guide-section local-empty" hidden></section>', '')
    if count != 1:
        raise ValueError(f'Expected one directory in {guide["href"]}; found {count}')

    def use_article(match):
        url, label = html.unescape(match[1]), match[2]
        if url in destination_links:
            return f'<a href="{destination_links[url]["href"]}">{label}</a>'
        return match[0]

    body = re.sub(r'<a href="(https?://[^\"]+)">([^<]+)</a>', use_article, body)
    return f'<p class="local-jump">{link("#local-articles", "詳しい記事を一覧から探す ↓")}</p>' + body
