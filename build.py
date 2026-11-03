#!/usr/bin/env python3
"""Builds data/ for Puente de Letras from palabras.txt + es_50k.txt.
Usage: python build.py [season_start YYYY-MM-DD]   (re-run any time to regenerate pair files)"""
import re,json,sys,os,unicodedata,collections
MIN_COMMON=25     # pair needs this many words found in the 50k frequency list
MAX_TOTAL=10**9   # optional cap on pair size
GOAL=30
BLOCK=set("puta puto putas putos mierda coño joder cabron cabrona pendejo pendeja verga marica maricon mamon chingar zorra".split())
def N(s):
    s=unicodedata.normalize('NFD',s.replace('ñ','#'))
    return ''.join(c for c in s if unicodedata.category(c)!='Mn').replace('#','ñ')
ok=lambda w:len(w)>=4 and re.fullmatch(r'[a-zñ]+',w)
words={N(l.strip()) for l in open('palabras.txt',encoding='utf-8')}
rank={};cnt={}
for l in open('es_50k.txt',encoding='utf-8'):
    a,b=l.split();n=N(a)
    if ok(n) and n not in rank: rank[n]=len(rank);cnt[n]=int(b)
CL=re.compile(r'^[a-zñ]*(ar|er|ir)(me|te|se|lo|la|le|nos|los|las|les)$')
add={w for w in rank if w not in words and cnt[w]>=100 and CL.match(w)}
print('clitic verb forms added:',len(add),sorted(add,key=lambda w:rank[w])[:12])
allw={w for w in words|add if ok(w) and w not in BLOCK and w.rstrip('s') not in BLOCK}
band=lambda w:'c' if rank.get(w,10**9)<10000 else 'm' if w in rank else 'r'
fn=lambda k:k.lower().replace('ñ','0')
pairs=collections.defaultdict(list)
for w in allw: pairs[w[0].upper()+'-'+w[-1].upper()].append(w)
elig=[]
for k,ws in pairs.items():
    com=sum(band(w)!='r' for w in ws)
    if k[2]!='S' and com>=MIN_COMMON and len(ws)<=MAX_TOTAL: elig.append((com,k))
elig.sort(reverse=True);elig=elig[:len(elig)//3*3]   # multiple of 3 -> a day's 3 pairs never span two cycles
keep=sorted(k for _,k in elig)
os.makedirs('data',exist_ok=True)
for f in os.listdir('data'): os.remove('data/'+f)
size=0
for k in keep:
    g={'c':[],'m':[],'r':[]}
    for w in sorted(pairs[k]): g[band(w)].append(w)
    s=json.dumps({'k':k,**{b:' '.join(v) for b,v in g.items()}},ensure_ascii=False,separators=(',',':'))
    open(f'data/{fn(k)}.json','w',encoding='utf-8').write(s);size+=len(s.encode())
start=sys.argv[1] if len(sys.argv)>1 else '2026-11-04'
if os.path.exists('seasons.json'): seasons=json.load(open('seasons.json'))
else: seasons=[{'start':start,'pairs':keep}];json.dump(seasons,open('seasons.json','w'))
json.dump({'goal':GOAL,'seasons':seasons},open('data/manifest.json','w'))
print('allowed words:',len(allw),'| eligible pairs:',len(keep),'| data size KB:',size//1024,'| largest file KB:',max(os.path.getsize('data/'+f) for f in os.listdir('data'))//1024)
print('days before any repeat:',len(keep)//3)
print('sample pairs:',keep[:20])
