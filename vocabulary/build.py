#!/usr/bin/env python3
"""Builds data/ for Puente de Letras from palabras.txt + es_50k.txt.
Usage: python build.py [season_start YYYY-MM-DD]   (re-run any time to regenerate pair files)"""
import re,json,sys,os,unicodedata,collections
MIN_COMMON=25     # pair needs this many words found in the 50k frequency list
MAX_TOTAL=10**9   # optional cap on pair size
GOAL=30            # fallback
GMIN,GMAX,GW=20,72,5   # goal = (words a native should find) x (avg points per word); words = GW*log10(effective pool size)
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
def _load(f):
    return {l.split()[0] for l in open(f,encoding='utf-8') if l.strip() and not l.startswith('#')} if os.path.exists(f) else set()
def _loadw(f):
    out=set()
    if os.path.exists(f):
        for l in open(f,encoding='utf-8'):
            if not l.startswith('#'): out|=set(l.split())
    return out
EXC=_load('excluir.txt')|_load('excluir_cat.txt')|_load('mixtas_cat.txt')   # demonyms etc. (mixtas banned unless in permitir.txt)
def _forms(p):                                       # an allowed word also allows its plural / feminine forms
    s={p,p+'s',p+'es'}
    if p[-1] in 'oa': s|={p[:-1]+x for x in ('a','o','as','os')}
    return s
def _expand(b):
    s={b,b+'s',b+'es',b+'a',b+'as'}
    if b[-1]=='o': s|={b[:-1]+x for x in ('a','as','os')}
    return s
for b in _loadw('excluir_extra.txt'):
    EXC|=_expand(unicodedata.normalize('NFD',b.replace('ñ','#')).encode('ascii','ignore').decode().replace('#','ñ'))
PERM=set()
for p in _loadw('permitir.txt'): PERM|=_forms(p)
EXC-=PERM                                            # ordinary words wrongly flagged
print('excluded as proper noun/demonym:',len(EXC))
allw={w for w in words|add if ok(w) and w not in BLOCK and w.rstrip('s') not in BLOCK and w not in EXC}
# --- rarity: judged by the word's FAMILY (base word + all its inflected forms), not by the exact form typed ---
lem={}
if os.path.exists('lemas.txt'):
    for l in open('lemas.txt',encoding='utf-8'):
        a=l.split()
        if len(a)==2: lem[a[0]]=a[1]
def root(w):
    for _ in range(4):
        if w in lem and lem[w]!=w: w=lem[w]
        else: break
    return w
fam=collections.Counter()
for w,c in cnt.items(): fam[root(w)]+=c
RARE_BELOW=1       # a word is rare (2x points) when its family has no word in the 50k frequency list
def famscore(w):
    sc=fam.get(root(w),0)
    if w.endswith('mente') and len(w)>7:        # adverbs in -mente follow their adjective (fabulosamente -> fabuloso)
        b=w[:-5]
        for c in {b,b[:-1]+'o' if b.endswith('a') else b}: sc=max(sc,fam.get(root(c),0))
    return sc
rare=lambda w:famscore(w)<RARE_BELOW
print('lemma links loaded:',len(lem))
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
    u=[w for w in g['r'] if not rare(w)]     # long-tail words from a common family: valid, but NOT double points
    s=json.dumps({'k':k,**{b:' '.join(v) for b,v in g.items()},'u':' '.join(u)},ensure_ascii=False,separators=(',',':'))
    open(f'data/{fn(k)}.json','w',encoding='utf-8').write(s);size+=len(s.encode())
import math
def goal(ws):
    c=[w for w in ws if band(w)=='c'];m=[w for w in ws if band(w)=='m'];r=len(ws)-len(c)-len(m)
    cm=c+m;avg=sum(len(w)-3 for w in cm)/len(cm)
    pool=len(c)+0.5*len(m)+0.05*r          # common words count fully, known words half, long-tail words a little
    return max(GMIN,min(GMAX,4*round(GW*math.log10(pool)*avg/4)))
GOALS={k:goal(pairs[k]) for k in keep}
start=sys.argv[1] if len(sys.argv)>1 else '2026-11-04'
if os.path.exists('seasons.json'): seasons=json.load(open('seasons.json'))
else: seasons=[{'start':start,'pairs':keep}];json.dump(seasons,open('seasons.json','w'))
json.dump({'goal':GOAL,'goals':GOALS,'seasons':seasons},open('data/manifest.json','w'))
print('allowed words:',len(allw),'| eligible pairs:',len(keep),'| data size KB:',size//1024,'| largest file KB:',max(os.path.getsize('data/'+f) for f in os.listdir('data'))//1024)
print('days before any repeat:',len(keep)//3)
print('goals:',{k:GOALS[k] for k in ['S-A','T-O','J-O','C-I','C-A','V-R'] if k in GOALS})
