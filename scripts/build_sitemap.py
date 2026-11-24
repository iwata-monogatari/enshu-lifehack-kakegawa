#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""topics_master.json + トップページ/利用規約からsitemap.xmlを生成する。
実行: python3 scripts/build_sitemap.py
"""
import json
from html import escape
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SITE = 'https://kakegawa.enshu-lifehack.com'

class PageImages(HTMLParser):
    """Collect same-origin editorial photos actually embedded on the page."""
    def __init__(self):
        super().__init__()
        self.urls = []

    def handle_starttag(self, tag, attrs):
        if tag != 'img':
            return
        src = dict(attrs).get('src', '')
        if src.startswith('/assets/discover-photos/'):
            self.urls.append(src)


def main():
    ledger = json.loads((ROOT / 'data/topics_master.json').read_text(encoding='utf-8'))
    guides = json.loads((ROOT / 'data/refresh-guides.json').read_text(encoding='utf-8'))
    articles = json.loads((ROOT / 'data/local-search-topics.json').read_text(encoding='utf-8'))
    urls = ['/', '/terms/'] + sorted({t['href'] for t in ledger + guides + articles})
    lines = ['<?xml version="1.0" encoding="UTF-8"?>',
             '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" '
             'xmlns:image="http://www.google.com/schemas/sitemap-image/1.1">']
    photos_by_page = {}
    for route in ['/', *(article['href'] for article in articles)]:
        parser = PageImages()
        parser.feed((ROOT / route.strip('/') / 'index.html').read_text(encoding='utf-8'))
        photos_by_page[route] = list(dict.fromkeys(parser.urls))
    for route in urls:
        loc = f'<url><loc>{escape(SITE + route)}</loc>'
        photos = photos_by_page.get(route, [])
        if not photos:
            lines.append(loc + '</url>')
            continue
        lines.append(loc)
        for photo in photos:
            if not (ROOT / photo.removeprefix('/')).is_file():
                raise FileNotFoundError(photo)
            lines.append(f'  <image:image><image:loc>{escape(SITE + photo)}</image:loc></image:image>')
        lines.append('</url>')
    lines.append('</urlset>')
    out = ROOT / 'sitemap.xml'
    out.write_text('\n'.join(lines) + '\n', encoding='utf-8')
    print(f'生成完了: {out}（{len(urls)}件）')

if __name__ == '__main__':
    main()
