import re,sys
sys.argv=['x','/home/user/OBJEKT']
src=open('/home/user/OBJEKT/plan/faux-books/artwork/make_flats.py').read().split("files = [single(v) for v in VOLS]")[0]
exec(src)
import json
meta=[]
for v in VOLS:
    body,Wf,H,_=build(v)
    body=re.sub(r'<line [^>]*/>','',body)
    svg=f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {Wf} {H}" width="{Wf*5}" height="{H*5}">{body}</svg>'
    open(f'tex/tex_{v[0]:02d}.svg','w').write(svg)
    W,Hh=SZ[v[4]]
    meta.append(dict(n=v[0],title=' '.join(v[1]),W=W/10,H=Hh/10,D=4.5,cover=C[v[2]],px=[Wf*5,H*5],Wmm=W,Dmm=D))
json.dump(meta,open('meta.json','w'))
