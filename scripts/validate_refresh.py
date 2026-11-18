"""Check every public page, link targets, canonical, guide coverage and dated facts."""
import json,re,sys
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlsplit,unquote
R=Path(__file__).resolve().parent.parent
class Page(HTMLParser):
 def __init__(self,text):
  super().__init__();self.ids=[];self.refs=[];self.canonical=[];self.h1=0;self.feed(text)
 def handle_starttag(self,tag,attrs):
  d=dict(attrs)
  if 'id'in d:self.ids.append(d['id'])
  if tag=='h1':self.h1+=1
  if tag=='link' and d.get('rel')=='canonical':self.canonical.append(d.get('href'))
  for attr in ['href','src']:
   if attr in d:self.refs.append(d[attr])
ledger=json.loads((R/'data/topics_master.json').read_text(encoding='utf8'))
guides=json.loads((R/'data/refresh-guides.json').read_text(encoding='utf8'))
articles=json.loads((R/'data/local-search-topics.json').read_text(encoding='utf8'))
paths=['/','/terms/']+[x['href'] for x in ledger+guides+articles]
errors=[];pages={}
for path in paths:
 f=R/path.strip('/')/'index.html'
 if not f.exists():errors.append('missing '+path);continue
 text=f.read_text(encoding='utf8');page=Page(text);pages[path]=page
 if page.h1!=1:errors.append('h1 '+path)
 if page.canonical!=['https://kakegawa.enshu-lifehack.com'+path]:errors.append('canonical '+path)
 if len(page.ids)!=len(set(page.ids)):errors.append('duplicate ids '+path)
 if '\ufffd' in text:errors.append('encoding '+path)
for path,page in pages.items():
 for ref in page.refs:
  u=urlsplit(ref)
  if u.scheme or u.netloc:continue
  target=u.path or path
  if not target.startswith('/'):continue
  f=R/unquote(target).strip('/')
  if target.endswith('/'):f=f/'index.html'
  if not f.exists():errors.append(f'broken {path} -> {ref}')
  if u.fragment and target in pages and unquote(u.fragment) not in pages[target].ids:errors.append(f'fragment {path} -> {ref}')
idx=json.loads((R/'search-index.json').read_text(encoding='utf8'))
if {x['href'] for x in idx}!={x['href'] for x in ledger+guides+articles}:errors.append('search coverage')
home=(R/'index.html').read_text(encoding='utf8')
if home.count('<details class="category"')!=13:errors.append('13 categories')
for slug in ['water-start-stop-fees','water-sewer']:
 text=(R/'life/start-living'/slug/'index.html').read_text(encoding='utf8')
 for stale in ['インターネットなら24時間','インターネット（24時間）','インターネットの専用サイトから24時間']:
  if stale in text:errors.append('stale water '+slug)
print(json.dumps({'public_pages':len(pages),'search_entries':len(idx),'guides':len(guides),'errors':errors},ensure_ascii=False))
sys.exit(bool(errors))
