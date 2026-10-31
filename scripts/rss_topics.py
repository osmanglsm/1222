from pathlib import Path
import json, urllib.request, xml.etree.ElementTree as ET
feeds = ['https://www.sciencedaily.com/rss/top/science.xml','https://www.nasa.gov/feed/']
items=[]
for feed in feeds:
    try:
        req=urllib.request.Request(feed,headers={'User-Agent':'Mozilla/5.0'})
        with urllib.request.urlopen(req,timeout=15) as response:
            root=ET.fromstring(response.read())
        for item in root.findall('.//item')[:8]:
            title=item.findtext('title') or ''
            link=item.findtext('link') or ''
            if title and link:items.append({'title':title,'url':link,'verified':False})
    except Exception as exc:print('RSS erişim hatası:',feed,exc)
out=Path('output');out.mkdir(exist_ok=True)
(out/'topics_for_review.json').write_text(json.dumps(items,ensure_ascii=False,indent=2),encoding='utf8')
print('İncelenecek konu sayısı:',len(items))
