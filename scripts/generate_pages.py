#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
generate_pages.py — data/topics_master.json + data/city.json から中項目詳細ページを生成する。

現状の実装範囲（2026-07-03時点）:
  本スクリプトが機械的に組み立てるのは「事実ベースの骨組み」（見出し・リード文・
  公式窓口ボックス・出典リンク・関連リンク・CVブロック・フィードバック欄・フッター）
  のみである。磐田版で確立した「タイプ別タブ」「Q&A」「今日/今週/後日の行動ステップ」
  などの厚みのある本文は、項目ごとの個別執筆（AI執筆＋チャット側レビュー）が必要な
  工程であり、本スクリプトでは生成しない。まずは骨組みで公開可否の検証・出典リンクの
  健全性チェックを回せるようにし、本文の厚みは人手（Claude Code対話）で個別に拡充する
  二段階運用とする。

公開ゲート（2026-07-03改訂）:
  大石による人力目視チェック(human-verified)は個別ゲートとして設けない。
  status が ai-checked 以上（＝出典調査済み。値の裏取りができなかったfactsは
  「確認中」と表示する運用で安全側に倒す）の項目を life/ 配下に出力する。
  draft のみ _staging/（.assetsignore対象・非配信）に出力する。

実行:
  python3 scripts/generate_pages.py            # 全項目を再生成
  python3 scripts/generate_pages.py --category 親のこと
"""
import argparse
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
LEDGER = ROOT / "data" / "topics_master.json"
CITY = ROOT / "data" / "city.json"
LIFE_DIR = ROOT / "life"
STAGING_DIR = ROOT / "_staging"

PUBLISHABLE_STATUSES = ("ai-checked", "machine-verified", "human-verified", "published")

CATEGORY_ICON = {
    "困った・相談したい": "🧩", "暮らし始めた": "🧭", "働く・暮らす": "💴",
    "家族が増える": "👶", "健康・医療": "🏥", "もしもの時": "⚠️",
    "人生の終わり": "🕊️", "家・住まい": "🏠", "学ぶ・育つ": "🎒",
    "親のこと": "👵", "遊ぶ・使う・出かける": "🌳", "これから暮らす": "🏡",
    "新しい場所へ": "📦",
}


def esc(s):
    if s is None:
        return ""
    return str(s).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;")


def load():
    ledger = json.loads(LEDGER.read_text(encoding="utf-8"))
    city = json.loads(CITY.read_text(encoding="utf-8"))
    return ledger, city


def facts_html(facts):
    if not facts:
        return ""
    rows = []
    for k, v in facts.items():
        rows.append(f"<p class=\"mini\"><b>{esc(k)}</b>：{esc(v)}</p>")
    return "".join(rows)


def sources_html(sources, city_name):
    if not sources:
        return f"<p class=\"mini\">出典URL未確定（{esc(city_name)}公式サイトでの個別確認が必要）</p>"
    links = []
    for s in sources:
        links.append(
            f'<a class="official-link" href="{esc(s["url"])}" target="_blank" rel="noopener">'
            f'{esc(s["label"])} <span>{esc(city_name)}公式</span></a>'
        )
    return "".join(links)


def related_links_html(item, category_items):
    others = [i for i in category_items if i["href"] != item["href"]][:8]
    if not others:
        return ""
    links = []
    for o in others:
        title = o.get("title") or o.get("title_iwata") or o["href"]
        links.append(f'<a class="official-link" href="{esc(o["href"])}">{esc(title)}</a>')
    return "".join(links)


def cv_block_html(city):
    cv = city.get("cv", {})
    if not cv.get("kaigo_lead") and not cv.get("fudosan_link"):
        return ""
    cards = []
    if cv.get("kaigo_lead") or cv.get("fudosan_link"):
        cards.append(
            '<div class="company-card"><h3>介護・住まいの相談</h3>'
            f'<p>{esc(city["city_name"])}で、介護施設さがしや高齢の親の住まいについての相談をお受けしています。</p>'
            '<a class="official-link" href="https://www.fujigaoka-service.co.jp/" target="_blank" rel="noopener" style="margin-top:8px">相談先を見る <span>富士ヶ丘サービス</span></a></div>'
        )
    if not cards:
        return ""
    return (
        '<div class="company-strip"><h2 class="sec" style="margin-top:0">迷ったときの相談先</h2>'
        f'<div class="company-grid">{"".join(cards)}</div></div>'
    )


def render_page(item, city, category_items):
    title = item.get("title") or item.get("title_iwata") or item["href"]
    city_name = city["city_name"]
    site_name = city["site_name"]
    category = item["category"]
    icon = CATEGORY_ICON.get(category, "")
    status = item.get("status", "draft")
    verified = status in PUBLISHABLE_STATUSES
    verified_date = item.get("verified_date") or item.get("ai_checked_date") or "確認中"

    facts = item.get("facts") or {}
    window = facts.get("window")
    if window:
        lead = f"{esc(city_name)}で「{esc(title)}」について確認するときの窓口は{esc(window)}です。詳細は下記の公式ページで確認してください。"
    else:
        lead = f"{esc(city_name)}の{esc(category)}に関する「{esc(title)}」について、公式ページの情報を整理しています。"

    html = f"""<!doctype html><html lang="ja"><head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{esc(title)} | {esc(site_name)}</title>
