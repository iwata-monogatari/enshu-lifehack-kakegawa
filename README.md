# enshu-lifehack-kakegawa

掛川ライフハック（遠州ライフハック 掛川版）の **静的サイト** リポジトリ。
公開先：`https://kakegawa.enshu-lifehack.com/`（Cloudflare Pages）

磐田版（`enshu-lifehack-iwata`）から手動クローン・履歴を切って新設。横展開の設計原則・置換保護リストは袋井版の指示書（`enshu-lifehack-fukuroi` リポジトリ `docs/fukuroi-lifehack-design-spec.md`）に準拠する。

## 構成

静的HTMLのみ。Cloudflare Pages の **Build output directory = `/`**（ビルド不要）で配信する。

```
index.html              トップ（暫定スケルトン。中項目公開後に本実装へ差し替え）
data/city.json          市プロファイル（市名・公式窓口・CVフラグ等の差分を集約）
data/topics_master.json 中項目マスター台帳（磐田155項目が起点。掛川列は今後追加）
life/<大項目>/           くらしの大項目ページ（生成パイプラインで今後作成）
life/<大項目>/<中項目>/   個別ページ（同上）
sitemap.xml             サイトマップ（暫定）
robots.txt
_redirects              旧 /iwata/ 配下 → 直下への 301
404.html                カスタム404
favicon.svg
```

## 生成方法

本サイトは市公式サイトのクロール・静的化ではなく、`data/topics_master.json` の中項目台帳をもとに、市公式情報を1件ずつ調査した上でAIが執筆する「台帳駆動」の生成物である（袋井版と同じ方式）。台帳のstatusが `human-verified` 以上になった項目のみ `life/` 配下に生成・公開する。

## 現状（2026-07-03時点）

- リポジトリ作成・磐田剥がし（`life/` 全削除、市名・ドメイン置換、`data/city.json` 新設）まで完了
- 中項目の出典調査・台帳整備・ページ生成・Cloudflareカスタムドメイン接続は未着手

## 免責

本サイトは掛川市公式サイトではありません。最新・正確な情報は掛川市公式サイトをご確認ください。
運営：富士ヶ丘サービス ／ 代表：大石浩之
