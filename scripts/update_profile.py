"""Refresh public GitHub profile visuals. Standard library only; retain old files on fetch failure."""
import os, re, json, html, urllib.request, urllib.parse, time
from pathlib import Path
from datetime import datetime, timezone, date
from html.parser import HTMLParser

ROOT = Path(__file__).resolve().parents[1]
USER = 'tiendat2712'
ASSETS = ROOT / 'assets'
COLORS = ['#142434', '#155e75', '#0891b2', '#22d3ee', '#a5f3fc']

def get(url):
    headers = {'User-Agent': 'tiendat2712-profile', 'Accept': 'application/vnd.github+json' if 'api.github.com' in url else 'text/html'}
    if 'api.github.com' in url and os.environ.get('GITHUB_TOKEN'):
        headers['Authorization'] = 'Bearer ' + os.environ['GITHUB_TOKEN']
    for attempt in range(3):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers=headers), timeout=30) as r:
                return r.read().decode('utf-8')
        except Exception:
            if attempt == 2: raise
            time.sleep(1)

def api(url): return json.loads(get(url))
def esc(s): return html.escape(str(s), quote=True)
def txt(x,y,s,size=14,color='#cbd5e1',weight=400):
    return f'<text x="{x}" y="{y}" fill="{color}" font-size="{size}" font-weight="{weight}" font-family="Segoe UI,Arial,sans-serif">{esc(s)}</text>'
def svg(w,h,title,body):
    return f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" role="img"><title>{esc(title)}</title><rect width="{w}" height="{h}" rx="16" fill="#0b1120"/>{body}</svg>'

class Calendar(HTMLParser):
    def __init__(self): super().__init__(); self.days = {}
    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if 'data-date' in a and 'data-level' in a:
            self.days[a['data-date']] = int(a['data-level'])