<meta name="description" content="{esc(city_name)}の{esc(category)}に関する情報を整理する非公式ナビです。最新・正確な情報は必ず{esc(city_name)}公式ページで確認してください。">
<link rel="icon" href="/favicon.svg" type="image/svg+xml">
<!-- PART:head-css:START --><link rel="stylesheet" href="/assets/site.css?v=20260702"><!-- PART:head-css:END --></head><body>
<!-- PART:header:START --><header class="site"><div class="wrap"><a class="logo" href="/">{esc(site_name)}</a></div></header><!-- PART:header:END -->
<!-- PART:disclaimer:START --><div class="disclaimer"><div class="wrap">{esc(site_name)}は{esc(city_name)}公式サイトではありません。最新・正確な情報は必ず公式ページで確認してください。</div></div><!-- PART:disclaimer:END -->
<main><div class="wrap">
<p class="breadcrumb"><a href="/">{esc(site_name)}</a> ／ <a href="{esc(item['href'].rsplit('/', 2)[0])}/">{esc(icon)} {esc(category)}</a> ／ {esc(title)}</p>
<section class="hero"><div class="hero-visual"><h1>{esc(title)}</h1></div><div class="hero-body"><p class="lead">{lead}</p></div></section>
<h2 class="sec">公式窓口・確認先</h2><div class="official">{facts_html(item.get('facts'))}{sources_html(item.get('sources_kakegawa'), city_name)}</div>
<h2 class="sec">あわせて確認したい{esc(category)}のリンク</h2><div class="official">{related_links_html(item, category_items)}</div>
{cv_block_html(city)}
<section class="feedback-box" id="feedback"><h2 class="sec" style="margin-top:0">これで解決しそうですか？</h2><p class="mini" style="margin:0 0 10px">いただいた反応は、ページ改善のためだけに使います。お名前や連絡先は取得しません。</p><div class="fb-actions"><button type="button" class="fb-btn" data-feedback="solved">解決しそう</button><button type="button" class="fb-btn" data-feedback="still_worried">まだ不安</button><button type="button" class="fb-btn" data-feedback="could_not_find">探している情報がなかった</button></div><p class="fb-thanks">ありがとうございました。いただいた声は今後のページ改善に役立てます。</p></section>
<p class="verified">最終確認日：{esc(verified_date)} ／ 本ページは公式情報を整理したものです。最新・正確な情報は必ず{esc(city_name)}公式ページで確認してください。</p>
</div></main><!-- PART:footer:START --><!-- PART:footer:END -->
</body></html>
"""
    return html, verified


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--category")
    args = ap.parse_args()

    ledger, city = load()
    items = [i for i in ledger if not args.category or i["category"] == args.category]

    by_category = {}
    for i in ledger:
        by_category.setdefault(i["category"], []).append(i)

    n_staged = n_published = 0
    for item in items:
        html, verified = render_page(item, city, by_category[item["category"]])
        rel = item["href"].strip("/")  # 例: life/education/after-school-club
        out_base = ROOT if verified else STAGING_DIR
        out_path = out_base / rel / "index.html"
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(html, encoding="utf-8", newline="\n")
        if verified:
            n_published += 1
        else:
            n_staged += 1

    print(f"生成完了: life/ へ {n_published}件・_staging/ へ {n_staged}件")
    if n_published == 0:
        print("注意: human-verified以上の項目が0件のため、life/ には何も出力されていません。")


if __name__ == "__main__":
    main()