def fetch():
    source = get(f'https://github.com/users/{USER}/contributions')
    cal = Calendar(); cal.feed(source)
    match = re.search(r'([\d,]+)\s+contributions\s+in the last year', source)
    if len(cal.days) < 300 or not match: raise ValueError('Unexpected contribution calendar format')
    repos = []
    for page in range(1, 100):
        batch = api(f'https://api.github.com/users/{USER}/repos?per_page=100&type=owner&page={page}')
        repos.extend(r for r in batch if not r['fork'])
        if len(batch) < 100: break
    langs, commits = {}, []
    for r in repos:
        for lang, count in api(r['languages_url']).items(): langs[lang] = langs.get(lang,0) + count
        if r['size'] == 0: continue
        for c in api(f"https://api.github.com/repos/{r['full_name']}/commits?author={USER}&per_page=5"):
            commits.append({'repo':r['name'],'sha':c['sha'],'url':c['html_url'], 'date':c['commit']['committer']['date'], 'message':c['commit']['message'].splitlines()[0]})
    commits.sort(key=lambda c:c['date'], reverse=True)
    return {'updated':datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC'),'days':sorted(cal.days.items()),'contributions':int(match[1].replace(',','')),'repos':len(repos),'stars':sum(r['stargazers_count'] for r in repos),'languages':langs,'commits':commits[:6]}

def render(d):
    ASSETS.mkdir(exist_ok=True)
    days=d['days']; active=sum(level>0 for _,level in days)
    body=txt(24,32,'GitHub at a glance',21,'#f8fafc',650)
    for x,y,value,label in [(24,86,d['contributions'],'Contributions / calendar'),(228,86,active,'Active days'),(24,165,d['repos'],'Public non-fork repos'),(228,165,d['stars'],'Stars / those repos')]:
        body+=txt(x,y,value,32,'#67e8f9',700)+txt(x,y+24,label,12)
    body+=txt(24,273,d['updated'],11,'#94a3b8')
    (ASSETS/'profile-stats.svg').write_text(svg(430,295,'GitHub statistics for '+USER,body),encoding='utf-8')
    sorted_langs=sorted(d['languages'].items(),key=lambda x:x[1],reverse=True)
    total=sum(d['languages'].values())
    entries=sorted_langs[:7]
    if len(sorted_langs)>7: entries.append(('Other',sum(v for _,v in sorted_langs[7:])))
    body=txt(24,32,'Languages in my public code',20,'#f8fafc',650)
    palette=['#60a5fa','#facc15','#c084fc','#fb923c','#2dd4bf','#e4cc98','#f59e0b','#94a3b8']
    for i,(name,n) in enumerate(entries):
        pct=n/total*100 if total else 0; y=61+i*25
        body+=txt(24,y,name,12)+txt(343,y,f'{pct:.1f}%',12)
        body+=f'<rect x="135" y="{y-9}" width="190" height="7" rx="3" fill="#1e293b"/><rect x="135" y="{y-9}" width="{190*pct/100:.2f}" height="7" rx="3" fill="{palette[i]}"/>'
    if not total: body+=txt(24,90,'No language data available.',14)
    body+=txt(24,273,'By code bytes; excludes forks. Not proficiency.',11,'#94a3b8')
    (ASSETS/'language-stats.svg').write_text(svg(430,295,'Public repository languages by code bytes',body),encoding='utf-8')
    # Calendar colors are observed GitHub levels. The moving trail is decorative.
    start=date.fromisoformat(days[0][0]); body=txt(24,32,'Contribution trail',22,'#f8fafc',650)
    body+=txt(24,56,f"{d['contributions']} contributions · {days[0][0]} — {days[-1][0]}",13)
    coords=[]
    for ds,level in days:
        delta=(date.fromisoformat(ds)-start).days; col,row=divmod(delta,7); x=24+col*16; y=78+row*16
        body+=f'<rect x="{x}" y="{y}" width="12" height="12" rx="3" fill="{COLORS[level]}"><title>{ds}: GitHub activity level {level}/4</title></rect>'
        coords.append((col,row,x+6,y+6))
    coords.sort(key=lambda p:(p[0],p[1] if p[0]%2==0 else -p[1]))
    motion='M '+' L '.join(f'{x-30},{y-84}' for _,_,x,y in coords)
    for i in range(5):
        body+=f'<circle cx="30" cy="84" r="{4.5-i*.5}" fill="#facc15" opacity="{1-i*.15}"><animateMotion dur="32s" begin="-{i*.12}s" repeatCount="indefinite" path="{motion}"/></circle>'
    body+=txt(24,220,'GitHub contribution levels · animated trail is decorative',12,'#94a3b8')+txt(24,244,'Updated '+d['updated'],11,'#94a3b8')
    (ASSETS/'contribution-trail.svg').write_text(svg(900,267,'Actual GitHub contribution calendar with decorative animated trail',body),encoding='utf-8')
    body=txt(24,32,'A year in contributions',22,'#f8fafc',650)
    # Isometric bars: height encodes the observed 0–4 activity level, not exact counts.
    for ds,level in days:
        delta=(date.fromisoformat(ds)-start).days; col,row=divmod(delta,7)
        x=105+col*13-row*11; y=80+col*1.5+row*9; h=3+level*10
        body+=f'<g><title>{ds}: level {level}/4</title><path d="M{x},{y-h}l11,1.5 -9,7 -11,-1.5Z" fill="{COLORS[level]}"/><path d="M{x-9},{y-h+7}l11,1.5v{h}l-11,-1.5Z" fill="{COLORS[level]}" opacity=".75"/><path d="M{x+2},{y-h+8.5}l9,-7v{h}l-9,7Z" fill="{COLORS[level]}" opacity=".45"/></g>'
    body+=txt(24,265,'Height = GitHub activity level (0–4), not exact commit count.',12,'#94a3b8')+txt(24,288,d['updated'],11,'#94a3b8')
    (ASSETS/'contributions-3d.svg').write_text(svg(900,312,'Isometric contribution calendar for '+USER,body),encoding='utf-8')
    readme=ROOT/'README.md'; content=readme.read_text(encoding='utf-8')
    rows=[]
    for c in d['commits']:
        message=html.escape(c['message'][:100]).replace('[','&#91;').replace(']','&#93;').replace('`','&#96;').replace('*','&#42;').replace('_','&#95;')
        rows.append(f"- **{c['date'][:10]}** · [{c['repo']}](https://github.com/{USER}/{c['repo']}) · [{c['sha'][:7]}]({c['url']}) — {message}")
    section='\n'+('\n'.join(rows) or 'No matching public commits found.')+'\n\n<sub>Updated '+d['updated']+'. Latest authored commits sampled from the default branches of owned public non-fork repositories.</sub>\n'
    if '<!-- ACTIVITY:START -->' not in content: raise ValueError('README activity markers missing')
    content=re.sub(r'(?<=<!-- ACTIVITY:START -->).*?(?=<!-- ACTIVITY:END -->)',lambda _:section,content,flags=re.S)
    readme.write_text(content,encoding='utf-8')
    (ASSETS/'github-profile-data.json').write_text(json.dumps(d,ensure_ascii=False,indent=2),encoding='utf-8')

if __name__=='__main__':
    # Fetch everything before writing; failed fetches leave the prior snapshot untouched.
    data=fetch(); render(data)
    print(f"Updated {data['repos']} repositories, {len(data['days'])} calendar days, {len(data['commits'])} commits.")
